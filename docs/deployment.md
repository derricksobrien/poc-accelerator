# Deployment Guide

## Deployment Options Overview

The POC Accelerator is deployable across 5 different environments, from local development to production cloud infrastructure.

| Environment | Best For | Difficulty | Time |
|------------|---------|-----------|------|
| Local Development | Testing & Development | Very Easy | 5 min |
| Local Docker | Container testing | Easy | 10 min |
| Docker Compose | Multi-service testing | Easy | 15 min |
| Azure Container Apps | Serverless production | Medium | 30 min |
| Azure App Service | Traditional managed hosting | Medium | 30 min |

---

## Option 1: Local Development

### Easiest Setup (5 minutes)

```bash
# 1. Clone repository
git clone https://github.com/derricksobrien/poc-accelerator.git
cd poc-accelerator

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install requirements
pip install -r requirements.txt

# 4. Set environment variables
export OPENAI_API_KEY="your-key-here"
export OPENAI_API_BASE="https://your-instance.openai.azure.com"

# 5. Run Flask server
python TechConnect/app.py
# Visit http://localhost:5000
```

### Running Streamlit Dashboard
```bash
streamlit run System3-RAG/streamlit_app.py
# Visit http://localhost:8501
```

---

## Option 2: Docker Container

### Build & Run Locally (10 minutes)

```bash
# Build image
docker build -t poc-accelerator:latest .

# Run container
docker run -p 5000:5000 \
  -e OPENAI_API_KEY="your-key" \
  -e OPENAI_API_BASE="https://your-instance.openai.azure.com" \
  poc-accelerator:latest

# Visit http://localhost:5000
```

### With Docker Compose
```bash
# Create .env file
echo 'OPENAI_API_KEY=your-key-here' > .env
echo 'OPENAI_API_BASE=https://your-instance.openai.azure.com' >> .env

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## Option 3: Azure Container Apps

### Production-Ready Cloud Deployment (30 minutes)

#### Prerequisites
```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login to Azure
az login

# Set variables
RG_NAME="poc-accelerator-rg"
LOCATION="eastus"
REGISTRY_NAME="pocacceleratoracr"
APP_NAME="poc-accelerator"
```

#### Step 1: Create Resource Group
```bash
az group create \
  --name $RG_NAME \
  --location $LOCATION
```

#### Step 2: Create Container Registry
```bash
az acr create \
  --resource-group $RG_NAME \
  --name $REGISTRY_NAME \
  --sku Basic

# Login to registry
az acr login --name $REGISTRY_NAME

# Get login server URL
LOGIN_SERVER=$(az acr show \
  --name $REGISTRY_NAME \
  --query loginServer -o tsv)
```

#### Step 3: Build & Push Container
```bash
# Build in Azure
az acr build \
  --registry $REGISTRY_NAME \
  --image poc-accelerator:latest .

# Tag image
docker tag poc-accelerator:latest \
  $LOGIN_SERVER/poc-accelerator:latest
```

#### Step 4: Create Container App Environment
```bash
az containerapp env create \
  --name poc-env \
  --resource-group $RG_NAME \
  --location $LOCATION
```

#### Step 5: Deploy Container App
```bash
az containerapp create \
  --name $APP_NAME \
  --resource-group $RG_NAME \
  --environment poc-env \
  --image $LOGIN_SERVER/poc-accelerator:latest \
  --target-port 5000 \
  --ingress external \
  --env-vars \
    OPENAI_API_KEY='your-key' \
    OPENAI_API_BASE='https://your-instance.openai.azure.com' \
  --registry-server $LOGIN_SERVER \
  --registry-username admin \
  --registry-password $(az acr credential show \
    --name $REGISTRY_NAME \
    --query passwords[0].value -o tsv)
```

#### Step 6: Get App URL
```bash
az containerapp show \
  --name $APP_NAME \
  --resource-group $RG_NAME \
  --query properties.configuration.ingress.fqdn -o tsv
```

---

## Option 4: Azure App Service

### Traditional Managed Hosting (30 minutes)

#### Prerequisites
```bash
# Set variables
APP_NAME="poc-accelerator-app"
PLAN_NAME="poc-plan"
RG_NAME="poc-accelerator-rg"
```

#### Step 1: Create App Service Plan
```bash
az appservice plan create \
  --name $PLAN_NAME \
  --resource-group $RG_NAME \
  --sku B1 \
  --is-linux
```

#### Step 2: Create Web App
```bash
az webapp create \
  --name $APP_NAME \
  --resource-group $RG_NAME \
  --plan $PLAN_NAME \
  --runtime "python:3.9"
```

#### Step 3: Configure Deployment
```bash
# Deploy from Git
az webapp deployment source config \
  --name $APP_NAME \
  --resource-group $RG_NAME \
  --repo-url https://github.com/derricksobrien/poc-accelerator.git \
  --branch master \
  --manual-integration
```

#### Step 4: Set Environment Variables
```bash
az webapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RG_NAME \
  --settings \
    OPENAI_API_KEY='your-key' \
    OPENAI_API_BASE='https://your-instance.openai.azure.com'
```

#### Step 5: Restart App
```bash
az webapp restart \
  --name $APP_NAME \
  --resource-group $RG_NAME
```

---

## Monitoring & Logging

### View Logs (All Platforms)
```bash
# Docker local
docker logs container-name

# Container Apps
az containerapp logs show \
  --name $APP_NAME \
  --resource-group $RG_NAME

# App Service
az webapp log tail \
  --name $APP_NAME \
  --resource-group $RG_NAME
```

### Health Checks
```bash
# Local
curl http://localhost:5000/api/health

# Azure Container Apps
curl https://your-app-url/api/health

# App Service
curl https://your-app-name.azurewebsites.net/api/health
```

---

## Scaling

### Docker Compose Scaling
```bash
docker-compose up -d --scale api=3
```

### Container Apps Auto-scaling
```bash
az containerapp update \
  --name $APP_NAME \
  --resource-group $RG_NAME \
  --scale-rule-name cpu-scaling \
  --scale-rule-type cpu \
  --scale-rule-metadata target=70
```

### App Service Auto-scaling
```bash
az monitor autoscale create \
  --resource-group $RG_NAME \
  --name poc-autoscale \
  --resource $APP_NAME \
  --resource-type "Microsoft.Web/sites" \
  --min-count 1 \
  --max-count 3 \
  --count 2
```

---

## Upgrading

### Update Container Image
```bash
# Build new image
docker build -t poc-accelerator:v2.0 .

# Push to registry
docker tag poc-accelerator:v2.0 $LOGIN_SERVER/poc-accelerator:v2.0
docker push $LOGIN_SERVER/poc-accelerator:v2.0

# Update Container App
az containerapp update \
  --name $APP_NAME \
  --resource-group $RG_NAME \
  --image $LOGIN_SERVER/poc-accelerator:v2.0
```

---

## Cost Estimation

| Service | Tier | Monthly Cost |
|---------|------|-------------|
| Local Docker | - | $0 |
| Container Apps | Standard | $5-50 |
| Container Registry | Basic | $5 |
| App Service | B1 | $12.50 |
| **Total (small)** | | **$17.50+** |

---

## Troubleshooting Deployments

**Container won't start:**
- Check env vars: `docker inspect container-id`
- View logs: See "View Logs" section above
- Verify ports: `docker port container-id`

**502 Bad Gateway:**
- Ensure health check passes: `curl /api/health`
- Check startup completed: Review logs
- Scale up instances if needed

**High memory usage:**
- Check for memory leaks: Review logs
- Reduce model batch size in configuration
- Increase container memory allocation

---

**Need Help?** See [Troubleshooting Guide](TROUBLESHOOTING.md) or check [Getting Started](GETTING-STARTED.md).

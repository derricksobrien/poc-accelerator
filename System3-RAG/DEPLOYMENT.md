# System3-RAG Deployment Guide

**Status**: ✅ Ready to Deploy  
**Options**: Local Docker | Azure Container Apps | Azure Container Instances

---

## 🚀 Option 1: Deploy Locally with Docker (5 minutes)

### Quick Start
```bash
cd c:\Users\derri\Code\techconnect_all\System3-RAG

# Build image
docker build -t system3-rag:latest .

# Run container
docker run -p 8000:8000 -p 8501:8501 system3-rag:latest

# Open in browser
# Backend API: http://localhost:8000
# Streamlit UI: http://localhost:8501
# Swagger Docs: http://localhost:8000/docs
```

### Using Docker Compose (Recommended)
```bash
# Start both services
docker-compose up --build

# Stop
docker-compose down

# View logs
docker-compose logs -f
```

### Verify Deployment
```bash
# Health check
curl http://localhost:8000/health

# API test
curl -X POST http://localhost:8000/api/rag/generate-poc \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test",
    "title": "Test POC",
    "solution_area": "AI",
    "complexity": "L400",
    "requirements": "Test deployment"
  }'

# Streamlit should load at http://localhost:8501
```

---

## ☁️ Option 2: Deploy to Azure Container Apps (15 minutes)

### Prerequisites
```bash
# Install Azure CLI
az --version

# Login
az login

# Set defaults
az config set defaults.group=<your-resource-group>
az config set defaults.location=eastus
```

### Step 1: Create Container Registry
```bash
# Create ACR (Azure Container Registry)
az acr create \
  --resource-group <your-resource-group> \
  --name <acr-name> \
  --sku Basic

# Example:
# az acr create --resource-group contoso-ai-rg --name contosoacr --sku Basic

# Enable admin user
az acr update -n <acr-name> --admin-enabled true

# Get credentials
az acr credential show --resource-group <your-resource-group> --name <acr-name>
```

### Step 2: Build & Push Image
```bash
# Build in ACR (no Docker Desktop needed!)
az acr build \
  --registry <acr-name> \
  --image system3-rag:latest .

# Or build locally then push
docker build -t <acr-name>.azurecr.io/system3-rag:latest .
docker push <acr-name>.azurecr.io/system3-rag:latest

# Verify
az acr repository list --name <acr-name>
```

### Step 3: Deploy to Container Apps
```bash
# Create container app environment (if first time)
az containerapp env create \
  --name system3-env \
  --resource-group <your-resource-group>

# Deploy container app
az containerapp create \
  --name system3-rag \
  --resource-group <your-resource-group> \
  --environment system3-env \
  --image <acr-name>.azurecr.io/system3-rag:latest \
  --target-port 8501 \
  --ingress 'external' \
  --registry-server <acr-name>.azurecr.io \
  --registry-username <username> \
  --registry-password <password> \
  --cpu 2 \
  --memory 4Gi \
  --env-vars \
    FASTAPI_HOST=0.0.0.0 \
    FASTAPI_PORT=8000 \
    LOG_LEVEL=INFO

# Get URL
az containerapp show \
  --name system3-rag \
  --resource-group <your-resource-group> \
  --query properties.configuration.ingress.fqdn
```

### Step 4: Access Application
```
URL: https://system3-rag.<region>.azurecontainerapps.io

Note: Application exposes port 8501 (Streamlit)
Backend API on same container, accessible internally
```

---

## 🔐 Option 3: Deploy with Azure Credentials

If you have Azure AI Foundry configured:

### Step 1: Update Environment Variables
```bash
# Add to container app
az containerapp update \
  --name system3-rag \
  --resource-group <your-resource-group> \
  --set-env-vars \
    AZURE_OPENAI_ENDPOINT="https://<resource>.openai.azure.com/" \
    AZURE_OPENAI_KEY="<your-key>" \
    AZURE_MODEL_DEPLOYMENT="gpt4-deployment"

# Or use Azure Key Vault
az containerapp identity assign \
  --name system3-rag \
  --resource-group <your-resource-group> \
  --system-assigned

# Store secrets in Key Vault
az keyvault secret set \
  --vault-name <vault-name> \
  --name openai-key \
  --value "<your-key>"
```

### Step 2: Restart Application
```bash
# Restart to apply environment variables
az containerapp revision restart \
  --name system3-rag \
  --resource-group <your-resource-group> \
  --revision latest
```

---

## 📊 Scaling & Monitoring

### Scale up/down
```bash
# Increase replicas
az containerapp update \
  --name system3-rag \
  --resource-group <your-resource-group> \
  --min-replicas 1 \
  --max-replicas 5

# Set CPU/memory
az containerapp update \
  --name system3-rag \
  --resource-group <your-resource-group> \
  --cpu 4 --memory 8Gi
```

### View logs
```bash
# Stream logs
az containerapp logs show \
  --name system3-rag \
  --resource-group <your-resource-group> \
  --follow

# View revision info
az containerapp revision list \
  --name system3-rag \
  --resource-group <your-resource-group>
```

### Health monitoring
```bash
# Get status
az containerapp show \
  --name system3-rag \
  --resource-group <your-resource-group>

# Check provisioning state
az containerapp show \
  --name system3-rag \
  --resource-group <your-resource-group> \
  --query provisioningState
```

---

## 🐛 Troubleshooting Deployment

### Container won't start
```bash
# Check logs
az containerapp logs show \
  --name system3-rag \
  --resource-group <your-resource-group> \
  --follow

# Common issues:
# - Port 8501 not exposed (fix: --target-port 8501)
# - Image not found (fix: verify ACR push succeeded)
# - Memory too low (fix: --memory 4Gi minimum)
```

### Image push fails
```bash
# Verify container is built
az acr repository list --name <acr-name>

# Verify credentials
az acr credential show --name <acr-name>

# Rebuild and push
az acr build --registry <acr-name> --image system3-rag:latest .
```

### Application timeout
```bash
# Increase timeout
az containerapp update \
  --name system3-rag \
  --resource-group <your-resource-group> \
  --ingress-transport http --ingress-allow-insecure false

# Scale up
az containerapp update \
  --name system3-rag \
  --resource-group <your-resource-group> \
  --cpu 4 --memory 8Gi
```

### Can't reach application
```bash
# Verify ingress
az containerapp show \
  --name system3-rag \
  --resource-group <your-resource-group> \
  --query properties.configuration.ingress

# Verify network connectivity
curl -v https://system3-rag.<region>.azurecontainers.io/health
```

---

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] Docker installed and running
- [ ] All tests pass: `pytest test_*.py -v`
- [ ] Dockerfile builds locally: `docker build -t system3-rag:latest .`
- [ ] Azure CLI authenticated: `az account show`

### Local Deployment
- [ ] Docker image builds: `docker build -t system3-rag:latest .`
- [ ] Container runs: `docker run -p 8000:8000 -p 8501:8501 system3-rag:latest`
- [ ] API responds: `curl http://localhost:8000/health`
- [ ] UI loads: http://localhost:8501

### Azure Deployment
- [ ] ACR created: `az acr list`
- [ ] Image pushed: `az acr repository list --name <acr>`
- [ ] Container App created: `az containerapp show --name system3-rag`
- [ ] Application accessible: `https://system3-rag.<region>.azurecontainers.io`

### Post-Deployment
- [ ] Health check passes
- [ ] Logs look good
- [ ] Generate POC endpoint works
- [ ] Search endpoint works
- [ ] Streamlit UI interactive

---

## 🔗 Useful Commands Quick Reference

```bash
# Docker
docker build -t system3-rag:latest .
docker run -p 8000:8000 -p 8501:8501 system3-rag:latest
docker-compose up --build
docker-compose down

# Azure ACR
az acr build --registry <name> --image system3-rag:latest .
az acr login --name <name>

# Azure Container Apps
az containerapp create --name system3-rag ...
az containerapp update --name system3-rag ...
az containerapp logs show --name system3-rag --follow
az containerapp delete --name system3-rag

# Health checks
curl http://localhost:8000/health
curl http://localhost:8000/docs
# Streamlit: http://localhost:8501
```

---

## 💰 Cost Estimation

### Local Docker
- **Cost**: $0 (free)
- **Time**: 5 minutes
- **Use case**: Development, testing

### Azure Container Apps
- **CPU**: 2 core × $0.040/hour = ~$29/month (always on)
- **Memory**: 4GB × $0.005/hour = ~$36/month
- **Storage**: ~1GB = minimal
- **Total**: ~$65/month (with auto-scaling: $20-50)
- **Use case**: Production, demo, POC

### Azure Container Instances (One-time)
- **Per execution**: $0.0000145/second
- **Use case**: Batch jobs, occasional testing

---

## ✅ Success Indicators

Once deployed:

1. **Backend responds**
   ```bash
   curl http://localhost:8000/health
   # Returns: {"status": "healthy"}
   ```

2. **API works**
   ```bash
   curl -X POST http://localhost:8000/api/rag/generate-poc \
     -H "Content-Type: application/json" \
     -d '{"session_id": "test", "title": "POC", ...}'
   # Returns: JSON with POC details
   ```

3. **UI loads**
   ```
   http://localhost:8501
   # Shows Streamlit interface with 5 tabs
   ```

4. **Endpoints accessible**
   - API Docs: http://localhost:8000/docs
   - Health: http://localhost:8000/health
   - Status: http://localhost:8000/status

---

## 🚀 Deployment Paths Recommended

### Path 1: Quick Local Test (5 min)
```bash
docker-compose up --build
# Test at http://localhost:8501
# Verify all works, then proceed to Azure
```

### Path 2: Production Azure (20 min)
```bash
# Setup ACR
az acr create --resource-group <rg> --name <acr> --sku Basic

# Build & push
az acr build --registry <acr> --image system3-rag:latest .

# Deploy
az containerapp create \
  --name system3-rag \
  --resource-group <rg> \
  --environment <env> \
  --image <acr>.azurecr.io/system3-rag:latest \
  --target-port 8501 \
  --ingress external

# Access
# https://system3-rag.<region>.azurecontainers.io
```

### Path 3: With Real Agent (25 min)
```bash
# First: Setup Azure AI Foundry
python setup_azure_agent.py --subscription <id> --resource-group <rg>

# Then: Deployment (as above) with env vars
az containerapp update \
  --name system3-rag \
  --set-env-vars \
    AZURE_OPENAI_ENDPOINT="..." \
    AZURE_OPENAI_KEY="..."
```

---

## 📚 Full Documentation

For complete details, see:
- **TESTING_GUIDE.md** - Test suite setup
- **QUICK_TEST_REFERENCE.md** - Command reference
- **STREAMLIT_QUICKSTART.md** - UI guide
- **README.md** - System overview

---

**Status**: ✅ Ready to Deploy  
**Recommended**: Start with local Docker, then Azure  
**Time**: 5-20 minutes depending on option

Let's go! 🚀

---

*Created: February 2026*  
*System3-RAG Deployment Guide*

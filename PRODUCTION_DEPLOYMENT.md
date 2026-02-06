# POC Accelerator - Production Deployment Guide

**Version**: 1.0.0  
**Last Updated**: February 2026  
**Status**: Production Ready

## Overview

This guide covers deploying the POC Accelerator RAG system to production environments including Azure Container Apps, Azure App Service, and Docker registries.

---

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Local Testing](#local-testing)
3. [Azure Container Apps Deployment](#azure-container-apps-deployment)
4. [Azure App Service Deployment](#azure-app-service-deployment)
5. [Docker Hub Deployment](#docker-hub-deployment)
6. [Environment Configuration](#environment-configuration)
7. [Monitoring & Logging](#monitoring--logging)
8. [Troubleshooting](#troubleshooting)

---

## Pre-Deployment Checklist

### Prerequisites
- [ ] Python 3.10+ installed
- [ ] Azure CLI installed and authenticated (`az login`)
- [ ] Docker installed (for containerization)
- [ ] Git installed
- [ ] Azure subscription with sufficient quotas
- [ ] GitHub account (for saving POCs)

### Code Readiness
- [ ] All tests pass: `python test_comprehensive.py`
- [ ] API endpoints tested locally
- [ ] Configuration files validated
- [ ] Environment variables documented

### Azure Resources
- [ ] Resource group created
- [ ] Azure OpenAI deployment available
- [ ] Azure AI Search instance (optional)
- [ ] Key Vault configured (optional but recommended)
- [ ] Storage account for POC artifacts (optional)

### Security Review
- [ ] No hardcoded credentials in code
- [ ] All secrets in `.env` or Azure Key Vault
- [ ] GitHub token secured
- [ ] HTTPS enabled for production
- [ ] Authentication configured for API endpoints

---

## Local Testing

### 1. Start Development Server

```bash
# Activate virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements-rag.txt

# Set environment variables
export FLASK_DEBUG=True
export PORT=5000

# Start server
python app.py
```

Expected output:
```
Running on http://localhost:5000
```

### 2. Test Web Interface

Visit http://localhost:5000 and verify:
- [ ] Solution areas load
- [ ] POC generation form displays
- [ ] System stats panel shows
- [ ] Data sources list loads

### 3. Test API Endpoints

```bash
# Get solution areas
curl http://localhost:5000/api/solution-areas

# Get system stats
curl http://localhost:5000/api/system-stats

# Get POC history
curl http://localhost:5000/api/poc-history

# Generate POC (example)
curl -X POST http://localhost:5000/api/generate-poc \
  -H "Content-Type: application/json" \
  -d '{
    "poc_title": "AI Chatbot",
    "solution_area": "ai-business",
    "save_to_github": false
  }'
```

### 4. Run Comprehensive Tests

```bash
python test_comprehensive.py
```

All 9 test modules should pass.

---

## Azure Container Apps Deployment

### Step 1: Create Container Image

```bash
# Build Docker image
docker build -t poc-accelerator:latest .

# Tag for Azure Container Registry (ACR)
docker tag poc-accelerator:latest myregistry.azurecr.io/poc-accelerator:latest

# Login to ACR
az acr login --name myregistry

# Push to ACR
docker push myregistry.azurecr.io/poc-accelerator:latest
```

### Step 2: Set Environment Variables in Azure

```bash
# Set resource group and location
RESOURCE_GROUP="poc-accelerator-rg"
LOCATION="eastus"
REGISTRY_NAME="myregistry"
CONTAINER_APP_NAME="poc-accelerator-app"

# Create resource group
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION
```

### Step 3: Create Container App Environment

```bash
# Create environment
az containerapp env create \
  --name poc-env \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION
```

### Step 4: Deploy Container App

```bash
# Create container app with environment variables
az containerapp create \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment poc-env \
  --image myregistry.azurecr.io/poc-accelerator:latest \
  --target-port 5000 \
  --ingress external \
  --registry-server myregistry.azurecr.io \
  --registry-username <registry-username> \
  --registry-password <registry-password> \
  --env-vars \
    AZURE_OPENAI_ENDPOINT=$AZURE_OPENAI_ENDPOINT \
    AZURE_OPENAI_KEY=$AZURE_OPENAI_KEY \
    AZURE_RESOURCE_GROUP=$RESOURCE_GROUP \
    FLASK_DEBUG=False \
    PORT=5000
```

### Step 5: Get Application URL

```bash
az containerapp show \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn \
  --output tsv
```

Visit the returned URL to access your POC Accelerator.

---

## Azure App Service Deployment

### Step 1: Create App Service Plan

```bash
RESOURCE_GROUP="poc-accelerator-rg"
APP_SERVICE_PLAN="poc-plan"
APP_SERVICE_NAME="poc-accelerator-app"
LOCATION="eastus"

# Create App Service Plan
az appservice plan create \
  --name $APP_SERVICE_PLAN \
  --resource-group $RESOURCE_GROUP \
  --sku B2 \
  --is-linux
```

### Step 2: Create Web App

```bash
# Create web app with Python runtime
az webapp create \
  --resource-group $RESOURCE_GROUP \
  --plan $APP_SERVICE_PLAN \
  --name $APP_SERVICE_NAME \
  --runtime "PYTHON:3.10"
```

### Step 3: Configure Application Settings

```bash
# Set environment variables
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name $APP_SERVICE_NAME \
  --settings \
    AZURE_OPENAI_ENDPOINT=$AZURE_OPENAI_ENDPOINT \
    AZURE_OPENAI_KEY=$AZURE_OPENAI_KEY \
    AZURE_RESOURCE_GROUP=$RESOURCE_GROUP \
    FLASK_DEBUG=False
```

### Step 4: Deploy Code

Option A: Deploy from GitHub
```bash
# Configure GitHub source
az webapp deployment source config-zip \
  --resource-group $RESOURCE_GROUP \
  --name $APP_SERVICE_NAME \
  --src deploy.zip
```

Option B: Deploy from Local Git
```bash
# Initialize local git repo and deploy
git init
git add .
git commit -m "Initial POC Accelerator deployment"

az webapp deployment source config-local-git \
  --name $APP_SERVICE_NAME \
  --resource-group $RESOURCE_GROUP

git push <git-url> master
```

### Step 5: Verify Deployment

```bash
# Get app URL
az webapp show \
  --resource-group $RESOURCE_GROUP \
  --name $APP_SERVICE_NAME \
  --query defaultHostName \
  --output tsv
```

---

## Docker Hub Deployment

### Step 1: Build Docker Image

```bash
docker build -t your-docker-username/poc-accelerator:1.0.0 .
```

### Step 2: Tag Image

```bash
docker tag poc-accelerator:latest your-docker-username/poc-accelerator:latest
docker tag poc-accelerator:latest your-docker-username/poc-accelerator:1.0.0
```

### Step 3: Push to Docker Hub

```bash
# Login to Docker Hub
docker login

# Push images
docker push your-docker-username/poc-accelerator:latest
docker push your-docker-username/poc-accelerator:1.0.0
```

### Step 4: Run Container Locally

```bash
docker run -p 5000:5000 \
  -e AZURE_OPENAI_ENDPOINT=$AZURE_OPENAI_ENDPOINT \
  -e AZURE_OPENAI_KEY=$AZURE_OPENAI_KEY \
  your-docker-username/poc-accelerator:latest
```

---

## Environment Configuration

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI API endpoint | `https://my-resource.openai.azure.com/` |
| `AZURE_OPENAI_KEY` | Azure OpenAI API key | `sk-...` |
| `FLASK_DEBUG` | Debug mode (False for production) | `False` |
| `PORT` | Application port | `5000` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AZURE_SEARCH_ENDPOINT` | Azure AI Search endpoint | (disabled) |
| `AZURE_SEARCH_KEY` | Azure AI Search key | (disabled) |
| `GITHUB_TOKEN` | GitHub personal access token | (disabled) |
| `GITHUB_REPO_OWNER` | GitHub repository owner | (disabled) |
| `GITHUB_REPO_NAME` | GitHub repository name | (disabled) |
| `AZURE_RESOURCE_GROUP` | Azure resource group | poc-accelerator-rg |
| `AZURE_LOCATION` | Azure region | eastus |

### Using Azure Key Vault (Recommended for Production)

```bash
# Create Key Vault
az keyvault create \
  --name poc-kv \
  --resource-group $RESOURCE_GROUP

# Add secrets
az keyvault secret set \
  --vault-name poc-kv \
  --name "AzureOpenAiKey" \
  --value $AZURE_OPENAI_KEY

az keyvault secret set \
  --vault-name poc-kv \
  --name "GitHubToken" \
  --value $GITHUB_TOKEN

# Configure app to use Key Vault
# Update app.py to fetch from Key Vault instead of .env
```

---

## Monitoring & Logging

### Azure Application Insights Integration

```python
# Add to app.py
from azure.monitor.opentelemetry import configure_azure_monitor

configure_azure_monitor()

# Now all requests and exceptions are tracked
```

### Enable Logging in App Service

```bash
# Enable application logging
az webapp log config \
  --name $APP_SERVICE_NAME \
  --resource-group $RESOURCE_GROUP \
  --application-logging true \
  --level information

# View logs
az webapp log tail \
  --name $APP_SERVICE_NAME \
  --resource-group $RESOURCE_GROUP
```

### Performance Monitoring

```bash
# Get metrics
az monitor metrics list \
  --resource /subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/Microsoft.Web/sites/{app-name} \
  --metric "Requests" \
  --aggregation Total
```

---

## Scaling Configuration

### Container Apps Auto-Scaling

```bash
# Set auto-scale rules
az containerapp update \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --scale-rule-name cpu-scaling \
  --scale-rule-type cpu \
  --scale-rule-metadata type=Utilization value=75
```

### App Service Scaling

```bash
# Create auto-scale rule
az monitor autoscale create \
  --resource-group $RESOURCE_GROUP \
  --resource-name $APP_SERVICE_PLAN \
  --resource-type "Microsoft.Web/serverfarms" \
  --min-count 2 \
  --max-count 10 \
  --count 2
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError"

```bash
# Ensure dependencies are installed
pip install -r requirements-rag.txt

# Check Python version
python --version  # Should be 3.10+
```

### Issue: "Azure credentials not found"

```bash
# Login to Azure
az login

# Set subscription
az account set --subscription <subscription-id>

# Verify credentials
az account show
```

### Issue: "Port already in use"

```bash
# Use different port
PORT=8000 python app.py

# Or kill process on port 5000
# Windows: netstat -ano | findstr :5000
# Linux: sudo lsof -i :5000
```

### Issue: "GitHub push failed"

```bash
# Verify GitHub token
echo $GITHUB_TOKEN

# Check Git configuration
git config --global user.name
git config --global user.email

# Test GitHub authentication
git ls-remote https://github.com/your-org/your-repo
```

### Issue: "Azure OpenAI quota exceeded"

```bash
# Check usage
az openai deployment list \
  --resource-group $RESOURCE_GROUP

# Request quota increase in Azure portal
```

---

## Backup & Disaster Recovery

### Backup POC Instructions

```bash
# Export POC repository
zip -r poc-backup-$(date +%Y%m%d).zip local-poc-repo/

# Push to Azure Blob Storage
az storage blob upload \
  --account-name myaccount \
  --container-name backups \
  --name poc-backup-$(date +%Y%m%d).zip \
  --file poc-backup-$(date +%Y%m%d).zip
```

### Restore from Backup

```bash
# Download from Blob Storage
az storage blob download \
  --account-name myaccount \
  --container-name backups \
  --name poc-backup-20260201.zip \
  --file restore.zip

# Extract
unzip restore.zip -d local-poc-repo/
```

---

## Security Checklist

- [ ] HTTPS enabled for all endpoints
- [ ] No hardcoded secrets in code
- [ ] All credentials in environment variables or Key Vault
- [ ] GitHub token has minimal required scopes
- [ ] API authentication implemented (if needed)
- [ ] CORS configured for specific origins
- [ ] Input validation on all endpoints
- [ ] Rate limiting implemented
- [ ] Regular security updates scheduled
- [ ] Audit logging enabled
- [ ] Data encrypted in transit and at rest

---

## Performance Optimization

### Caching
```python
# Enable caching in app.py
from functools import lru_cache

@lru_cache(maxsize=100)
def get_solution_areas():
    # Cached for performance
    pass
```

### Database Connection Pooling
```python
# Use connection pooling for Azure services
from sqlalchemy import create_engine
engine = create_engine('...', pool_size=20, max_overflow=0)
```

### CDN Integration
```bash
# Use Azure CDN for static assets
az cdn profile create \
  --name poc-cdn \
  --resource-group $RESOURCE_GROUP \
  --sku Standard_Microsoft
```

---

## Maintenance Schedule

| Task | Frequency | Owner |
|------|-----------|-------|
| Security patches | Weekly | DevOps |
| Dependency updates | Monthly | Development |
| POC archive | Monthly | Operations |
| Performance review | Monthly | DevOps |
| Capacity planning | Quarterly | Architecture |
| Disaster recovery test | Quarterly | Operations |

---

## Support & Escalation

For issues, contact:
- **Development**: team@example.com
- **Azure Support**: https://portal.azure.com/
- **GitHub Issues**: https://github.com/your-org/poc-accelerator/issues

---

**End of Deployment Guide**

For additional support, see `RAG_SETUP_GUIDE.md` and `README.md`

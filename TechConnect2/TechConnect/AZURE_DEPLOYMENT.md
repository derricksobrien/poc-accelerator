# Azure Deployment Guide - TechConnect API

## Overview

This guide walks you through deploying the TechConnect API to Azure in testable stages:

1. **Stage 1: Azure Container Registry (ACR)** — Store Docker image
2. **Stage 2: Azure Container Instances (ACI)** — Quick test deployment
3. **Stage 3: Azure App Service** — Production-ready with auto-scaling
4. **Stage 4: Azure Container Apps** — Modern serverless alternative

---

## Prerequisites

- Azure subscription (create free: https://azure.microsoft.com/free)
- Azure CLI installed (`az --version` returns v2.50+)
- Docker image working locally (`docker run ...` succeeds)
- Git for pushing to Azure repos

**Install Azure CLI:**
```powershell
# Windows
choco install azure-cli
# Or download: https://aka.ms/installazurecliwindows

# Verify
az --version
```

---

## Stage 1: Set Up Azure Container Registry (20 minutes)

### Step 1.1: Login to Azure

```powershell
az login
# Browser opens; sign in with your Microsoft account
# Returns subscription ID upon success
```

### Step 1.2: Create Resource Group

```powershell
$resourceGroup = "techconnect-rg"
$location = "eastus"  # or your preferred region

az group create `
  --name $resourceGroup `
  --location $location

# Verify
az group list --output table
```

### Step 1.3: Create Container Registry

```powershell
$acrName = "techconnectregistry"  # Must be globally unique
$resourceGroup = "techconnect-rg"

az acr create `
  --resource-group $resourceGroup `
  --name $acrName `
  --sku Basic `  # Basic = $5/month; Standard for production
  --admin-enabled true

# Get login credentials
az acr credential show `
  --resource-group $resourceGroup `
  --name $acrName

# Output: username, password (save for later)
```

### Step 1.4: Push Docker Image to ACR

```powershell
$acrName = "techconnectregistry"
$acrUrl = "$acrName.azurecr.io"
$imageTag = "techconnect-api:v1.0.0"

# Login to ACR
az acr login --name $acrName
# Or use credentials from Step 1.3

# Tag image
docker tag techconnect-api:latest $acrUrl/techconnect-api:v1.0.0
docker tag techconnect-api:latest $acrUrl/techconnect-api:latest

# Push to registry
docker push $acrUrl/techconnect-api:v1.0.0
docker push $acrUrl/techconnect-api:latest

# Verify
az acr repository list --name $acrName --output table
az acr repository show-tags --name $acrName --repository techconnect-api
```

---

## Stage 2: Deploy to Azure Container Instances (Quick Test - 15 minutes)

### Step 2.1: Deploy Container

```powershell
$acrName = "techconnectregistry"
$acrUrl = "$acrName.azurecr.io"
$containerName = "techconnect-api-test"
$resourceGroup = "techconnect-rg"
$imageUrl = "$acrUrl/techconnect-api:latest"

# Get ACR credentials
$acrPassword = az acr credential show `
  --resource-group $resourceGroup `
  --name $acrName `
  --query "passwords[0].value" -o tsv

# Deploy
az container create `
  --resource-group $resourceGroup `
  --name $containerName `
  --image $imageUrl `
  --cpu 1 `
  --memory 1.5 `
  --registry-login-server "$acrUrl" `
  --registry-username "$acrName" `
  --registry-password $acrPassword `
  --environment-variables PORT=8000 `
  --ports 8000 `
  --dns-name-label techconnect-api-test

# Monitor deployment
az container show `
  --resource-group $resourceGroup `
  --name $containerName `
  --query "containers[0].instanceView.currentState"
```

### Step 2.2: Test Deployment

```powershell
# Get public IP
$publicIp = az container show `
  --resource-group $resourceGroup `
  --name $containerName `
  --query "ipAddress.fqdn" -o tsv

echo "API URL: http://$publicIp:8000"

# Test endpoints
curl "http://$publicIp:8000/health"
curl "http://$publicIp:8000/accelerators"

# Full test
curl -X POST "http://$publicIp:8000/context" `
  -H "Content-Type: application/json" `
  -d '{"scenario_title":"AI automation","solution_area":"AI","num_results":2}'
```

### Step 2.3: View Logs

```powershell
az container logs `
  --resource-group $resourceGroup `
  --name $containerName `
  --follow
```

### Step 2.4: Cleanup Test Deployment

```powershell
az container delete `
  --resource-group $resourceGroup `
  --name $containerName `
  --yes
```

---

## Stage 3: Deploy to Azure App Service (Production - 30 minutes)

### Step 3.1: Create App Service Plan

```powershell
$appServicePlan = "techconnect-plan"
$resourceGroup = "techconnect-rg"

az appservice plan create `
  --name $appServicePlan `
  --resource-group $resourceGroup `
  --sku B1 `  # B1 = $12.75/month; P1V2 for production
  --is-linux

# Verify
az appservice plan list --output table
```

### Step 3.2: Deploy Web App

```powershell
$webAppName = "techconnect-api-prod"  # Must be globally unique
$appServicePlan = "techconnect-plan"
$resourceGroup = "techconnect-rg"
$acrUrl = "techconnectregistry.azurecr.io"

az webapp create `
  --resource-group $resourceGroup `
  --plan $appServicePlan `
  --name $webAppName `
  --deployment-container-image-name "$acrUrl/techconnect-api:latest"

# Configure container settings
az webapp config container set `
  --name $webAppName `
  --resource-group $resourceGroup `
  --docker-custom-image-name "$acrUrl/techconnect-api:latest" `
  --docker-registry-server-url "https://$acrUrl" `
  --docker-registry-server-user "techconnectregistry" `
  --docker-registry-server-password $acrPassword `
  --enable-app-service-storage false

# Configure port
az webapp config appsettings set `
  --name $webAppName `
  --resource-group $resourceGroup `
  --settings WEBSITES_PORT=8000 PORT=8000
```

### Step 3.3: Test App Service Deployment

```powershell
$webAppName = "techconnect-api-prod"

# Get URL
$appUrl = az webapp show `
  --resource-group techconnect-rg `
  --name $webAppName `
  --query "defaultHostName" -o tsv

echo "Web App URL: https://$appUrl"

# Health check (may take 2-3 min to start)
curl "https://$appUrl/health"

# Test API
curl -X POST "https://$appUrl/context" `
  -H "Content-Type: application/json" `
  -d '{"scenario_title":"AI automation","num_results":1}'
```

### Step 3.4: View App Service Logs

```powershell
# Enable logging
az webapp log config `
  --name techconnect-api-prod `
  --resource-group techconnect-rg `
  --docker-container-logging filesystem

# Stream logs
az webapp log tail `
  --name techconnect-api-prod `
  --resource-group techconnect-rg
```

---

## Stage 4: Azure Container Apps (Modern Serverless - Optional)

### Step 4.1: Create Container Apps Environment

```powershell
$containerAppEnv = "techconnect-env"
$resourceGroup = "techconnect-rg"
$location = "eastus"

az containerapp env create `
  --name $containerAppEnv `
  --resource-group $resourceGroup `
  --location $location
```

### Step 4.2: Deploy Container App

```powershell
$containerAppName = "techconnect-api-app"
$acrUrl = "techconnectregistry.azurecr.io"
$acrPassword = "..."  # From Step 1.3

az containerapp create `
  --resource-group techconnect-rg `
  --name $containerAppName `
  --environment $containerAppEnv `
  --image "$acrUrl/techconnect-api:latest" `
  --target-port 8000 `
  --ingress external `
  --min-replicas 1 `
  --max-replicas 3 `
  --registry-server $acrUrl `
  --registry-username "techconnectregistry" `
  --registry-password $acrPassword
```

### Step 4.3: Test Container App

```powershell
# Get URL
$appUrl = az containerapp show `
  --name techconnect-api-app `
  --resource-group techconnect-rg `
  --query properties.latestRevisionFqdn -o tsv

curl "https://$appUrl/health"
```

---

## CI/CD Pipeline Setup (GitHub Actions - Optional)

### Step 5.1: Create GitHub Secrets

In GitHub repo settings → Secrets:
```
ACR_LOGIN_SERVER = techconnectregistry.azurecr.io
ACR_USERNAME = techconnectregistry
ACR_PASSWORD = <from-step-1.3>
AZURE_CREDENTIALS = <from-step-5.2>
```

### Step 5.2: Create Service Principal

```powershell
# Create service principal for CI/CD
az ad sp create-for-rbac `
  --name techconnect-cicd `
  --role contributor `
  --scopes /subscriptions/{subscriptionId}/resourceGroups/techconnect-rg `
  --json-auth

# Copy entire JSON output to GitHub secret AZURE_CREDENTIALS
```

### Step 5.3: Create GitHub Workflow

Create `.github/workflows/deploy-azure.yml`:

```yaml
name: Deploy to Azure

on:
  push:
    branches: [main]
    paths: ['TechConnect/**']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Login to ACR
        run: |
          echo ${{ secrets.ACR_PASSWORD }} | docker login \
            ${{ secrets.ACR_LOGIN_SERVER }} \
            -u ${{ secrets.ACR_USERNAME }} \
            --password-stdin
      
      - name: Build and push Docker image
        run: |
          cd TechConnect
          docker build -t ${{ secrets.ACR_LOGIN_SERVER }}/techconnect-api:${{ github.sha }} .
          docker tag ${{ secrets.ACR_LOGIN_SERVER }}/techconnect-api:${{ github.sha }} \
                     ${{ secrets.ACR_LOGIN_SERVER }}/techconnect-api:latest
          docker push ${{ secrets.ACR_LOGIN_SERVER }}/techconnect-api:${{ github.sha }}
          docker push ${{ secrets.ACR_LOGIN_SERVER }}/techconnect-api:latest
      
      - name: Deploy to App Service
        uses: azure/webapps-deploy@v2
        with:
          app-name: techconnect-api-prod
          publish-profile: ${{ secrets.AZURE_PUBLISH_PROFILE }}
          images: ${{ secrets.ACR_LOGIN_SERVER }}/techconnect-api:latest
```

---

## Monitoring & Management

### View Deployment Costs

```powershell
# Estimate costs
az billing usage list --output table

# Or use Azure Portal: https://portal.azure.com
```

### Scale App Service

```powershell
# Scale up (more powerful instance)
az appservice plan update `
  --name techconnect-plan `
  --resource-group techconnect-rg `
  --sku S1

# Scale out (more instances)
az appservice plan update `
  --name techconnect-plan `
  --resource-group techconnect-rg `
  --number-of-workers 3
```

### Configure Auto-Scale

```powershell
az monitor autoscale-settings create `
  --resource-group techconnect-rg `
  --resource-id /subscriptions/{subscriptionId}/resourceGroups/techconnect-rg/providers/Microsoft.Web/serverfarms/techconnect-plan `
  --resource-type "Microsoft.Web/serverfarms" `
  --name "auto-scale" `
  --min-count 1 `
  --max-count 5 `
  --count 2
```

---

## Troubleshooting

### Container fails to start

```powershell
# Check logs
az container logs --name <containerName> --resource-group techconnect-rg

# Common: Port mismatch, missing environment variables
# Solution: Verify Dockerfile EXPOSE and docker-compose env vars
```

### Image not found in ACR

```powershell
# Verify image exists
az acr repository list --name techconnectregistry

# Check credentials
az acr credential show --name techconnectregistry
```

### Web App shows "Bad Gateway"

```powershell
# Check app service logs
az webapp log tail --name techconnect-api-prod --resource-group techconnect-rg

# Verify port configuration
az webapp config show --name techconnect-api-prod --resource-group techconnect-rg
```

---

## Cleanup

```powershell
# Delete all resources
az group delete --name techconnect-rg --yes

# Or delete individual resources
az container delete --name techconnect-api-test --resource-group techconnect-rg --yes
az acr delete --name techconnectregistry --yes
az webapp delete --name techconnect-api-prod --resource-group techconnect-rg
```

---

## Quick Reference

| Stage | Deployment | Cost | Startup | Auto-Scale |
|-------|-----------|------|---------|-----------|
| 1 | Container Registry | $5/mo | N/A | N/A |
| 2 | Container Instances | ~$0.20/hr | 2-3 min | Manual |
| 3 | App Service (B1) | $12.75/mo | <1 min | Configured |
| 4 | Container Apps | ~$0.05/hr/core | <1 min | Auto (1-3 replicas) |

**Recommendation:** Start with Stage 2 (ACI) for testing, move to Stage 3 (App Service) for production.

---

**Last Updated:** January 2026  
**Next:** Monitor logs, set up alerts, configure custom domain

# Docker Rebuild & Deploy Instructions

**Status**: Ready for rebuild on another machine  
**Date**: February 4, 2026  
**Branch**: `main` (or your current branch)

---

## Overview

The System2-RAG frontend JavaScript was updated to properly handle API calls. The Azure Container App needs to be rebuilt with the new code.

### What Changed

**File Modified**: `static/script.js`

Changes made:
1. ✅ Added smart API URL detection function `getAPIBaseURL()`
2. ✅ Auto-detects environment (local vs Azure)
3. ✅ Fixed CORS mode configuration
4. ✅ Added console logging for debugging
5. ✅ Improved error handling

**Key Functions**:
```javascript
// Detects if running on localhost or Azure Container Apps
// Uses relative paths (/api) for cloud, absolute for local
function getAPIBaseURL() {
    const host = window.location.hostname;
    
    if (host === 'localhost' || host === '127.0.0.1') {
        return 'http://localhost:8001/api';
    }
    if (host.includes('azurecontainerapps.io') || host.includes('rag-system2')) {
        return '/api';
    }
    return `${protocol}//${host}/api`;
}
```

---

## Prerequisites on Rebuild Machine

Ensure the following are installed:
- ✅ Docker Desktop (latest)
- ✅ Azure CLI (`az` command)
- ✅ Git
- ✅ PowerShell (for deployment scripts)

### Verify Prerequisites

```powershell
docker --version
az --version
git --version
```

---

## Step-by-Step Rebuild Instructions

### Step 1: Clone/Pull the Repository

```powershell
# If cloning for first time
git clone https://github.com/YOUR_ORG/System2-RAG.git
cd System2-RAG

# If already cloned, pull latest
git pull origin main
```

### Step 2: Verify the Code Changes

Confirm `static/script.js` has the updated code:

```powershell
# Check for the new function
Select-String -Path "static/script.js" -Pattern "getAPIBaseURL"

# Output should show:
# static/script.js:3:function getAPIBaseURL() {
```

If not found, pull the latest code:
```powershell
git fetch origin
git pull origin main
```

### Step 3: Build the Docker Image

```powershell
# From the System2-RAG directory
cd System2-RAG

# Build the image
docker build -t rag-system2:latest .

# Verify the build succeeded
docker images | findstr rag-system2
```

**Expected output**:
```
REPOSITORY          TAG        IMAGE ID        CREATED        SIZE
rag-system2        latest     abc123def456    1 minute ago    250MB
```

### Step 4: Test the Image Locally (Optional)

```powershell
# Run the image locally
docker run -p 8000:8000 `
    -e OPENAI_API_KEY="your-key" `
    -e AZURE_SEARCH_ENDPOINT="your-endpoint" `
    -e AZURE_SEARCH_KEY="your-key" `
    rag-system2:latest

# Test the frontend
# Open browser: http://localhost:8000

# Test the API
curl http://localhost:8000/health
```

### Step 5: Login to Azure Container Registry

```powershell
# Login to ACR
az acr login --name acrpocdev

# Verify login
docker ps
```

### Step 6: Tag the Image for Registry

```powershell
# Tag the image with registry path
docker tag rag-system2:latest acrpocdev.azurecr.io/rag-system2:latest

# Verify the tag
docker images | findstr rag-system2
```

### Step 7: Push to Azure Container Registry

```powershell
# Push the image
docker push acrpocdev.azurecr.io/rag-system2:latest

# Verify it was pushed
az acr repository show --name acrpocdev --image rag-system2:latest
```

### Step 8: Update the Azure Container App

```powershell
# Trigger new deployment
az containerapp update `
    --name rag-system2-api `
    --resource-group rg-poc-accelerator `
    --image acrpocdev.azurecr.io/rag-system2:latest

# Wait 30-60 seconds for the container to restart
```

### Step 9: Verify the Deployment

```powershell
# Check container app status
az containerapp show `
    --name rag-system2-api `
    --resource-group rg-poc-accelerator `
    --query "properties.provisioningState" -o tsv

# Test the live endpoint
curl https://rag-system2-api.purplefield-e5b9c49f.eastus.azurecontainerapps.io/health

# Check the updated JavaScript
curl https://rag-system2-api.purplefield-e5b9c49f.eastus.azurecontainerapps.io/static/script.js | findstr "getAPIBaseURL"
```

**Expected output**: Should contain `function getAPIBaseURL() {`

---

## Automated Deployment Script

Instead of manual steps, use this PowerShell script:

```powershell
# save-this-as: deploy.ps1

param(
    [string]$ImageTag = "latest",
    [string]$RegistryName = "acrpocdev",
    [string]$ContainerAppName = "rag-system2-api",
    [string]$ResourceGroup = "rg-poc-accelerator"
)

Write-Host "Building Docker image..." -ForegroundColor Yellow
docker build -t rag-system2:$ImageTag .

Write-Host "Tagging image..." -ForegroundColor Yellow
docker tag rag-system2:$ImageTag $RegistryName.azurecr.io/rag-system2:$ImageTag

Write-Host "Logging into Azure Container Registry..." -ForegroundColor Yellow
az acr login --name $RegistryName

Write-Host "Pushing to registry..." -ForegroundColor Yellow
docker push $RegistryName.azurecr.io/rag-system2:$ImageTag

Write-Host "Updating container app..." -ForegroundColor Yellow
az containerapp update `
    --name $ContainerAppName `
    --resource-group $ResourceGroup `
    --image $RegistryName.azurecr.io/rag-system2:$ImageTag

Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host "Waiting for container to restart..."
Start-Sleep -Seconds 30

Write-Host "Testing endpoint..." -ForegroundColor Yellow
$response = Invoke-WebRequest -Uri "https://rag-system2-api.purplefield-e5b9c49f.eastus.azurecontainerapps.io/health" -UseBasicParsing
Write-Host "Status: $($response.StatusCode)" -ForegroundColor Green
```

**Usage**:
```powershell
.\deploy.ps1
```

---

## Files Modified

Here's what changed in the repository:

| File | Changes | Status |
|------|---------|--------|
| `static/script.js` | Added `getAPIBaseURL()` function, improved error handling | ✅ Ready |
| `Dockerfile` | No changes | ✅ OK |
| `app/main.py` | No changes | ✅ OK |
| `static/index.html` | No changes | ✅ OK |
| `static/style.css` | No changes | ✅ OK |

---

## Environment Variables Needed

Ensure these are set in the Container App (Azure Portal):

```
OPENAI_API_KEY = <your-openai-key>
AZURE_SEARCH_ENDPOINT = <your-search-endpoint>
AZURE_SEARCH_KEY = <your-search-key>
AZURE_OPENAI_ENDPOINT = <your-openai-endpoint>
AZURE_OPENAI_API_KEY = <your-openai-api-key>
```

---

## Troubleshooting

### Issue: Docker push fails
**Solution**: Login to ACR first
```powershell
az acr login --name acrpocdev
```

### Issue: Container app update fails
**Solution**: Verify the image exists in registry
```powershell
az acr repository show --name acrpocdev --image rag-system2:latest
```

### Issue: Container app still showing old code
**Solution**: Give it 2-3 minutes to restart, then hard refresh browser
```powershell
# Force browser cache clear:
Ctrl+Shift+Delete → Select "All time" → Clear data
# Hard refresh:
Ctrl+Shift+R
```

### Issue: Cannot login to Azure
**Solution**: Ensure you're authenticated
```powershell
az login
az account show
```

---

## Rollback (If Needed)

If the new version has issues, rollback to previous version:

```powershell
# Find previous image
az acr repository show-tags --name acrpocdev --repository rag-system2

# Rollback to previous tag
az containerapp update `
    --name rag-system2-api `
    --resource-group rg-poc-accelerator `
    --image acrpocdev.azurecr.io/rag-system2:previous-tag
```

---

## Verification Checklist

After deployment, verify:

- [ ] Container app updated (check Azure Portal)
- [ ] Container is running (Status: Running)
- [ ] Health check passing (curl /health → 200 OK)
- [ ] Frontend loads (https://rag-system2-api.../ returns HTML)
- [ ] JavaScript has new function (curl /static/script.js | grep getAPIBaseURL)
- [ ] Browser cache cleared (Ctrl+Shift+Delete)
- [ ] Page hard refreshed (Ctrl+Shift+R)
- [ ] Form submission works (no "failed to fetch" errors)
- [ ] Console shows API calls (F12 → Console tab)

---

## Quick Reference

```powershell
# Quick 4-step deployment
docker build -t rag-system2:latest .
docker tag rag-system2:latest acrpocdev.azurecr.io/rag-system2:latest
az acr login --name acrpocdev
docker push acrpocdev.azurecr.io/rag-system2:latest
az containerapp update --name rag-system2-api --resource-group rg-poc-accelerator --image acrpocdev.azurecr.io/rag-system2:latest
```

---

## Support

If you hit any issues during rebuild:

1. **Check logs**: `az containerapp logs show --name rag-system2-api --resource-group rg-poc-accelerator`
2. **Check status**: `az containerapp show --name rag-system2-api --resource-group rg-poc-accelerator`
3. **Verify code**: `curl https://rag-system2-api.purplefield-e5b9c49f.eastus.azurecontainerapps.io/static/script.js | head -20`

---

**Branch**: `main`  
**Last Updated**: February 4, 2026  
**Status**: Ready for rebuild

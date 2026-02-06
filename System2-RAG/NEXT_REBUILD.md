# 🚀 NEXT REBUILD - START HERE

**Status**: Ready for rebuild  
**Date**: February 4, 2026  
**Branch**: `master` ← **USE THIS BRANCH**  
**Last Update**: Source code added - app/main.py, static files, Dockerfile

---

## Quick Summary

The Azure Container App needs a **Docker rebuild** because the source code files were just added to GitHub. The critical fix (getAPIBaseURL function) is already in the code.

**Current Issue**: Container was deployed with old code  
**Solution**: Rebuild with files from this repository  
**Time Needed**: ~15 minutes  

---

## Prerequisites (Check First!)

```powershell
# Verify you have these installed
docker --version      # Docker Desktop
az --version          # Azure CLI
git --version         # Git
```

---

## Step-by-Step Process

### 1️⃣ Clone/Pull Latest Code

```powershell
# If cloning for first time:
git clone https://github.com/derricksobrien/poc-accelerator.git
cd poc-accelerator

# If already cloned, get latest:
git pull origin master
cd System2-RAG
```

**✅ Verify you're on master branch:**
```powershell
git branch --show-current
# Output should be: master
```

---

### 2️⃣ Verify the Fix is Present

The critical fix must be in the code:

```powershell
# Check for the getAPIBaseURL function
Select-String -Path "static/script.js" -Pattern "getAPIBaseURL"

# Should output:
# static/script.js:3:function getAPIBaseURL() {
```

**If NOT found**: 
- Something's wrong, check git status and pull again
- The repo should have this function - don't proceed without it

**If found**: ✅ Continue to step 3

---

### 3️⃣ Build Docker Image

```powershell
cd System2-RAG

# Build the image
docker build -t rag-system2:latest .

# Verify build succeeded
docker images | Select-String "rag-system2"
```

---

### 4️⃣ Tag for Azure Container Registry

```powershell
# Use the correct registry (with admin enabled)
docker tag rag-system2:latest acrragsystem202041846.azurecr.io/rag-system2:latest

# Verify tag
docker images | Select-String "acrragsystem202041846"
```

---

### 5️⃣ Login to Azure Container Registry

```powershell
az acr login --name acrragsystem202041846
```

---

### 6️⃣ Push to Azure

```powershell
docker push acrragsystem202041846.azurecr.io/rag-system2:latest

# Wait for ~5-10 minutes for upload to complete
```

---

### 7️⃣ Update Azure Container App

```powershell
az containerapp update \
  --name rag-system2-api \
  --resource-group rg-poc-accelerator \
  --image acrragsystem202041846.azurecr.io/rag-system2:latest

# Wait for deployment to complete (~2 minutes)
```

---

### 8️⃣ Verify Deployment

```powershell
# Check container status
az containerapp show \
  --name rag-system2-api \
  --resource-group rg-poc-accelerator \
  --query "properties.runningStatus"

# Should show: Running
```

---

### 9️⃣ Test in Browser

Clear cache and test:

```
1. Open browser: https://rag-system2-api.purplefield-e5b9c49f.eastus.azurecontainerapps.io
2. Hard refresh: Ctrl+Shift+Delete (clear all cache)
3. Reload: Ctrl+Shift+R
4. Test the form - should NO LONGER show "failed to fetch"
5. Open DevTools (F12) → Console tab
6. Should see: [API] Azure environment detected, using relative path: /api
```

---

## What Changed

### Files Added to Repository
- ✅ `app/main.py` - FastAPI backend
- ✅ `static/script.js` - **Frontend with getAPIBaseURL() fix**
- ✅ `static/index.html` - Web interface
- ✅ `static/style.css` - Styling
- ✅ `Dockerfile` - Container configuration
- ✅ `requirements.txt` - Dependencies

### The Critical Fix
The JavaScript now detects environment automatically:
```javascript
function getAPIBaseURL() {
    const host = window.location.hostname;
    
    // Local development
    if (host === 'localhost' || host === '127.0.0.1') {
        return 'http://localhost:8000/api';
    }
    
    // Azure Container Apps
    if (host.includes('azurecontainerapps.io')) {
        return '/api';  // ← THIS FIX (relative path)
    }
    
    return `${protocol}//${host}/api`;
}
```

---

## Troubleshooting

### Docker build fails
```powershell
# Check you're in System2-RAG directory
pwd
# Should show: .../System2-RAG

# Clear Docker cache
docker system prune -a
docker build -t rag-system2:latest .
```

### Cannot login to registry
```powershell
# Verify correct registry name
az acr list --output table
# Find: acrragsystem202041846 (with admin ENABLED)

# Try login again
az acr login --name acrragsystem202041846
```

### Container still has old code
- Wait 60+ seconds after update
- Hard refresh browser (Ctrl+Shift+Delete then Ctrl+Shift+R)
- Check container logs: `az containerapp logs ...`

### "failed to fetch" error still appears
- Check browser console (F12 → Console)
- Should show `[API] Azure environment detected`
- If shows `localhost`, container has old code - rebuild again

---

## Key Information

**Azure Container App**: `rag-system2-api`  
**Resource Group**: `rg-poc-accelerator`  
**Region**: `eastus`  
**Public URL**: `https://rag-system2-api.purplefield-e5b9c49f.eastus.azurecontainerapps.io`  

**Git Repository**: `https://github.com/derricksobrien/poc-accelerator.git`  
**Branch to Use**: `master` ← **IMPORTANT**  
**Source Location in Repo**: `System2-RAG/` folder  

**Build Registry**: `acrragsystem202041846.azurecr.io` (admin enabled)  
**Old Registry**: `acrragsystem202041841.azurecr.io` (don't use - no admin)  

---

## Success Checklist

After deployment, verify:

- [ ] Docker image built successfully
- [ ] Image pushed to registry
- [ ] Container App updated
- [ ] Container status shows "Running"
- [ ] Container logs show no errors
- [ ] Browser loads the page (HTTP 200)
- [ ] JavaScript loads without console errors
- [ ] Console shows: `[API] Azure environment detected, using relative path: /api`
- [ ] Form submission works (no "failed to fetch" error)
- [ ] POC generation returns results
- [ ] Search functionality works
- [ ] All 4 tabs respond correctly

---

## Questions?

- Check the detailed instructions in `REBUILD_INSTRUCTIONS.md`
- Review `DEPLOYMENT_VERIFICATION_REPORT.md` for testing details
- Check `GITHUB_PUSH_GUIDE.md` for git operations

**This should take ~15-20 minutes total.**

Good luck! 🚀

---

*Last Updated: February 4, 2026*  
*Status: Ready for rebuild*  
*Branch: master*

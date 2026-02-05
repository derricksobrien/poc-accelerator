# Azure App Service Deployment - Staged Steps

**Status**: ✅ Ready to Deploy  
**Method**: Azure App Service (no containers, no ACR)  
**Time**: 10-15 minutes  
**Cost**: ~$13/month (B1 tier) → $50/month (B3 tier)

---

## 🎯 Deployment Overview

The deployment script (`deploy_app_service.py`) runs **7 stages** in sequence. You can run them all at once, or one at a time to verify each step.

```
Stage 1: Check Prerequisites
   ↓
Stage 2: Create Resource Group
   ↓
Stage 3: Create App Service Plan
   ↓
Stage 4: Create Web App
   ↓
Stage 5: Deploy Code
   ↓
Stage 6: Configure Settings
   ↓
Stage 7: Verify Deployment
```

---

## 📋 Pre-Deployment Checklist

Before starting, verify:

- [ ] You have an Azure subscription
- [ ] Azure CLI installed: `az --version`
- [ ] You're authenticated: `az login`
- [ ] You're in System3-RAG directory: `cd System3-RAG`
- [ ] All tests pass: `pytest test_all_endpoints.py -v` (optional but recommended)

---

## 🚀 **STAGE 1: Check Prerequisites**

**What it does:** Verifies Azure CLI is installed and you're logged in

**Run this:**
```bash
python deploy_app_service.py --stage 1 --resource-group <your-rg-name>
```

**Example:**
```bash
python deploy_app_service.py --stage 1 --resource-group contoso-ai-rg
```

**Expected output:**
```
✅ Azure CLI installed
✅ Authenticated with Azure
✅ Current subscription: Your Subscription Name
```

**If fails:**
```bash
# Not authenticated?
az login

# CLI not installed?
# Windows: Download from https://aka.ms/azcliinstaller
```

---

## 🚀 **STAGE 2: Create Resource Group**

**What it does:** Creates (or verifies) the Azure resource group where everything lives

**Run this:**
```bash
python deploy_app_service.py --stage 2 --resource-group <your-rg-name> --region eastus
```

**Expected output:**
```
✅ Resource group 'contoso-ai-rg' created in eastus
   (or "already exists" if already created)
```

**Choose your region:**
- `eastus` - Default
- `westus2` - West Coast
- `northeurope` - Europe
- `southeastasia` - Asia
- `canadacentral` - Canada

---

## 🚀 **STAGE 3: Create App Service Plan**

**What it does:** Creates the hosting plan that runs your app

**Run this:**
```bash
python deploy_app_service.py --stage 3 --resource-group <your-rg-name>
```

**Expected output:**
```
✅ App Service Plan created (B1 tier - $13/mo)
```

**Pricing:**
- B1 (Basic) = $13/month - Good for testing/demo
- B2 (Basic) = $26/month - Small production
- B3 (Basic) = $52/month - Medium production
- S1 (Standard) = $50/month - Auto-scaling

---

## 🚀 **STAGE 4: Create Web App**

**What it does:** Creates the actual web app instance running Python 3.10

**Run this:**
```bash
python deploy_app_service.py --stage 4 --resource-group <your-rg-name> --name system3-rag
```

**Expected output:**
```
✅ Web App created
🌐 Web App URL: https://system3-rag.azurewebsites.net
```

**Note:** Save the URL - you'll use this to access your app

---

## 🚀 **STAGE 5: Deploy Code**

**What it does:** Uploads System3-RAG code to Azure and installs dependencies

**Requirements:**
- Must be in System3-RAG directory
- `requirements.txt` must exist

**Run this:**
```bash
python deploy_app_service.py --stage 5 --resource-group <your-rg-name> --name system3-rag
```

**Expected output:**
```
Deploying code to system3-rag...
✅ Code deployed successfully
```

**What happens in background:**
1. Uploads all Python files
2. Runs `pip install -r requirements.txt`
3. Sets up the app
4. Takes 2-3 minutes

---

## 🚀 **STAGE 6: Configure Settings**

**What it does:** Sets environment variables and startup command

**Run this:**
```bash
python deploy_app_service.py --stage 6 --resource-group <your-rg-name> --name system3-rag
```

**Expected output:**
```
✅ Application settings configured
```

**Configures:**
- Startup command: `gunicorn app.main:app`
- Environment variables: HOST, PORT, LOG_LEVEL, SESSION_TIMEOUT
- Python runtime: 3.10

---

## 🚀 **STAGE 7: Verify Deployment**

**What it does:** Checks if the app is running and responds to health check

**Run this:**
```bash
python deploy_app_service.py --stage 7 --resource-group <your-rg-name> --name system3-rag
```

**Expected output:**
```
✅ Application is responding!

🎉 Deployment successful!

📌 Access your app at: https://system3-rag.azurewebsites.net
```

**If it doesn't respond immediately:**
- ⏳ App is still starting (takes 1-2 minutes)
- Check back in a moment
- Monitor via Azure Portal

---

## 🎯 **Run All Stages at Once (Recommended)**

Instead of running each stage individually, you can run them all:

```bash
python deploy_app_service.py \
  --resource-group contoso-ai-rg \
  --name system3-rag \
  --region eastus
```

Script will:
1. ✅ Check prerequisites
2. ✅ Create resource group
3. ✅ Create App Service Plan
4. ✅ Create Web App
5. ✅ Deploy code (takes 2-3 min)
6. ✅ Configure settings
7. ✅ Verify
8. ✅ Show you the URL

**Total time: 10-15 minutes**

---

## 🌐 **Access Your App**

Once deployed, your app is live at:
```
https://system3-rag.azurewebsites.net
```

### What's running:
- **FastAPI Backend**: Runs on port 8000 (internal)
- **Streamlit UI**: Accessible at the main URL

### Test endpoints:
```bash
# Health check
curl https://system3-rag.azurewebsites.net/health

# API documentation (not available in App Service by default)
# https://system3-rag.azurewebsites.net/docs (might not work due to Streamlit)

# Generate POC (via curl)
curl -X POST https://system3-rag.azurewebsites.net/api/rag/generate-poc \
  -H "Content-Type: application/json" \
  -d '{"session_id":"test","title":"POC","solution_area":"AI","complexity":"L400","requirements":"Test"}'
```

---

## 🔧 If Something Goes Wrong

### App won't start
```bash
# Check logs
az webapp log tail -n system3-rag -g <resource-group>

# Common issues:
# - Missing dependency → pip install -r requirements.txt
# - Wrong startup command → Check stage 6 settings
# - Python version mismatch → Already set to 3.10
```

### Deployment stuck
```bash
# Check deployment status
az webapp show -n system3-rag -g <resource-group> --query state

# Restart the app
az webapp restart -n system3-rag -g <resource-group>
```

### Too slow / need more power
```bash
# Scale up the plan
az appservice plan update \
  -n system3-rag-plan \
  -g <resource-group> \
  --sku B2  # or S1 for auto-scaling
```

---

## 🔐 **Next: Add Azure AI Credentials (Optional)**

If you want the real agent (not mock):

```bash
# Set Azure credentials
az webapp config appsettings set \
  -n system3-rag \
  -g <resource-group> \
  --settings \
    AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/" \
    AZURE_OPENAI_KEY="sk-your-key"

# Restart app
az webapp restart -n system3-rag -g <resource-group>
```

Then the app will use real Azure AI Foundry agent instead of mocks!

---

## 📊 **Monitoring & Stats**

```bash
# View real-time logs
az webapp log tail -n system3-rag -g <resource-group>

# Get resource metrics
az webapp show -n system3-rag -g <resource-group> --query '{state:state,url:defaultHostName,sku:appServicePlanId}'

# View all app settings
az webapp config appsettings list -n system3-rag -g <resource-group>

# Check quotas
az appservice plan show -n system3-rag-plan -g <resource-group>
```

---

## ✅ **After Deployment - Next Steps**

Once app is live (Stage 7 passes):

### 1. **Test the web interface**
   - Visit: https://system3-rag.azurewebsites.net
   - Try the 5 tabs
   - Generate a mock POC
   - Search for solutions

### 2. **Run tests against live deployment**
   ```bash
   # Point tests at deployed app
   export API_BASE_URL="https://system3-rag.azurewebsites.net"
   pytest test_all_endpoints.py -v
   ```

### 3. **Configure real agent** (if you have Azure AI Foundry)
   - Run: `python setup_azure_agent.py ...`
   - Get credentials
   - Add to app settings (see above)

### 4. **Monitor performance**
   - Check logs: `az webapp log tail ...`
   - Monitor metrics in Azure Portal
   - Scale up if needed

### 5. **Custom domain** (optional)
   ```bash
   # Map your domain (e.g., system3-rag.mycompany.com)
   az webapp config hostname add \
     -n system3-rag \
     --custom-hostname system3-rag.mycompany.com
   ```

---

## 🎓 **Understanding the Architecture**

```
Your Computer
    ↓ (you visit browser)
    ↓
Azure App Service (system3-rag.azurewebsites.net)
    ├─ FastAPI Backend (port 8000 - internal)
    │   ├─ Session management
    │   ├─ POC generation
    │   ├─ Search
    │   └─ Tools (RBAC, deployment, IaC)
    │
    └─ Streamlit Frontend (port 8501 - exposed)
        ├─ Generate POC tab
        ├─ Agent Chat tab
        ├─ Search Solutions tab
        ├─ History tab
        └─ System Status tab
```

**Streamlit** talks to **FastAPI** backend internally (same container)

---

## 💾 **Cleanup (Delete Everything)**

If you want to remove the deployment:

```bash
# Delete everything (careful!)
az group delete -n <resource-group> --yes --no-wait
```

This deletes:
- Web app
- App Service Plan
- Resource Group
- Everything else

**Cost drops to $0 immediately**

---

## 📞 **Support Commands**

```bash
# Check if app is running
curl -I https://system3-rag.azurewebsites.net/health

# View deployment history
az webapp deployment list -n system3-rag -g <resource-group>

# Get app logs (last 100 lines)
az webapp log download -n system3-rag -g <resource-group> --log-name gunicorn

# Restart app
az webapp restart -n system3-rag -g <resource-group>

# SSH into container (advanced)
az webapp create-remote-connection -n system3-rag -g <resource-group>
```

---

## 🚀 **Ready to Deploy?**

### Run all stages at once:
```bash
cd c:\Users\derri\Code\techconnect_all\System3-RAG

python deploy_app_service.py \
  --resource-group contoso-ai-rg \
  --name system3-rag \
  --region eastus
```

### Or run stages individually:
```bash
python deploy_app_service.py --stage 1 --resource-group <rg>
python deploy_app_service.py --stage 2 --resource-group <rg>
python deploy_app_service.py --stage 3 --resource-group <rg>
# ... etc (check progress at each stage)
```

**Let's go! 🚀**

---

*Azure App Service Deployment Guide*  
*February 2026*

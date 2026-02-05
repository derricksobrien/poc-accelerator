# 🚀 Quick Reference - Deploy TechConnect to Azure

## ONE-LINER DEPLOYMENT

### Deploy to Container Instances (NOW - 3 minutes)
```powershell
cd c:\Users\mokoj\code\TechConnect2\TechConnect; .\deploy-azure-aci.ps1
```

### Deploy to App Service (After Quota - 5-10 minutes)
```powershell
cd c:\Users\mokoj\code\TechConnect2\TechConnect; .\deploy-azure.ps1
```

---

## QUICK STATUS

| Item | Status |
|------|--------|
| Azure CLI | ✅ Installed (v2.82.0) |
| Docker Image | ✅ Built (213 MB) |
| Container Registry | ✅ Created (techconnectregistry.azurecr.io) |
| Image in Registry | ✅ Uploaded (latest, v1.0.0) |
| ACI Deployment | ✅ Script Ready |
| App Service | ⏳ Script Ready (needs quota) |
| Documentation | ✅ Complete |

---

## DEPLOYMENT OPTIONS

### Option A: Container Instances ⭐
- **Time**: 3 minutes
- **Cost**: $0.20/hour (pay-as-you-go)
- **Quota**: Not needed
- **Best for**: Testing, demos
- **Command**: `.\deploy-azure-aci.ps1`

### Option B: App Service
- **Time**: 5-10 minutes
- **Cost**: $12.75+/month
- **Quota**: Required (1 vCPU)
- **Best for**: Production
- **Command**: `.\deploy-azure.ps1`
- **Action**: First request quota, then run script

### Option C: Different Region
- **Time**: 5 minutes
- **Cost**: Same as Option B
- **Quota**: Maybe
- **Regions**: westus, westus2, centralus, southcentralus
- **Action**: Edit region in deploy-azure.ps1

---

## KEY COMMANDS

### Deploy
```powershell
.\deploy-azure-aci.ps1          # Deploy to ACI now
.\deploy-azure.ps1              # Deploy to App Service (after quota)
```

### Check Status
```powershell
$azPath = "C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"
& $azPath acr repository list --name techconnectregistry
& $azPath container show --name techconnect-api-prod --resource-group techconnect-rg
```

### View Logs
```powershell
# For ACI
& $azPath container logs --name techconnect-api-prod --resource-group techconnect-rg --follow

# For App Service
& $azPath webapp log tail --name techconnect-api-prod --resource-group techconnect-rg
```

### Test Endpoints
```bash
curl https://<YOUR-APP-URL>/health
curl https://<YOUR-APP-URL>/accelerators
curl -X POST https://<YOUR-APP-URL>/context -H "Content-Type: application/json" -d '{"scenario_title":"test","num_results":1}'
```

### Stop/Delete
```powershell
# Stop ACI (pause billing)
& $azPath container stop --name techconnect-api-prod --resource-group techconnect-rg

# Delete ACI (remove completely)
& $azPath container delete --name techconnect-api-prod --resource-group techconnect-rg --yes

# Stop App Service
& $azPath webapp stop --name techconnect-api-prod --resource-group techconnect-rg

# Delete everything
& $azPath group delete --name techconnect-rg --yes
```

---

## TROUBLESHOOTING

### "Quota not available"
```
→ Use ACI (Option A) instead
→ OR request quota at: portal.azure.com/#view/.../QuotaMenuBlade
```

### "Container won't start"
```
→ Check logs: az container logs --name techconnect-api-prod
→ Check status: az container show --name techconnect-api-prod
```

### "Image not found"
```
→ List images: az acr repository list --name techconnectregistry
→ List tags: az acr repository show-tags --name techconnectregistry --repository techconnect-api
```

### "Endpoint not responding"
```
→ App Service takes 5-10 minutes to start
→ ACI takes 2-3 minutes to start
→ Wait and try again, check logs
```

---

## COST SNAPSHOT

| Option | Startup | Monthly | Per Hour |
|--------|---------|---------|----------|
| ACI (24/7) | 2-3 min | ~$150 | $0.20 |
| App Service | 5-10 min | $12.75 | $0.53 |
| Container Apps | 1-2 min | ~$36 | $0.05 |

**Cheapest**: App Service ($12.75/month)  
**Quickest**: Container Apps (1-2 min)  
**Most Flexible**: ACI (pay-as-you-go)

---

## WHAT YOU GET

After deployment:
- ✅ Public HTTP(S) endpoint
- ✅ API accessible from anywhere
- ✅ Logs streaming
- ✅ Auto-restart on failure
- ✅ Scalable architecture

---

## CRITICAL FILES

| File | Purpose |
|------|---------|
| `deploy-azure-aci.ps1` | Deploy to ACI (use now) |
| `deploy-azure.ps1` | Deploy to App Service (after quota) |
| `AZURE_READY_TO_DEPLOY.md` | Full quick start |
| `DEPLOYMENT_ARCHITECTURE.md` | Visual diagrams |
| `AZURE_DEPLOYMENT.md` | Manual steps |
| `SESSION_SUMMARY.md` | Session notes |

---

## NEXT STEPS

1. **Right Now**
   ```powershell
   .\deploy-azure-aci.ps1
   ```

2. **In 3 Minutes**
   - Get your app URL from script output
   - Test: `curl https://<YOUR-APP-URL>/health`

3. **Optional Later**
   - Request App Service quota
   - Migrate to App Service if you want production-grade
   - Set up GitHub Actions CI/CD

---

## SUCCESS CHECKLIST

- [ ] Azure CLI installed (`az --version` shows v2.50+)
- [ ] Logged into Azure (`az account show` shows subscription)
- [ ] Docker image in registry (`az acr repository list`)
- [ ] Deployment script chosen (ACI or App Service)
- [ ] Script executed successfully
- [ ] App URL obtained from output
- [ ] Health endpoint responds (`curl .../health`)
- [ ] All endpoints working

---

## IMPORTANT REMINDERS

⚠️ **Stop unused deployments to save costs!**
```powershell
# ACI: Stop when not needed
az container stop --name techconnect-api-prod --resource-group techconnect-rg

# App Service: Stop when not needed
az webapp stop --name techconnect-api-prod --resource-group techconnect-rg
```

💰 **App Service costs money even when idle, ACI only costs when running**

🔐 **Docker image is in registry forever, delete resource group to delete everything**

---

## SUPPORT

- **Azure Issues**: [Azure Portal](https://portal.azure.com) 
- **Quota Requests**: [Quotas Page](https://portal.azure.com/#view/Microsoft_Azure_Capacity/QuotaMenuBlade)
- **Documentation**: See files in current directory
- **TechConnect API**: See `.github/copilot-instructions.md`

---

**Status**: Ready to deploy ✅  
**Action**: Run deployment script  
**Time to Deploy**: 3 minutes (ACI) or 10 minutes (App Service + quota)

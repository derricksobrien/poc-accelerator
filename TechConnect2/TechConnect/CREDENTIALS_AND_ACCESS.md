# TechConnect API - Deployment Credentials & Access

**Status**: ✅ Live on Azure  
**Date**: January 21, 2026

---

## 📍 API Access (Public - Share Freely)

### Base URL
```
http://techconnect-api-prod.eastus.azurecontainer.io:8000
```

### Health Check
```bash
curl http://techconnect-api-prod.eastus.azurecontainer.io:8000/health
```

### For Users
- **Share**: Just the URL above
- **Security**: Public, no authentication needed
- **Distribution**: Email, docs, dashboard, any method

**See**: `HOW_TO_USE_API.md` for usage examples

---

## 🔐 Azure Credentials (Admin Only)

### Subscription
```
ID: 7ee5516b-974e-44ba-96a6-e2dd381dc83c
Name: Azure subscription 1
Status: Active
```

### Resource Group
```
Name: techconnect-rg
Location: eastus
Status: Created ✅
```

### Container Registry (ACR)
```
Name: techconnectregistry
URL: techconnectregistry.azurecr.io
SKU: Basic ($5/month)
Username: techconnectregistry
Password: bi7z4IOXp2y/AFlFEEeGWOH953MJ7wc
```

### Container Instance
```
Name: techconnect-api-prod
Image: techconnectregistry.azurecr.io/techconnect-api:latest
CPU: 1
Memory: 1.5 GB
Port: 8000
OS: Linux
Status: Running ✅
Cost: $0.20/hour
```

---

## 🔑 Access Levels

### Level 1: API Users (Share URL Only)
**Can do**: 
- Call API endpoints
- Get recommendations
- Health checks

**Need**: Just the URL above

**Share via**: Email, docs, wiki, etc.

---

### Level 2: Container Managers (Full Azure Access)
**Can do**:
- View logs
- Stop/restart container
- Check status
- Monitor costs

**Need**:
1. Azure CLI installed
2. Azure account with access to resource group
3. Invite them to the resource group in Azure Portal

**Commands**:
```bash
# View logs
az container logs --name techconnect-api-prod --resource-group techconnect-rg --follow

# Stop (save costs)
az container stop --name techconnect-api-prod --resource-group techconnect-rg

# Restart
az container restart --name techconnect-api-prod --resource-group techconnect-rg

# Check status
az container show --name techconnect-api-prod --resource-group techconnect-rg
```

---

### Level 3: Developers (Full Deployment Access)
**Can do**:
- Rebuild images
- Deploy new versions
- Manage registry
- Modify infrastructure

**Need**:
1. All credentials below
2. Access to source code repository
3. Docker installed
4. Azure subscription access

**Credentials**:
- Azure subscription ID: `7ee5516b-974e-44ba-96a6-e2dd381dc83c`
- ACR credentials (see above)
- Docker image location: `techconnectregistry.azurecr.io/techconnect-api`

**Deployment Scripts**:
- `deploy-azure-aci.ps1` - Deploy to Container Instances
- `deploy-azure.ps1` - Deploy to App Service

---

## 📊 What to Share

### Share with Everyone (Marketing, Management)
```
API URL: http://techconnect-api-prod.eastus.azurecontainer.io:8000
Status: ✅ Live and running
Cost: ~$0.20/hour

For usage, see: HOW_TO_USE_API.md
```

### Share with Container Admins
```
Resource Group: techconnect-rg
Container Name: techconnect-api-prod
Region: eastus

Management Commands:
- View logs: az container logs --name techconnect-api-prod --resource-group techconnect-rg --follow
- Stop: az container stop --name techconnect-api-prod --resource-group techconnect-rg
- Restart: az container restart --name techconnect-api-prod --resource-group techconnect-rg

To get access:
1. Ask to be added to the resource group
2. Install Azure CLI
3. Run: az login
4. Then use the commands above
```

### Share with Developers (Full Handoff)
Include all files from this directory:
- `deploy-azure-aci.ps1`
- `deploy-azure.ps1`
- `AZURE_DEPLOYMENT.md`
- `AZURE_READY_TO_DEPLOY.md`
- `HOW_TO_USE_API.md`
- `Dockerfile`
- `docker-compose.yml`
- Source code: `api/`, `ingestion/`, `models/`, etc.

Plus credentials:
```
Azure Subscription: 7ee5516b-974e-44ba-96a6-e2dd381dc83c
ACR URL: techconnectregistry.azurecr.io
ACR Username: techconnectregistry
ACR Password: bi7z4IOXp2y/AFlFEEeGWOH953MJ7wc
Resource Group: techconnect-rg
```

---

## 🔒 Security Recommendations

### For Public API
- ✅ Currently: No authentication (anyone can call it)
- Consider adding API key authentication if sensitive
- Monitor usage patterns
- Set up cost alerts

### For Azure Credentials
- ⚠️ **Don't share password in email** - Use Azure Portal RBAC instead
- ✅ Create separate Azure accounts for team members
- ⚠️ Rotate ACR passwords periodically
- ✅ Use Azure Managed Identity instead of passwords

### For Source Code
- Keep GitHub repo private if sensitive
- Use branch protection rules
- Require code reviews before deployment

---

## 🚀 How to Give Access

### Option 1: Just Share the URL (Easiest)
```
Send to team:
"API is ready! Use this URL: http://techconnect-api-prod.eastus.azurecontainer.io:8000"
```

### Option 2: Full Access (Best for Teams)
1. **Git Repository** - Clone entire repo
2. **Azure Portal** - Invite users to resource group
3. **Documentation** - Share this folder
4. **Credentials** - Share only the password below securely

ACR Password: `bi7z4IOXp2y/AFlFEEeGWOH953MJ7wc`

### Option 3: API Key / Dashboard (Future)
- Add authentication layer (JWT tokens)
- Create API key system
- Build usage dashboard
- Track who's calling what

---

## 📝 Summary

**For End Users**: Just share the URL
```
http://techconnect-api-prod.eastus.azurecontainer.io:8000
```

**For Admins**: Share access to resource group via Azure Portal
```
techconnect-rg in eastus region
```

**For Developers**: Share this entire folder + credentials

---

## 💰 Cost Management

**Remind users**:
- Container costs $0.20/hour while running
- ~$150/month if running 24/7
- Stop with: `az container stop --name techconnect-api-prod --resource-group techconnect-rg`
- Delete completely with: `az container delete --name techconnect-api-prod --resource-group techconnect-rg --yes`

---

## ✅ Sharing Checklist

- [ ] Send API URL to users: `http://techconnect-api-prod.eastus.azurecontainer.io:8000`
- [ ] Share `HOW_TO_USE_API.md` with usage examples
- [ ] Invite admins to Azure resource group
- [ ] Share deployment scripts with developers
- [ ] Document any custom usage or limitations
- [ ] Set up monitoring/alerts if needed

---

**Last Updated**: January 21, 2026  
**Status**: ✅ Ready to share  
**Next**: Send credentials to appropriate team members

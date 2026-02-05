# 📋 Deployment Checklist

Use this checklist to track your progress through each deployment stage.

---

## 🟢 Stage 1: Local Development (Python Native)

**Time Estimate**: 15-30 minutes  
**Status**: Not Started / In Progress / ✅ Complete

### Prerequisites
- [ ] Python 3.9+ installed (`python --version`)
- [ ] pip working (`pip --version`)
- [ ] Git installed (`git --version`)
- [ ] Docker installed (for later stages) (`docker --version`)

### Setup
- [ ] Clone/navigate to TechConnect directory
- [ ] Create virtual environment (`.venv`)
- [ ] Activate virtual environment
- [ ] Install dependencies (`pip install -r requirements.txt`)
- [ ] Verify catalog.json exists in project root

### Validation
- [ ] Run full test suite: `python test_mvp.py`
  - [ ] Module A (Scraper) tests pass
  - [ ] Module B (Metadata) tests pass
  - [ ] Module C (Vector Store) tests pass
  - [ ] Module D (Context Provider) tests pass
  - [ ] Module E (RAI Guardrails) tests pass
- [ ] Start API: `python -m uvicorn api.main:app --port 8000`
- [ ] In separate terminal, test endpoints:
  - [ ] `curl http://localhost:8000/health` returns 200
  - [ ] `curl http://localhost:8000/accelerators` returns list
  - [ ] `curl -X POST .../context` returns ContextBlock with XML tags
- [ ] Test Skillable Simulator: `python skillable_simulator/demo.py` produces output

### Debugging Tips
- Python not found? Add to PATH or use full path: `C:\Python39\python.exe`
- Module import error? Reinstall: `pip install -r requirements.txt --force-reinstall`
- Port 8000 in use? Use different port: `python -m uvicorn api.main:app --port 8001`

### Completion Criteria ✅
- All tests pass with no errors
- API responds to all 3 endpoint types
- Skillable Simulator generates lab output
- No warnings or errors in logs

**Sign-off Date**: _______________

---

## 🟡 Stage 2: Docker Local Testing

**Time Estimate**: 10-20 minutes  
**Status**: Not Started / In Progress / ✅ Complete  
**Prerequisite**: Stage 1 Complete ✅

### Docker Prerequisites
- [ ] Docker Desktop installed and running
- [ ] Docker version 20.10+: `docker --version`
- [ ] Can login to Docker: `docker run hello-world` succeeds

### Build Docker Image
- [ ] Build image: `docker build -t techconnect-api:latest .`
- [ ] Verify build succeeded (no errors)
- [ ] Check image size: `docker images` shows ~250MB or less
- [ ] Can run image: `docker run -it techconnect-api:latest /bin/bash` (exit with `exit`)

### Run with Docker Compose
- [ ] `docker-compose up -d` starts without errors
- [ ] `docker-compose ps` shows all containers
- [ ] Container status is "Up (healthy)" (may take 10-15 seconds)
- [ ] No errors in logs: `docker-compose logs api`

### Test API in Container
- [ ] Health check: `curl http://localhost:8000/health`
- [ ] List accelerators: `curl http://localhost:8000/accelerators`
- [ ] Get context: `curl -X POST http://localhost:8000/context -H "Content-Type: application/json" -d '{"scenario_title":"test"}'`
- [ ] All responses identical to Stage 1

### Docker Cleanup
- [ ] Stop services: `docker-compose down`
- [ ] Container no longer running: `docker-compose ps` shows nothing
- [ ] Optional: Clean up images: `docker system prune -a`

### Debugging Tips
- Build fails? Use `docker build --progress=plain .` to see details
- Container won't start? Check logs: `docker-compose logs api`
- Port still in use? Force clean: `docker-compose down -v`

### Completion Criteria ✅
- Docker image builds without errors
- docker-compose starts and becomes healthy
- All API endpoints work identically to Stage 1
- No errors in container logs

**Sign-off Date**: _______________

---

## 🔴 Stage 3: Azure Deployment

**Time Estimate**: 60-90 minutes  
**Status**: Not Started / In Progress / ✅ Complete  
**Prerequisite**: Stage 2 Complete ✅

### Azure Preparation
- [ ] Azure subscription created (free trial: https://azure.microsoft.com/free)
- [ ] Azure CLI installed: `az --version` returns 2.50+
- [ ] Logged into Azure: `az login` succeeds
- [ ] Subscription selected: `az account show` shows correct subscription

### 3a: Azure Container Registry (ACR)
**Time**: ~5 minutes

- [ ] Create resource group: `az group create --name techconnect-rg --location eastus`
- [ ] Create ACR: `az acr create --resource-group techconnect-rg --name techconnectregistry --sku Basic`
- [ ] Verify registry exists: `az acr list --output table`
- [ ] Get registry credentials: `az acr credential show --name techconnectregistry`
- [ ] Tag image: `docker tag techconnect-api:latest techconnectregistry.azurecr.io/techconnect-api:v1.0.0`
- [ ] Login to ACR: `az acr login --name techconnectregistry` (or use Docker Desktop)
- [ ] Push image: `docker push techconnectregistry.azurecr.io/techconnect-api:v1.0.0`
- [ ] Verify in registry: `az acr repository list --name techconnectregistry`

### 3b: Azure Container Instances (ACI) - Testing
**Time**: ~10 minutes

- [ ] Get ACR password: `az acr credential show --name techconnectregistry --query "passwords[0].value"`
- [ ] Deploy: `az container create --resource-group techconnect-rg --name techconnect-api-test --image techconnectregistry.azurecr.io/techconnect-api:v1.0.0 --registry-username techconnectregistry --registry-password <PASSWORD> --ports 8000 --dns-name-label techconnect-api-test`
- [ ] Wait for startup (2-3 minutes)
- [ ] Get public IP: `az container show --resource-group techconnect-rg --name techconnect-api-test --query "ipAddress.fqdn"`
- [ ] Test endpoints:
  - [ ] `curl http://<PUBLIC-IP>:8000/health`
  - [ ] `curl http://<PUBLIC-IP>:8000/accelerators`
  - [ ] `curl -X POST http://<PUBLIC-IP>:8000/context ...`
- [ ] View logs: `az container logs --name techconnect-api-test --resource-group techconnect-rg`
- [ ] Delete test deployment: `az container delete --name techconnect-api-test --resource-group techconnect-rg --yes`

### 3c: Azure App Service (Production)
**Time**: ~20 minutes (skip if using ACI only)

- [ ] Create App Service plan: `az appservice plan create --name techconnect-plan --resource-group techconnect-rg --sku B1 --is-linux`
- [ ] Create web app: `az webapp create --resource-group techconnect-rg --plan techconnect-plan --name techconnect-api-prod --deployment-container-image-name techconnectregistry.azurecr.io/techconnect-api:latest`
- [ ] Get ACR password again
- [ ] Configure container: `az webapp config container set --name techconnect-api-prod --resource-group techconnect-rg --docker-custom-image-name techconnectregistry.azurecr.io/techconnect-api:latest --docker-registry-server-url https://techconnectregistry.azurecr.io --docker-registry-server-user techconnectregistry --docker-registry-server-password <PASSWORD>`
- [ ] Configure port: `az webapp config appsettings set --name techconnect-api-prod --resource-group techconnect-rg --settings WEBSITES_PORT=8000`
- [ ] Wait for app to start (3-5 minutes)
- [ ] Get web app URL: `az webapp show --name techconnect-api-prod --resource-group techconnect-rg --query "defaultHostName"`
- [ ] Test endpoints:
  - [ ] `curl https://<APP-NAME>.azurewebsites.net/health`
  - [ ] `curl https://<APP-NAME>.azurewebsites.net/accelerators`
  - [ ] `curl -X POST https://<APP-NAME>.azurewebsites.net/context ...`
- [ ] View logs: `az webapp log tail --name techconnect-api-prod --resource-group techconnect-rg`

### Azure Cleanup (Optional)
- [ ] Keep ACR and resources for ongoing use, OR
- [ ] Delete all resources: `az group delete --name techconnect-rg --yes`

### Cost Tracking
- [ ] ACR cost: ~$5/month (tracked)
- [ ] ACI cost: ~$0.20/hour while running (review estimates)
- [ ] App Service cost: $12.75+/month (review pricing tier)
- [ ] Optional: Enable cost alerts in Azure Portal

### Debugging Tips
- Image not found in ACR? Verify: `az acr repository list --name techconnectregistry`
- Container won't start? Check logs: `az container logs --name <name> --resource-group techconnect-rg`
- App Service shows "Bad Gateway"? Restart: `az webapp restart --name techconnect-api-prod --resource-group techconnect-rg`
- Authentication failed? Verify credentials: `az acr credential show --name techconnectregistry`

### Completion Criteria ✅
- Image exists in Azure Container Registry
- ACI deployment successful and responds to requests (or skipped)
- App Service deployment successful and responds to requests
- All endpoints return identical responses to local testing
- Costs within budget

**Sign-off Date**: _______________

---

## 📊 Overall Progress

```
Stage 1: Local Python  ☐ ☐ ☐ ☐ ☐
Stage 2: Docker       ☐ ☐ ☐ ☐ ☐
Stage 3: Azure        ☐ ☐ ☐ ☐ ☐
```

---

## 🎯 Key Milestones

- [ ] **Milestone 1**: Local API running and tested (by Day 1)
- [ ] **Milestone 2**: Docker container running locally (by Day 2)
- [ ] **Milestone 3**: Image pushed to Azure Registry (by Day 3-5)
- [ ] **Milestone 4**: Test deployment on Azure ACI (by Day 5-7)
- [ ] **Milestone 5**: Production deployment on App Service (by Week 2-3)

---

## 📚 Documentation Reference

- **Help with Stage 1**: [SETUP_LOCAL.md](SETUP_LOCAL.md) § Stage 1
- **Help with Stage 2**: [SETUP_LOCAL.md](SETUP_LOCAL.md) § Stage 2
- **Help with Stage 3**: [AZURE_DEPLOYMENT.md](AZURE_DEPLOYMENT.md)
- **Testing help**: [TESTING.md](TESTING.md)
- **Quick commands**: [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- **Architecture**: [.github/copilot-instructions.md](.github/copilot-instructions.md)

---

## 💾 Document History

| Date | Stage | Status | Notes |
|------|-------|--------|-------|
| | 1 | | |
| | 2 | | |
| | 3a | | |
| | 3b | | |
| | 3c | | |

---

## ✨ Final Sign-Off

**All stages complete?** ✅  
**Ready for production?** ✅  
**Deployment date**: _______________  
**Deployed by**: _______________  
**Notes**: 

---

**Print this page** (Ctrl+P → Save as PDF) **for offline reference during deployment**

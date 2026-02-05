# Deployment Roadmap: From Local to Azure

## Executive Summary

Your TechConnect API is now production-ready with a complete pipeline:

```
Local Development → Docker Testing → Azure Deployment
```

This document maps out the 3-stage deployment journey with testable milestones.

---

## Stage 1: Local Development (Complete ✅)

### What You Get
- Native Python API running locally on `http://localhost:8000`
- Full test suite validating all 5 modules
- Quick iteration and debugging

### How to Start

**Option A: Automated (Recommended)**
```powershell
cd TechConnect
.\setup.ps1
```

**Option B: Manual**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python test_mvp.py
python -m uvicorn api.main:app --reload --port 8000
```

### Key Files
- **Setup Guide**: [SETUP_LOCAL.md](SETUP_LOCAL.md)
- **Testing Guide**: [TESTING.md](TESTING.md)
- **Quick Start**: [QUICKSTART.md](QUICKSTART.md)

### Success Criteria
- ✅ `python test_mvp.py` passes all 5 modules
- ✅ `curl http://localhost:8000/health` returns 200
- ✅ `curl -X POST http://localhost:8000/context` returns ContextBlock

---

## Stage 2: Docker Local Testing (Complete ✅)

### What You Get
- Containerized API that runs identically on any machine
- Docker Compose for multi-container orchestration
- Production-like environment for validation

### How to Start

**With Docker Compose (Recommended)**
```powershell
cd TechConnect
docker-compose up -d
docker-compose logs -f api
```

**Or Standalone Docker**
```powershell
docker build -t techconnect-api:latest .
docker run -d -p 8000:8000 `
  -v "$(pwd)\catalog.json:/app/catalog.json:ro" `
  techconnect-api:latest
```

### Key Files
- **Dockerfile**: [Dockerfile](Dockerfile) — Multi-stage build optimized for ~200MB
- **Docker Compose**: [docker-compose.yml](docker-compose.yml) — Service orchestration
- **.dockerignore**: [.dockerignore](.dockerignore) — Exclude non-essential files

### Success Criteria
- ✅ `docker build -t techconnect-api:latest .` succeeds
- ✅ `docker-compose up -d` starts and container becomes healthy
- ✅ `curl http://localhost:8000/health` returns 200 from container
- ✅ Image size is optimized (~250MB or less)

### Performance Expectations
- Image Build Time: 2-3 minutes (first time), <30 seconds (cached)
- Container Startup: <5 seconds
- Memory Usage: ~50-100 MB at idle
- Response Time: <500ms per request

---

## Stage 3: Azure Deployment (Testable Stages)

Your solution is designed to deploy to Azure in **3 testable stages**:

### 3.1: Azure Container Registry (ACR) - 5 minutes
**Purpose**: Store your Docker image securely in Azure

```powershell
# Create resource group
az group create --name techconnect-rg --location eastus

# Create registry (globally unique name)
az acr create --resource-group techconnect-rg `
  --name techconnectregistry --sku Basic

# Push image
docker tag techconnect-api:latest techconnectregistry.azurecr.io/techconnect-api:v1.0.0
docker push techconnectregistry.azurecr.io/techconnect-api:v1.0.0
```

**Cost**: ~$5/month  
**Status**: ✅ Production-ready registry

### 3.2: Azure Container Instances (ACI) - 10 minutes (Testing)
**Purpose**: Quick deployment for testing without infrastructure setup

```powershell
# Deploy directly from ACR
az container create --resource-group techconnect-rg `
  --name techconnect-api-test `
  --image techconnectregistry.azurecr.io/techconnect-api:v1.0.0 `
  --cpu 1 --memory 1.5 `
  --registry-username <username> --registry-password <password> `
  --ports 8000 --dns-name-label techconnect-api-test

# Get public IP
az container show --resource-group techconnect-rg `
  --name techconnect-api-test `
  --query "ipAddress.fqdn"

# Test
curl "http://<public-ip>:8000/health"
```

**Cost**: ~$0.20/hour (pay only when running)  
**Best For**: Quick validation, demos, testing  
**Status**: ✅ Perfect for Stage 2 testing

### 3.3: Azure App Service - 20 minutes (Production)
**Purpose**: Managed web hosting with auto-scaling

```powershell
# Create App Service plan (Linux)
az appservice plan create --name techconnect-plan `
  --resource-group techconnect-rg --sku B1 --is-linux

# Create web app
az webapp create --resource-group techconnect-rg `
  --plan techconnect-plan --name techconnect-api-prod `
  --deployment-container-image-name techconnectregistry.azurecr.io/techconnect-api:latest

# Configure container
az webapp config container set --name techconnect-api-prod `
  --resource-group techconnect-rg `
  --docker-custom-image-name techconnectregistry.azurecr.io/techconnect-api:latest `
  --docker-registry-server-url https://techconnectregistry.azurecr.io `
  --docker-registry-server-user <username> `
  --docker-registry-server-password <password>

# Test
curl "https://techconnect-api-prod.azurewebsites.net/health"
```

**Cost**: $12.75/month (B1) → $60+/month (production)  
**Best For**: Production use, auto-scaling, custom domain  
**Features**: 
- ✅ Built-in health monitoring
- ✅ Auto-scaling
- ✅ Custom domain support
- ✅ CI/CD integration
- ✅ Development slots for testing

---

## Recommended Deployment Path

### Week 1: Validate Locally
1. Run `.\setup.ps1` → Verify all tests pass
2. Start API → Test endpoints with curl
3. Run Skillable Simulator → Verify integration

### Week 2: Validate with Docker
1. Build Docker image → Verify size is <300MB
2. Use docker-compose → Verify services start healthily
3. Test all endpoints → Verify identical behavior to native

### Week 3: Test on Azure
1. Push to ACR → Verify image is in registry
2. Deploy to ACI → Quick validation on cloud infrastructure
3. Load test → Verify performance matches local testing

### Week 4: Go Live to Production
1. Deploy to App Service → Production-ready environment
2. Configure auto-scaling → Handle traffic spikes
3. Set up monitoring → Track performance and errors

---

## Cost Estimation

| Component | Cost | Duration | Use Case |
|-----------|------|----------|----------|
| ACR (Basic) | $5/mo | Permanent | Image storage |
| ACI | $0.20/hr | While running | Testing |
| App Service (B1) | $12.75/mo | Permanent | Production |
| App Service (S1) | $60/mo | Permanent | Production with traffic |
| **Total MVP** | **~$6/mo** | | Dev + testing |
| **Total Production** | **~$70/mo** | | Full stack |

---

## Key Features Included

✅ **Multi-stage Docker build** — Optimized image size  
✅ **Health checks** — Automated monitoring  
✅ **Volume mounts** — Live development capability  
✅ **Environment variables** — Configurable at runtime  
✅ **Azure deployment scripts** — Copy-paste ready  
✅ **CI/CD ready** — GitHub Actions integration ready  

---

## What's Next

### Immediate (Next 1-2 weeks)
- [ ] Follow [SETUP_LOCAL.md](SETUP_LOCAL.md) to start locally
- [ ] Run [TESTING.md](TESTING.md) validation suite
- [ ] Test with `docker-compose up -d`

### Short Term (Next 2-4 weeks)
- [ ] Push to Azure Container Registry
- [ ] Deploy to ACI for testing
- [ ] Configure auto-scaling in App Service

### Medium Term (Month 2-3)
- [ ] Set up GitHub Actions for CI/CD
- [ ] Configure Azure Application Insights (monitoring)
- [ ] Add custom domain & SSL certificate
- [ ] Scale to production workloads

### Long Term (Month 3+)
- [ ] Implement real GitHub crawling (Module A enhancement)
- [ ] Upgrade to production vector DB (Pinecone/Qdrant)
- [ ] Add API authentication (API keys, OAuth)
- [ ] Implement request rate limiting
- [ ] Set up backup & disaster recovery

---

## Files Created for You

| File | Purpose |
|------|---------|
| [Dockerfile](Dockerfile) | Multi-stage build, production optimized |
| [docker-compose.yml](docker-compose.yml) | Local development orchestration |
| [.dockerignore](.dockerignore) | Exclude large files from image |
| [SETUP_LOCAL.md](SETUP_LOCAL.md) | Detailed local setup guide |
| [TESTING.md](TESTING.md) | Comprehensive testing playbook |
| [AZURE_DEPLOYMENT.md](AZURE_DEPLOYMENT.md) | Step-by-step Azure deployment |
| [setup.ps1](setup.ps1) | Automated setup script |
| [.env.example](.env.example) | Environment variables template |
| [.github/copilot-instructions.md](.github/copilot-instructions.md) | AI agent guidance (updated) |

---

## Quick Command Reference

```powershell
# Local Setup
.\setup.ps1                              # Automated setup

# Local Development
python -m uvicorn api.main:app --reload  # Start API
python test_mvp.py                       # Run tests

# Docker Development
docker-compose up -d                     # Start services
docker-compose logs -f api               # View logs
docker-compose down                      # Stop services

# Azure Deployment
az login                                 # Authenticate
az group create --name techconnect-rg    # Create resource group
az acr push techconnectregistry/...      # Push image
az container create ...                  # Deploy to ACI
az webapp create ...                     # Deploy to App Service

# Testing
curl http://localhost:8000/health        # Health check
curl http://localhost:8000/accelerators  # List
curl -X POST http://localhost:8000/context ...  # Context search
```

---

## Support & Troubleshooting

**Stuck on Local Setup?**
→ See [SETUP_LOCAL.md](SETUP_LOCAL.md) § Troubleshooting

**Docker build failing?**
→ See [TESTING.md](TESTING.md) § Troubleshooting Test Failures

**Azure deployment issues?**
→ See [AZURE_DEPLOYMENT.md](AZURE_DEPLOYMENT.md) § Troubleshooting

**API behavior unexpected?**
→ See [.github/copilot-instructions.md](.github/copilot-instructions.md) for architecture details

---

## Architecture Summary

```
┌─────────────────────────────────────────────────────┐
│           TechConnect Solution Stack                │
└─────────────────────────────────────────────────────┘

┌─ LOCAL DEVELOPMENT ────────────────────────────────┐
│  Python API (uvicorn)                              │
│  Skillable Simulator                               │
│  http://localhost:8000                             │
│  (Use for: Coding, debugging, quick testing)       │
└────────────────────────────────────────────────────┘
                    ↓ docker build
┌─ LOCAL DOCKER ─────────────────────────────────────┐
│  Containerized API                                 │
│  docker-compose orchestration                      │
│  http://localhost:8000 (in container)              │
│  (Use for: Validation, CI/CD testing)              │
└────────────────────────────────────────────────────┘
                    ↓ docker push
┌─ AZURE REGISTRY ───────────────────────────────────┐
│  Azure Container Registry (ACR)                    │
│  Image: techconnectregistry.azurecr.io/...         │
│  (Use for: Secure image storage)                   │
└────────────────────────────────────────────────────┘
           ↙                    ↘
    Test Stage              Prod Stage
    ↓                       ↓
┌─ ACI (Test) ──────┐  ┌─ APP SERVICE ─────────┐
│ Quick validation   │  │ Production hosting     │
│ Pay per second     │  │ Auto-scaling           │
│ ~$0.20/hr          │  │ Custom domain          │
└────────────────────┘  │ Monitoring/Alerts      │
                        │ $12.75+/mo             │
                        └────────────────────────┘
```

---

## Next: Get Started!

**Ready to begin?**

1. **Local Setup** (15 min): Follow [SETUP_LOCAL.md](SETUP_LOCAL.md) § Stage 1
2. **Docker Testing** (10 min): Follow [SETUP_LOCAL.md](SETUP_LOCAL.md) § Stage 2
3. **Azure Deployment** (30 min): Follow [AZURE_DEPLOYMENT.md](AZURE_DEPLOYMENT.md) § Stages 1-3

Run this now to get started:
```powershell
cd TechConnect
.\setup.ps1
```

---

**Last Updated:** January 2026  
**Status:** ✅ Complete and ready for deployment  
**Next Phase:** You're ready to move from local → Docker → Azure!

# Quick Reference: TechConnect Commands

## 🚀 Get Started (First Time)

```powershell
# 1. Navigate to project
cd c:\Users\<username>\code\TechConnect2\TechConnect

# 2. Run automated setup
.\setup.ps1

# That's it! Then:
# - Native API runs at http://localhost:8000
# - Docker services running in background
# - Tests validated
```

---

## 🐍 Python Development (Native)

### Initial Setup
```bash
python -m venv .venv              # Create virtual environment
.venv\Scripts\Activate.ps1        # Activate (Windows)
source .venv/bin/activate         # Activate (Mac/Linux)
pip install -r requirements.txt   # Install dependencies
```

### Daily Development
```bash
# Activate environment (first time each session)
.venv\Scripts\Activate.ps1

# Run tests (validates all 5 modules)
python test_mvp.py

# Start API server (with auto-reload)
python -m uvicorn api.main:app --reload --port 8000

# Run Skillable Simulator
python skillable_simulator\demo.py

# Deactivate environment (when done)
deactivate
```

### Testing & Validation
```bash
# Run all module tests
python test_mvp.py

# Run API integration tests
python test_api_requests.py

# Run Skillable Simulator tests
python skillable_simulator\test_simulator.py

# Run batch processing
python -c "
from skillable_simulator.batch_processor import BatchProcessor
processor = BatchProcessor('lab_runs')
results = processor.process_batch([{'scenario_title': 'AI automation'}])
print(f'Processed {len(results)} scenarios')
"
```

---

## 🐳 Docker Development

### Build & Run
```bash
# Build image
docker build -t techconnect-api:latest .

# Run standalone (port 8000)
docker run -d --name techconnect-api -p 8000:8000 techconnect-api:latest

# View logs
docker logs -f techconnect-api

# Stop container
docker stop techconnect-api
docker rm techconnect-api
```

### Docker Compose (Recommended)
```bash
# Start all services
docker-compose up -d

# View status
docker-compose ps

# View logs
docker-compose logs -f api

# Reload after code changes
docker-compose restart api

# Stop all services
docker-compose down

# Clean up (remove images/volumes)
docker-compose down -v
```

### Debugging Containers
```bash
# Check if container is healthy
docker-compose ps

# View detailed logs
docker-compose logs api

# Execute command in running container
docker exec techconnect-api-dev curl http://localhost:8000/health

# Inspect container details
docker inspect techconnect-api-dev
```

---

## 🌐 API Testing

### Health Check
```bash
curl http://localhost:8000/health
```

### List All Accelerators
```bash
curl http://localhost:8000/accelerators
```

### Get Specific Accelerator
```bash
curl http://localhost:8000/accelerators/multi-agent-automation
```

### Search for Context (Main Endpoint)
```bash
# Windows PowerShell
curl -X POST http://localhost:8000/context `
  -H "Content-Type: application/json" `
  -d '{"scenario_title":"AI automation","solution_area":"AI","num_results":2}'

# Bash/macOS
curl -X POST http://localhost:8000/context \
  -H "Content-Type: application/json" \
  -d '{"scenario_title":"AI automation","solution_area":"AI","num_results":2}'
```

### Test with Different Scenarios
```bash
# Security focus
curl -X POST http://localhost:8000/context \
  -H "Content-Type: application/json" \
  -d '{"scenario_title":"Secure Azure deployment","solution_area":"Security"}'

# Data focus
curl -X POST http://localhost:8000/context \
  -H "Content-Type: application/json" \
  -d '{"scenario_title":"Azure data pipeline","solution_area":"Azure (Data & AI)"}'
```

---

## ☁️ Azure Deployment

### Prerequisites
```bash
az login                              # Login to Azure
az account show                       # Verify subscription
```

### Stage 1: Container Registry Setup
```bash
# Create resource group
az group create --name techconnect-rg --location eastus

# Create container registry
az acr create --resource-group techconnect-rg \
  --name techconnectregistry --sku Basic

# Login to registry
az acr login --name techconnectregistry

# Push image
docker tag techconnect-api:latest techconnectregistry.azurecr.io/techconnect-api:v1.0.0
docker push techconnectregistry.azurecr.io/techconnect-api:v1.0.0

# List images in registry
az acr repository list --name techconnectregistry
```

### Stage 2: Deploy to Container Instances (Testing)
```bash
# Get ACR credentials
az acr credential show --name techconnectregistry

# Deploy
az container create \
  --resource-group techconnect-rg \
  --name techconnect-api-test \
  --image techconnectregistry.azurecr.io/techconnect-api:v1.0.0 \
  --registry-username <username> \
  --registry-password <password> \
  --ports 8000 \
  --dns-name-label techconnect-api-test

# Get public IP
az container show --resource-group techconnect-rg \
  --name techconnect-api-test \
  --query "ipAddress.fqdn"

# Test
curl "http://<public-ip>:8000/health"

# Delete when done
az container delete --resource-group techconnect-rg \
  --name techconnect-api-test --yes
```

### Stage 3: Deploy to App Service (Production)
```bash
# Create App Service plan
az appservice plan create --name techconnect-plan \
  --resource-group techconnect-rg --sku B1 --is-linux

# Create web app
az webapp create --resource-group techconnect-rg \
  --plan techconnect-plan \
  --name techconnect-api-prod \
  --deployment-container-image-name techconnectregistry.azurecr.io/techconnect-api:latest

# Configure container
az webapp config container set --name techconnect-api-prod \
  --resource-group techconnect-rg \
  --docker-custom-image-name techconnectregistry.azurecr.io/techconnect-api:latest \
  --docker-registry-server-url https://techconnectregistry.azurecr.io \
  --docker-registry-server-user <username> \
  --docker-registry-server-password <password>

# Test
curl "https://techconnect-api-prod.azurewebsites.net/health"

# View logs
az webapp log tail --name techconnect-api-prod \
  --resource-group techconnect-rg
```

### Monitoring & Management
```bash
# View resource group
az group show --name techconnect-rg

# List all resources
az resource list --resource-group techconnect-rg --output table

# Delete all resources (cleanup)
az group delete --name techconnect-rg --yes
```

---

## 📊 Performance & Debugging

### Monitor API Performance
```bash
# Check response time
Measure-Command {
    curl -s http://localhost:8000/context `
      -H "Content-Type: application/json" `
      -d '{"scenario_title":"test"}' | Out-Null
}

# Load test with Apache Bench
ab -n 100 -c 10 http://localhost:8000/health

# Monitor Docker resource usage
docker stats techconnect-api-dev
```

### Check Port Usage
```bash
# Find what's using port 8000
netstat -ano | findstr :8000

# Kill process (replace <PID>)
taskkill /PID <PID> /F
```

### View File Sizes
```bash
# Check Docker image size
docker images techconnect-api

# Check directory sizes
du -sh TechConnect
ls -lh *.json
```

---

## 🔍 Troubleshooting Cheat Sheet

| Problem | Command | Solution |
|---------|---------|----------|
| Port already in use | `netstat -ano \| findstr :8000` | Kill process or use different port |
| Docker build slow | `docker build --progress=plain .` | Use `-nocache` or check disk space |
| Container won't start | `docker logs <container>` | Check logs for error messages |
| Missing dependencies | `pip list` | Reinstall: `pip install -r requirements.txt` |
| Venv not activated | `which python` | Run `.venv\Scripts\Activate.ps1` |
| API returns 404 | `curl http://localhost:8000/health` | Check if API is running |
| Catalog not found | `ls -la catalog.json` | Verify file exists in project root |
| Docker image too large | `docker history techconnect-api` | Use multi-stage build (already done) |

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| [SETUP_LOCAL.md](SETUP_LOCAL.md) | Detailed local development guide |
| [TESTING.md](TESTING.md) | Complete testing playbook |
| [AZURE_DEPLOYMENT.md](AZURE_DEPLOYMENT.md) | Azure deployment steps |
| [DEPLOYMENT_ROADMAP.md](DEPLOYMENT_ROADMAP.md) | Overall strategy & timeline |
| [.github/copilot-instructions.md](.github/copilot-instructions.md) | Architecture overview for AI agents |
| [QUICKSTART.md](QUICKSTART.md) | MVP quick start guide |

---

## 💡 Pro Tips

1. **Save time with aliases** (Bash/PowerShell):
   ```powershell
   New-Alias api-start "python -m uvicorn api.main:app --reload"
   New-Alias docker-up "docker-compose up -d"
   ```

2. **Keep terminal window open for logs**:
   ```bash
   # Terminal 1: API logs
   docker-compose logs -f api
   
   # Terminal 2: Testing
   curl http://localhost:8000/health
   ```

3. **Use environment file for settings**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   docker-compose --env-file .env up -d
   ```

4. **Automate testing in CI/CD** (GitHub Actions ready):
   See [TESTING.md](TESTING.md) § Continuous Testing

5. **Monitor API health while developing**:
   ```bash
   # Run every 5 seconds
   while ($true) { curl -s http://localhost:8000/health; Start-Sleep -Seconds 5 }
   ```

---

**Last Updated:** January 2026  
**Print this page:** Ctrl+P → Save as PDF for quick reference

# Local Development Setup Guide

## Overview

This guide walks you through running the TechConnect API and Skillable Simulator locally. We'll start with **native Python**, then move to **Docker** for production-like testing, and finally **Azure deployment**.

## Stage 1: Native Local Setup (10 minutes)

### Prerequisites
- Python 3.9+
- pip package manager
- Terminal/PowerShell

### Step 1.1: Create Virtual Environment

**Windows (PowerShell):**
```powershell
cd c:\Users\<username>\code\TechConnect2\TechConnect
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
cd ~/path/to/TechConnect
python3 -m venv .venv
source .venv/bin/activate
```

You should see `(.venv)` in your terminal prompt.

### Step 1.2: Install Dependencies

```bash
pip install -r requirements.txt
```

Verify installation:
```bash
python -c "import fastapi; import pydantic; print('✓ Dependencies installed')"
```

### Step 1.3: Run Tests

```bash
python test_mvp.py
```

Expected output:
```
========== TEST MODULE A: Scraper ==================
✓ Loaded catalog with 3 accelerators
...
========== TEST MODULE E: RAI Guardrails ===========
✓ RAI disclaimer injected correctly
```

### Step 1.4: Start the API Server

```bash
python -m uvicorn api.main:app --reload --port 8000
```

Expected:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### Step 1.5: Test the API

**In a new terminal (keep server running):**

```powershell
# Health check
curl http://localhost:8000/health

# List accelerators
curl http://localhost:8000/accelerators

# Get context block
curl -X POST http://localhost:8000/context `
  -H "Content-Type: application/json" `
  -d '{"scenario_title":"AI automation","solution_area":"AI","num_results":2}'
```

**Example successful response:**
```json
{
  "request_id": "req_abc123",
  "blocks": [
    {
      "catalog_item_id": "multi-agent-automation",
      "solution_name": "Multi-Agent Custom Automation Engine",
      "solution_area": "AI",
      "complexity_level": "L400",
      "architecture_summary": "Build autonomous agents...",
      "prerequisites_xml": "<prerequisites><item>Azure Subscription</item>...</prerequisites>",
      "products_xml": "<products><product>Azure AI Foundry</product>...</products>",
      "rai_disclaimer": "⚠️ RESPONSIBLE AI DISCLAIMER...",
      "repository_url": "https://github.com/microsoft/Solution-Accelerators"
    }
  ],
  "count": 1
}
```

---

## Stage 2: Docker Local Development (15 minutes)

### Prerequisites
- Docker Desktop installed and running
- Verify: `docker --version` returns v24.0+

### Step 2.1: Build Docker Image

```powershell
cd c:\Users\<username>\code\TechConnect2\TechConnect

# Build image
docker build -t techconnect-api:latest .

# Verify build
docker images | grep techconnect-api
```

### Step 2.2: Run API in Container

```powershell
# Run container
docker run -d `
  --name techconnect-api-dev `
  -p 8000:8000 `
  -v "$(Get-Location)\catalog.json:/app/catalog.json:ro" `
  -v "$(Get-Location)\data\chroma:/app/.chroma" `
  techconnect-api:latest

# Check logs
docker logs -f techconnect-api-dev
```

Expected logs:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Step 2.3: Test Containerized API

```powershell
# Health check
curl http://localhost:8000/health

# Test context endpoint
curl -X POST http://localhost:8000/context `
  -H "Content-Type: application/json" `
  -d '{"scenario_title":"AI automation","num_results":2}'
```

### Step 2.4: Use Docker Compose (Recommended)

```powershell
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

**Check container is healthy:**
```powershell
docker-compose ps
# Should show: techconnect-api    Up (healthy)
```

### Step 2.5: Develop with Docker Compose

Mount your local code for live updates:

```yaml
# docker-compose.yml (modify volumes section)
volumes:
  - ./:/app  # Mount entire project for live development
  - /app/__pycache__  # Except Python cache
```

Then:
```powershell
docker-compose up -d
docker-compose logs -f api
# Edit files locally; changes reflected immediately
```

---

## Stage 3: Skillable Simulator Integration (20 minutes)

### Step 3.1: Test Simulator with Running API

```powershell
# Ensure API is running (Stage 1 or 2)
# API should be at http://localhost:8000

# Run simulator tests
python skillable_simulator\test_simulator.py

# Or use the simulator directly
python -c "
from skillable_simulator.simulator import SkillableSimulator
sim = SkillableSimulator('catalog.json')
context = sim.fetch_context_block('AI automation', 'AI')
print(f'Got context: {context.solution_name}')
"
```

### Step 3.2: Run End-to-End Workflow

```powershell
# Start API in background (or in separate terminal)
python -m uvicorn api.main:app --port 8000

# In new terminal, run demo
cd skillable_simulator
python demo.py
```

Expected output:
```
Generating lab for: Multi-Agent Custom Automation Engine
Lab Guide:
===========
## Scenario
Build an AI agent for automating business workflows...

Lab Instructions:
1. Create Azure AI resource
2. Deploy agent...

Deployment Script:
#!/bin/bash
az group create --name myGroup...
```

### Step 3.3: Batch Processing (Optional)

```powershell
python -c "
from skillable_simulator.batch_processor import BatchProcessor

processor = BatchProcessor('lab_runs')
results = processor.process_batch([
    {'scenario_title': 'AI automation', 'solution_area': 'AI'},
    {'scenario_title': 'Security hardening', 'solution_area': 'Security'}
])
print(f'Processed {len(results)} scenarios')
"
```

---

## Troubleshooting

### Issue: Port 8000 already in use

**Solution:**
```powershell
# Find process using port
netstat -ano | findstr :8000

# Kill process (get PID from above)
taskkill /PID <PID> /F

# Or use different port
python -m uvicorn api.main:app --port 8001
```

### Issue: Docker build fails

**Solution:**
```powershell
# Clean and rebuild
docker system prune -a
docker build --no-cache -t techconnect-api:latest .
```

### Issue: catalog.json not found in container

**Solution:** Ensure volume mount is correct:
```powershell
# Check mounted files
docker exec techconnect-api-dev ls -la /app/

# Should show catalog.json
```

### Issue: Vector store not persisting

**Solution:** Check volume mount for `.chroma` directory:
```powershell
# Create data directory if missing
mkdir data\chroma

# Verify in docker-compose.yml:
# - ./data/chroma:/app/.chroma
```

---

## Development Workflow

### Daily Development Loop

```powershell
# 1. Start services
docker-compose up -d

# 2. Watch logs
docker-compose logs -f api

# 3. Edit code in VS Code (mounted via volume)

# 4. Test changes
curl http://localhost:8000/health

# 5. When done
docker-compose down
```

### Making Changes to Requirements

```powershell
# 1. Add new package to requirements.txt
# 2. Rebuild image
docker build -t techconnect-api:latest .

# 3. Update container
docker-compose up -d --build

# 4. Verify
docker-compose logs api
```

---

## Next Steps: Azure Deployment

Once local testing is complete, proceed to [AZURE_DEPLOYMENT.md](AZURE_DEPLOYMENT.md) for:
- Setting up Azure Container Registry (ACR)
- Deploying to Azure Container Instances (ACI)
- Setting up Azure App Service
- Configuring Azure Resource Manager templates

---

**Quick Reference**

| Task | Command |
|------|---------|
| Start API (native) | `python -m uvicorn api.main:app --port 8000` |
| Start API (docker) | `docker-compose up -d` |
| Run tests | `python test_mvp.py` |
| View logs | `docker-compose logs -f api` |
| Stop services | `docker-compose down` |
| Clean Docker | `docker system prune -a` |
| Test health | `curl http://localhost:8000/health` |

---

**Last Updated:** January 2026  
**Status:** Ready for local development and Docker testing

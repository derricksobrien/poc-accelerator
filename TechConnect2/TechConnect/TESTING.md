# Testing & Validation Guide

## Quick Start (5 minutes)

### Option A: Use Automated Setup Script

**Windows (PowerShell):**
```powershell
cd c:\Users\<username>\code\TechConnect2\TechConnect
.\setup.ps1
```

This will:
- ✅ Check prerequisites (Python, Docker)
- ✅ Create virtual environment
- ✅ Install dependencies
- ✅ Build Docker image
- ✅ Start API with docker-compose
- ✅ Run health checks

### Option B: Manual Setup

**Step 1: Install Dependencies**
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
```

**Step 2: Run Tests**
```bash
python test_mvp.py
```

**Step 3: Start API**
```bash
python -m uvicorn api.main:app --reload --port 8000
```

**Step 4: Start Docker (in another terminal)**
```bash
docker-compose up -d
```

---

## Complete Testing Workflow

### 1. Unit Tests (Module Validation)

Run atomic tests for each module:

```bash
python test_mvp.py
```

Expected output:
```
======== TEST MODULE A: Scraper ========
✓ Loaded catalog with 3 accelerators
✓ Retrieved accelerators by ID
✓ Filtered by solution area
✓ Found RAI-required items

======== TEST MODULE B: Metadata ========
✓ Validated 3 CatalogItem schemas
✓ Pydantic validation enforced

======== TEST MODULE C: Vector Store ========
✓ Ingested 3 accelerators
✓ Semantic search returned results
✓ Metadata filtering works
✓ Direct lookup successful

======== TEST MODULE D: Context Provider ========
✓ ContextBlock formatting correct
✓ XML tags properly formed
✓ Prerequisites compacted

======== TEST MODULE E: RAI Guardrails ========
✓ RAI disclaimer injected for AI solutions
✓ Non-RAI solutions excluded

✓ All 5 modules validated successfully!
```

**If tests fail:**
1. Check catalog.json exists: `ls catalog.json`
2. Verify Python environment: `python -c "import pydantic; print(pydantic.__version__)"`
3. Check for errors: `python test_mvp.py 2>&1 | head -50`

---

### 2. API Tests (HTTP Integration)

#### 2.1: Health Check

```bash
curl http://localhost:8000/health
```

Expected: `{"status": "ok"}`

#### 2.2: List Accelerators

```bash
curl http://localhost:8000/accelerators
```

Expected: 
```json
{
  "accelerators": [
    {
      "id": "multi-agent-automation",
      "name": "Multi-Agent Custom Automation Engine",
      ...
    }
  ]
}
```

#### 2.3: Get Specific Accelerator

```bash
curl http://localhost:8000/accelerators/multi-agent-automation
```

#### 2.4: Main Endpoint - Context Retrieval

```bash
curl -X POST http://localhost:8000/context \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_title": "Build an AI agent for automating business workflows",
    "solution_area": "AI",
    "num_results": 2
  }'
```

Expected:
```json
{
  "request_id": "req_abc123def456",
  "blocks": [
    {
      "catalog_item_id": "multi-agent-automation",
      "solution_name": "Multi-Agent Custom Automation Engine",
      "solution_area": "AI",
      "complexity_level": "L400",
      "architecture_summary": "Delegate complex, repetitive tasks to AI agents...",
      "prerequisites_xml": "<prerequisites><item>Azure Subscription</item>...</prerequisites>",
      "products_xml": "<products><product>Azure AI Foundry</product>...</products>",
      "rai_disclaimer": "⚠️ RESPONSIBLE AI DISCLAIMER...",
      "repository_url": "https://github.com/microsoft/Solution-Accelerators"
    }
  ],
  "count": 1
}
```

#### 2.5: Error Handling

**Invalid request (missing scenario_title):**
```bash
curl -X POST http://localhost:8000/context \
  -H "Content-Type: application/json" \
  -d '{"solution_area":"AI"}'
```

Expected: `400 Bad Request - Field scenario_title required`

**Nonexistent accelerator:**
```bash
curl http://localhost:8000/accelerators/nonexistent
```

Expected: `404 Not Found`

---

### 3. Docker Tests

#### 3.1: Build Image

```bash
docker build -t techconnect-api:test .
docker image ls | grep techconnect
```

#### 3.2: Run Container (Standalone)

```bash
docker run -d \
  --name techconnect-test \
  -p 8001:8000 \
  -v "$(pwd)\catalog.json:/app/catalog.json:ro" \
  techconnect-api:test

# Wait for startup
Sleep-Milliseconds 3000

# Test
curl http://localhost:8001/health

# Cleanup
docker stop techconnect-test
docker rm techconnect-test
```

#### 3.3: Run with Docker Compose

```bash
# Start
docker-compose up -d

# Verify healthy
docker-compose ps
# Status should be: "Up (healthy)"

# View logs
docker-compose logs -f api

# Test
curl http://localhost:8000/health

# Stop
docker-compose down
```

#### 3.4: Image Size & Performance

```bash
# Check image size
docker images techconnect-api

# Expected: ~200-300 MB (multi-stage build optimized)

# Check container resource usage
docker stats techconnect-api-dev

# Expected: <50 MB memory, <5% CPU at idle
```

---

### 4. Integration Tests (API + Simulator)

#### 4.1: Skillable Simulator Test

```bash
python skillable_simulator/test_simulator.py
```

Expected output:
```
Test XMLParser...
✓ Extracted prerequisites
✓ Extracted products

Test LabInstructionGenerator...
✓ Generated lab guide
✓ Generated deployment script
✓ Generated test report

Test SkillableSimulator...
✓ Fetched context block
✓ Generated complete lab
```

#### 4.2: End-to-End Demo

```bash
# Ensure API is running (from test 2 or 3)

# Run demo
cd skillable_simulator
python demo.py
```

Expected output:
```
Generating lab for: Multi-Agent Custom Automation Engine

LAB GUIDE
=========
## Scenario
Build an AI agent for automating business workflows

## Learning Objectives
1. Understand multi-agent design patterns
2. Implement orchestration logic
...

DEPLOYMENT SCRIPT
=================
#!/bin/bash
az group create --name myResourceGroup --location eastus
...

LAB REPORT
==========
Title: Multi-Agent Custom Automation Engine
Complexity: L400
Duration: 45-60 minutes
```

---

### 5. Performance Tests (Load Testing)

#### 5.1: Single Request Timing

```bash
# Measure latency
Measure-Command {
    curl -s http://localhost:8000/context `
      -H "Content-Type: application/json" `
      -d '{"scenario_title":"AI automation","num_results":1}' | Out-Null
}
```

Expected: <500ms response time

#### 5.2: Multiple Concurrent Requests

```bash
# Install Apache Bench
# On Windows with Chocolatey: choco install apache-httpd
# Extract ab.exe from \Apache24\bin\

# Run 100 requests with 10 concurrent
ab -n 100 -c 10 http://localhost:8000/health

# Expected output shows:
# Requests per second: 50+
# Failed requests: 0
# Average response time: <50ms
```

---

### 6. Data Validation Tests

#### 6.1: Catalog Integrity

```bash
python -c "
from ingestion.scraper import CatalogScraper
from models.schemas import CatalogItem

scraper = CatalogScraper('catalog.json')
catalog = scraper.load_catalog()

print(f'Total accelerators: {len(catalog.solution_accelerators)}')

for acc in catalog.solution_accelerators:
    # Validate required fields
    assert acc.id, 'Missing ID'
    assert acc.name, 'Missing name'
    assert acc.solution_area in ['AI', 'Security', 'Azure (Data & AI)', 'Cloud & AI Platforms'], f'Invalid area: {acc.solution_area}'
    assert acc.technical_complexity in ['L200', 'L300', 'L400'], f'Invalid complexity: {acc.technical_complexity}'
    assert isinstance(acc.prerequisites, list), 'Prerequisites not a list'
    assert isinstance(acc.responsible_ai_tag, bool), 'RAI tag not boolean'
    
print('✓ All accelerators valid')
"
```

#### 6.2: XML Output Validation

```bash
python -c "
from api.main import _format_prerequisites_xml, _format_products_xml
from xml.etree import ElementTree as ET

# Test prerequisites XML
prereqs = ['Azure Subscription', 'Python 3.9+']
xml = _format_prerequisites_xml(prereqs)
print(f'Prerequisites XML: {xml}')

# Validate it's well-formed XML
root = ET.fromstring(xml)
print(f'✓ Valid XML with {len(root)} items')

# Test products XML
products = ['Azure AI Foundry', 'Azure OpenAI Service']
xml = _format_products_xml(products)
root = ET.fromstring(xml)
print(f'✓ Valid XML with {len(root)} products')
"
```

---

### 7. Security Tests (Basic)

#### 7.1: Input Validation

```bash
# Test SQL injection (should be safe with Pydantic)
curl -X POST http://localhost:8000/context \
  -H "Content-Type: application/json" \
  -d '{"scenario_title":"test; DROP TABLE catalog;--","num_results":1}'
# Expected: Normal response, no injection

# Test XSS (should be escaped in response)
curl -X POST http://localhost:8000/context \
  -H "Content-Type: application/json" \
  -d '{"scenario_title":"<script>alert(1)</script>","num_results":1}'
# Expected: Returns with script tag as literal string in JSON
```

#### 7.2: API Abuse Prevention

```bash
# Test rate limiting (if implemented, should reject after N requests)
for ($i=0; $i -lt 50; $i++) {
    curl -s http://localhost:8000/health | Out-Null
}
# Expected: All requests succeed (rate limiting not implemented yet)
```

---

## Troubleshooting Test Failures

### Issue: ModuleNotFoundError

```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```bash
# Verify venv is activated
.venv\Scripts\Activate.ps1  # Should show (.venv) in prompt

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue: catalog.json Not Found

```
FileNotFoundError: Catalog not found at ...
```

**Solution:**
```bash
# Verify file exists
ls -la catalog.json

# If missing, check workspace structure
ls -la *.json
```

### Issue: Port Already in Use

```
Address already in use: 0.0.0.0:8000
```

**Solution:**
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process (replace <PID> with number from above)
taskkill /PID <PID> /F

# Or use different port
python -m uvicorn api.main:app --port 8001
```

### Issue: Docker Image Build Fails

```
ERROR: failed to solve with frontend dockerfile.v0: failed to build LLB
```

**Solution:**
```powershell
# Clean Docker system
docker system prune -a

# Rebuild with verbose output
docker build -t techconnect-api:latest --progress=plain .
```

### Issue: Docker Container Exits Immediately

```bash
docker logs techconnect-api-dev
# Look for error messages
```

**Solution:**
```bash
# Check container logs
docker-compose logs api

# Common causes:
# 1. Missing catalog.json volume
# 2. Port conflict
# 3. Python error in main.py

# Fix and restart
docker-compose down
docker-compose up -d
docker-compose logs -f api
```

---

## Test Checklist

Before declaring "ready for deployment":

- [ ] `python test_mvp.py` — All 5 modules pass
- [ ] `curl http://localhost:8000/health` — Returns 200
- [ ] `curl http://localhost:8000/accelerators` — Returns all 3
- [ ] `curl -X POST .../context` — Returns ContextBlock with XML tags
- [ ] Docker image builds without errors
- [ ] `docker-compose up -d` — Services start and become healthy
- [ ] Skillable simulator test passes
- [ ] Performance acceptable (<500ms per request)
- [ ] No Python warnings or errors in logs

---

## Continuous Testing

### Setup Automated Testing (Optional)

Create `.github/workflows/test.yml`:

```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r TechConnect/requirements.txt
      - run: cd TechConnect && python test_mvp.py
      - run: cd TechConnect && python skillable_simulator/test_simulator.py
```

---

**Last Updated:** January 2026  
**Status:** All tests automated and documented

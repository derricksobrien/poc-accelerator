# Troubleshooting Guide

## Quick Diagnosis

### Is the service running?
```bash
curl http://localhost:5000/api/health
```
**Expected:** HTTP 200 with `{"status": "healthy"}`

### Is Python installed?
```bash
python --version
```
**Expected:** Python 3.8 or higher

### Are dependencies installed?
```bash
pip list | grep -E "(fastapi|flask|pydantic|requests)"
```
**Expected:** All packages listed

---

## Common Issues & Solutions

## 1. "ModuleNotFoundError: No module named 'techconnect'"

### Problem
```
ModuleNotFoundError: No module named 'techconnect'
ImportError: cannot import name 'RAGSystem'
```

### Solutions

**Option A: Install Requirements**
```bash
pip install -r requirements.txt
```

**Option B: Add to Python Path**
```bash
# Linux/Mac
export PYTHONPATH="${PYTHONPATH}:/path/to/TechConnect"

# Windows PowerShell
$env:PYTHONPATH += ";C:\path\to\TechConnect"
```

**Option C: Install in Dev Mode**
```bash
cd /path/to/poc-accelerator
pip install -e .
```

---

## 2. "Connection refused" or "Cannot connect to localhost:5000"

### Problem
```
Error: Cannot connect to http://localhost:5000
ConnectionRefusedError: [Errno 111] Connection refused
```

### Diagnosis
```bash
# Check if service is running
netstat -an | grep 5000

# Check if port is in use
lsof -i :5000
```

### Solutions

**Option A: Start the Service**
```bash
python TechConnect/app.py
# or
python System3-RAG/streamlit_app.py
```

**Option B: Port Already in Use**
```bash
# Kill existing process on port 5000
# Windows PowerShell
Stop-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess -Force

# Linux/Mac
lsof -ti:5000 | xargs kill -9

# Then restart service on different port
python TechConnect/app.py --port 8080
```

**Option C: Check Firewall**
```bash
# Windows: Allow Flask through firewall
# Settings > Privacy & Security > Firewall > Allow app through firewall
# Linux: Check UFW
sudo ufw status
```

---

## 3. "ModuleNotFoundError: No module named 'azure'"

### Problem
```
ModuleNotFoundError: No module named 'azure'
ModuleNotFoundError: No module named 'openai'
```

### Solution
```bash
# Install Azure SDK packages
pip install azure-identity azure-keyvault-secrets
pip install openai

# Or install all at once
pip install -r requirements.txt
```

---

## 4. Azure Connection Error: "Invalid API Key"

### Problem
```
401 Unauthorized: Invalid authentication credentials
AuthenticationError: Authentication failed. Invalid credentials.
```

### Diagnosis
```bash
# Check if env var is set
echo $OPENAI_API_KEY
# (Should print your key, not blank)

# Verify it's valid format
# Keys usually start with: sk-... or similar
```

### Solutions

**Option A: Set Correct API Key**
```bash
# Linux/Mac
export OPENAI_API_KEY="sk-your-actual-key-here"

# Windows PowerShell
$env:OPENAI_API_KEY="sk-your-actual-key-here"

# Verify
echo $env:OPENAI_API_KEY
```

**Option B: Check Azure Credentials**
```bash
# Verify you have valid Azure subscription
az login

# List available OpenAI instances
az cognitiveservices account list --query "[].{Name:name, Kind:kind}"
```

**Option C: Validate in Python**
```python
import os
import openai

key = os.environ.get('OPENAI_API_KEY')
if not key:
    print("ERROR: OPENAI_API_KEY not set")
else:
    print(f"Key found: {key[:10]}...")
    
# Try connection
try:
    openai.api_key = key
    models = openai.Model.list()
    print("✓ Connection successful")
except Exception as e:
    print(f"✗ Connection failed: {e}")
```

---

## 5. "Catalog.json not found"

### Problem
```
FileNotFoundError: [Errno 2] No such file or directory: 'catalog.json'
```

### Solution
```bash
# Verify file exists
ls -la catalog.json

# Should be in root directory
# If not, create a sample catalog.json
```

### Create Sample Catalog
```bash
cat > catalog.json << 'EOF'
[
  {
    "id": "ai-001",
    "name": "Sample AI Solution",
    "solution_area": "AI",
    "technical_complexity": "L300",
    "description": "Sample description"
  }
]
EOF
```

---

## 6. Docker Build Fails

### Problem
```
docker build -t poc-accelerator .
ERROR: failed to solve with frontend dockerfile.v0
```

### Solutions

**Option A: Check Docker is Running**
```bash
docker ps
# If error: Cannot connect to Docker daemon
# Solution: Start Docker Desktop or Docker service
```

**Option B: Clean Docker Cache**
```bash
docker system prune -a
docker build -t poc-accelerator .
```

**Option C: Check Dockerfile**
```bash
# Verify Dockerfile exists in current directory
ls -la Dockerfile

# Verify it's valid
docker build --no-cache -t poc-accelerator .
```

**Option D: Build with Verbose Output**
```bash
docker build --progress=plain -t poc-accelerator .
```

---

## 7. Container Won't Start (Docker)

### Problem
```
docker: Error response from daemon: OCI runtime create failed
container_linux.go:380: starting container process caused: ...
```

### Diagnosis
```bash
# Check container logs
docker logs container-name

# Check if port is available
lsof -i :5000

# Inspect container
docker inspect container-name
```

### Solutions

**Option A: Map Different Port**
```bash
docker run -p 8080:5000 poc-accelerator:latest
# Service now at http://localhost:8080
```

**Option B: Increase Memory**
```bash
docker run -m 2g -p 5000:5000 poc-accelerator:latest
```

**Option C: Run in Foreground (See Errors)**
```bash
docker run -it --rm -p 5000:5000 poc-accelerator:latest
# Press Ctrl+C to stop
```

---

## 8. "Port Already in Use"

### Problem
```
Error: Port 5000 is already in use
Address already in use
```

### Solutions

**Option A: Find & Kill Process**
```bash
# Linux/Mac
lsof -i :5000 | tail -1 | awk '{print $2}' | xargs kill -9

# Windows PowerShell
Stop-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess -Force
```

**Option B: Use Different Port**
```bash
python TechConnect/app.py --port 8080
# Now at http://localhost:8080
```

**Option C: See What's Using Port**
```bash
# Linux/Mac
lsof -i :5000

# Windows
netstat -ano | findstr :5000
```

---

## 9. Search Returns No Results

### Problem
```json
{
    "total_results": 0,
    "results": []
}
```

### Solutions

**Option A: Try Broader Query**
```bash
# Instead of: "specific tool X version Y"
# Try: "tool", "data processing", etc
```

**Option B: Verify Catalog Loaded**
```bash
curl http://localhost:5000/api/list-scenarios
# Should return 50+ items
```

**Option C: Check Spelling**
```bash
# Search is case-insensitive, but exact terms help
# Valid areas: "AI", "Security", "Azure (Data & AI)", "Cloud & AI Platforms"
```

**Option D: Debug Search Directly**
```python
from techconnect.vector_store import VectorStore
store = VectorStore("catalog.json")
results = store.search("your query here")
print(f"Found {len(results)} results")
for r in results:
    print(f"- {r['name']}: {r['similarity_score']:.2f}")
```

---

## 10. "POC Generation Failed"

### Problem
```json
{
    "status": "error",
    "message": "Failed to generate POC"
}
```

### Solutions

**Option A: Check Azure Connection**
```bash
curl -X POST http://localhost:5000/api/validate-azure \
  -H "Content-Type: application/json" \
  -d '{"openai_key":"sk-...","openai_base":"https://..."}'
```

**Option B: Verify API Key**
```bash
# Check key is set and correctly formatted
echo $OPENAI_API_KEY
# Should start with "sk-" and be 40+ characters
```

**Option C: Check Input**
```bash
# Verify title and description are provided
curl -X POST http://localhost:5000/api/generate-poc \
  -H "Content-Type: application/json" \
  -d '{
    "title":"My POC Title",
    "description":"Clear description here",
    "azure_config":{"openai_key":"sk-...","openai_base":"https://..."}
  }'
```

**Option D: Check Logs**
```bash
# If running in terminal: Check error output
# If Docker: docker logs container-name
# If Azure: Check Application Insights
az monitor app-insights metrics show --resource-group rg-name --resource app-name
```

---

## 11. High Memory Usage

### Problem
```
Memory usage: 1.2GB (expected: <512MB)
Container OOMKilled
```

### Solutions

**Option A: Check for Memory Leaks**
```python
import tracemalloc

tracemalloc.start()
# ... your code ...
current, peak = tracemalloc.get_traced_memory()
print(f"Current: {current / 1024 / 1024:.1f} MB")
print(f"Peak: {peak / 1024 / 1024:.1f} MB")
```

**Option B: Reduce Batch Size**
```python
# In rag_system.py
batch_size = 5  # Reduce from 10 to 5
```

**Option C: Increase Container Memory**
```bash
# Docker
docker run -m 2g -p 5000:5000 poc-accelerator:latest

# Azure Container Apps
az containerapp update --name app-name --resource-group rg-name \
  --memory "1.5Gi"
```

---

## 12. Deployment to Azure Fails

### Problem
```
Error: Subscription not found
Error: Resource group doesn't exist
```

### Solutions

**Option A: Check Azure Login**
```bash
az login
az account show
# Should show your subscription
```

**Option B: Create Resource Group**
```bash
az group create \
  --name my-resource-group \
  --location eastus
```

**Option C: Set Default Subscription**
```bash
az account set --subscription "subscription-name"
az account show
```

**Option D: Check Permissions**
```bash
# You need Owner or Contributor role
az role assignment list --assignee $(az account show --query user.name -o tsv)
```

---

## 13. GitHub Pages 404 Errors

### Problem
```
GitHub Pages shows 404 for documentation
Markdown files not rendering
```

### Solutions

**Option A: Verify File Names**
```bash
# Check exact filenames in docs/ folder
ls docs/
# Should include: COMPLETION-REPORT.md, GETTING-STARTED.md, etc
```

**Option B: Check Links**
```bash
# In index.html, verify links are correct
# Should be: href="COMPLETION-REPORT.md" (lowercase)
```

**Option C: Push Changes**
```bash
git add docs/
git commit -m "docs: Add markdown documentation"
git push origin master
```

---

## 14. Tests Failing

### Problem
```
FAILED test/test_rag_system.py::test_generate_poc
AssertionError: ...
```

### Solutions

**Option A: Check Dependencies**
```bash
pip install -r requirements.txt
pip install pytest pytest-cov
```

**Option B: Run Single Test**
```bash
pytest test/test_rag_system.py::test_generate_poc -v
```

**Option C: Check Test Config**
```bash
# Verify test has required environment variables
export OPENAI_API_KEY="test-key"
pytest
```

---

## Still Having Issues?

### Collect Diagnostic Info
```bash
# Save system info
python --version > diagnostics.txt
pip list >> diagnostics.txt
echo "---" >> diagnostics.txt

# Run health check
curl http://localhost:5000/api/health >> diagnostics.txt

# Include in bug report
cat diagnostics.txt
```

### Debug Modes

**Flask Debug Mode**
```python
# In app.py
app = Flask(__name__)
app.config['DEBUG'] = True
```

**Streamlit Debug**
```bash
streamlit run system3-RAG/streamlit_app.py --logger.level=debug
```

**Python Verbose**
```bash
python -vvv TechConnect/app.py
```

---

### Getting Help

1. **Check this guide** first (you are here!)
2. **Review logs:** Browser console, terminal output, Docker logs
3. **Search GitHub Issues:** https://github.com/derricksobrien/poc-accelerator/issues
4. **Check API Status:** `/api/health` endpoint
5. **Verify Prerequisites:** Python, pip, Docker (if needed)

---

**Other Resources:** [Getting Started](GETTING-STARTED.md) | [Deployment](DEPLOYMENT.md) | [API Reference](API-REFERENCE.md)

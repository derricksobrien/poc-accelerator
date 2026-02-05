# Quick Reference: Testing & Agent Setup Commands

**Copy-paste ready commands for common tasks**

## 🧪 Testing Commands

### Install Test Dependencies
```bash
cd System3-RAG
pip install pytest pytest-asyncio httpx coverage
```

### Run Tests

**All tests:**
```bash
pytest test_all_endpoints.py test_csa_scenarios.py -v
```

**Just endpoint tests:**
```bash
pytest test_all_endpoints.py -v
```

**Just CSA scenarios:**
```bash
pytest test_csa_scenarios.py -v
```

**Single test:**
```bash
pytest test_all_endpoints.py::TestHealthAndStatus::test_health_check -v
```

**With coverage:**
```bash
pytest test_all_endpoints.py --cov=app --cov-report=html
# Opens: coverage/index.html
```

**CSA Scenario 1 (Enterprise AI Chatbot):**
```bash
pytest test_csa_scenarios.py::TestCSAL400Scenarios::test_scenario_1_enterprise_ai_chatbot_basic -v
```

**All RBAC tests:**
```bash
pytest test_all_endpoints.py::TestAgentIntegration::test_agent_generate_rbac_tool -v
```

**Performance tests:**
```bash
pytest test_all_endpoints.py::TestPerformance -v --durations=10
```

---

## ⚙️ Azure AI Foundry Setup Commands

### Quick Setup (Automated)
```bash
# Replace with your values:
python setup_azure_agent.py \
  --subscription "12345678-1234-1234-1234-123456789012" \
  --resource-group "contoso-ai-rg" \
  --region eastus \
  --project techconnect-rag
```

### Manual Azure CLI Commands

**Create resource group:**
```bash
az group create \
  --name contoso-ai-rg \
  --location eastus
```

**Check subscription:**
```bash
az account show
az account set --subscription "YOUR_SUBSCRIPTION_ID"
```

**Create AI Hub:**
```bash
az ai hub create \
  --resource-group contoso-ai-rg \
  --name techconnect-rag-hub \
  --location eastus
```

**Create AI Project:**
```bash
az ai project create \
  --resource-group contoso-ai-rg \
  --name techconnect-rag \
  --hub techconnect-rag-hub
```

**Deploy GPT-4 Model:**
```bash
az ai deployment create \
  --resource-group contoso-ai-rg \
  --project techconnect-rag \
  --name gpt4-deployment \
  --model gpt-4 \
  --version 0125-preview \
  --instance-type standard
```

**Get Azure Credentials:**
```bash
# Get project details
az ai project show \
  --resource-group contoso-ai-rg \
  --name techconnect-rag \
  --query properties

# Get API key
az keyvault secret show \
  --vault-name techconnect-rag-kv \
  --name openai-api-key \
  --query value
```

---

## 🔐 Configuration

### Create .env File
```bash
# Copy template
copy .env.example .env
# Or on Linux/Mac:
cp .env.example .env

# Edit with your values:
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=sk-your-key-here
AZURE_MODEL_DEPLOYMENT=gpt4-deployment
AZURE_AI_PROJECT_ID=your-project-id
```

### Verify Configuration
```bash
# Check agent status
python -c "from app.agent_enhanced import AzureAIFoundryAgent; print(AzureAIFoundryAgent().get_status())"

# Check Azure CLI
az --version
az account show
az extension list
```

---

## 🚀 Running Services

### Start Backend
```bash
# Terminal 1
python -m uvicorn app.main:app --reload
# Or on specific port:
python -m uvicorn app.main:app --reload --port 8000
```

### Start Frontend
```bash
# Terminal 2
streamlit run streamlit_app.py
# Or on specific port:
streamlit run streamlit_app.py --server.port 8502
```

### Test API Endpoint
```bash
# Terminal 3
curl -X POST http://localhost:8000/api/rag/generate-poc \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-123",
    "title": "Enterprise AI Chatbot",
    "solution_area": "AI",
    "complexity": "L400",
    "requirements": "Multi-region deployment with high availability"
  }'
```

---

## 📊 Test Coverage Summary

**50+ Tests Across 2 Suites:**

```bash
# Endpoint Tests (39 tests)
- Health checks (2)
- Session management (7)
- POC generation (5)
- Search (5)
- History (2)
- Agent integration (10)
- Error handling (3)
- Data validation (3)
- Performance (2)

# CSA Scenarios (6 main scenarios, 18 tests)
- Enterprise AI Chatbot (3 tests)
- Healthcare Analytics (3 tests)
- Cloud Migration (3 tests)
- ML Trading Platform (2 tests)
- IoT Edge Platform (2 tests)
- SaaS Platform (2 tests)
- Validation tests (1 test)
```

### Run Everything
```bash
# Full test suite with report
pytest test_*.py -v --tb=short --cov=app --cov-report=term-missing
```

---

## 🎯 CSA Scenario Testing

### Test Each Scenario
```bash
# Scenario 1: Enterprise AI Chatbot
pytest test_csa_scenarios.py::TestCSAL400Scenarios::test_scenario_1_enterprise_ai_chatbot_basic -v

# Scenario 2: Healthcare Analytics
pytest test_csa_scenarios.py::TestCSAL400Scenarios::test_scenario_2_secure_analytics_basic -v

# Scenario 3: Cloud Migration
pytest test_csa_scenarios.py::TestCSAL400Scenarios::test_scenario_3_cloud_migration_basic -v

# Scenario 4: ML Trading Platform
pytest test_csa_scenarios.py::TestCSAL400Scenarios::test_scenario_4_ml_platform_basic -v

# Scenario 5: IoT Platform
pytest test_csa_scenarios.py::TestCSAL400Scenarios::test_scenario_5_iot_edge_basic -v

# Scenario 6: SaaS Platform
pytest test_csa_scenarios.py::TestCSAL400Scenarios::test_scenario_6_saas_platform_basic -v
```

### Test RBAC Generation (All Scenarios)
```bash
pytest test_csa_scenarios.py -k "rbac" -v
```

### Test Deployment Scripts (All Scenarios)
```bash
pytest test_csa_scenarios.py -k "deployment" -v
```

### Test IaC Templates (All Scenarios)
```bash
pytest test_csa_scenarios.py -k "iac" -v
```

---

## 🔧 Troubleshooting Commands

### Check What's Running
```bash
# Windows - Check ports
netstat -ano | findstr :8000
netstat -ano | findstr :8501

# Linux/Mac - Check ports
lsof -i :8000
lsof -i :8501
```

### Kill Processes
```bash
# PowerShell
Get-Process | Where-Object {$_.Port -eq 8000} | Stop-Process

# Linux/Mac
kill -9 $(lsof -ti :8000)
```

### Check Virtual Environment
```bash
python -m venv --version
which python
pip list | grep fastapi
```

### Clear Python Cache
```bash
# Remove cache files
rm -r __pycache__
rm -r .pytest_cache
rm -r app/__pycache__

# Or Windows
rmdir /s __pycache__
rmdir /s .pytest_cache
rmdir /s app\__pycache__
```

---

## 📈 Performance Debugging

### Time Individual Tests
```bash
pytest test_all_endpoints.py -v --durations=10
# Shows slowest 10 tests
```

### Profile Agent Responses
```bash
python -c "
import time
from app.agent_enhanced import AzureAIFoundryAgent

agent = AzureAIFoundryAgent()
session_id = agent.create_session()

start = time.time()
response = agent.send_message(
    session_id=session_id,
    message='Test message'
)
elapsed = time.time() - start

print(f'Response time: {elapsed:.2f}s')
print(f'Tools used: {response.tools_used}')
"
```

### Check Agent Status
```bash
python -c "
from app.agent_enhanced import AzureAIFoundryAgent
import json

agent = AzureAIFoundryAgent()
status = agent.get_status()
print(json.dumps(status, indent=2))
"
```

---

## 🧹 Cleanup

### Clean Test Data
```bash
# Remove all sessions (if database cleanup implemented)
# Depends on your session storage implementation
```

### Clean Test Artifacts
```bash
rm -r .pytest_cache
rm -r htmlcov
rm .coverage
rm -r __pycache__
```

### Clean Azure (Delete Resources)
```bash
# WARNING: This deletes everything!
az group delete \
  --name contoso-ai-rg \
  --yes --no-wait
```

---

## 📝 Test Result Interpretation

### Green ✅
```
PASSED - Test ran successfully
```

### Red ❌
```
FAILED - Test assertion failed
ERROR - Exception during test execution
```

### Common Error Messages

**"Connection refused"**
```
→ Start backend: python -m uvicorn app.main:app --reload
```

**"No module named 'pytest'"**
```
→ Install: pip install pytest
```

**"AZURE_OPENAI_ENDPOINT not configured"**
```
→ Run setup_azure_agent.py or create .env file
```

**"Test timeout"**
```
→ Increase timeout: pytest --timeout=60
→ Or check system performance
```

---

## 🎓 Example Test Run

```bash
# Terminal
C:\System3-RAG> pytest test_all_endpoints.py::TestSessionManagement -v

test_all_endpoints.py::TestSessionManagement::test_create_session PASSED
test_all_endpoints.py::TestSessionManagement::test_get_session PASSED
test_all_endpoints.py::TestSessionManagement::test_session_not_found PASSED
test_all_endpoints.py::TestSessionManagement::test_export_session PASSED
test_all_endpoints.py::TestSessionManagement::test_delete_session PASSED

=============== 5 passed in 0.23s ================
```

---

## 🚀 One-Liner Commands

### Setup and Test Everything
```bash
python setup.py && pytest test_all_endpoints.py test_csa_scenarios.py -v
```

### Setup Azure and Run Tests
```bash
python setup_azure_agent.py --subscription abc123 --resource-group test && pytest test_csa_scenarios.py -v
```

### Start Services and Run Tests
```bash
start "Backend" python -m uvicorn app.main:app --reload && start "Streamlit" streamlit run streamlit_app.py && pytest test_all_endpoints.py -v
```

---

## 📞 Support

**Need help?** Check these in order:

1. **TESTING_GUIDE.md** - Full testing documentation
2. **README.md** - System overview
3. **STREAMLIT_QUICKSTART.md** - UI setup guide
4. **Code comments** - In-file documentation

---

**Last Updated**: February 2026  
**Status**: ✅ Ready to Use  
**Total Tests**: 50+ across 2 suites

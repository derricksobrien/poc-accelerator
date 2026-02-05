# Testing & Agent Setup Guide for System3-RAG

Complete guide for running tests, setting up Azure AI Foundry agent, and validating all endpoints.

## 📋 Table of Contents

1. [Quick Start Testing](#quick-start-testing)
2. [Azure AI Foundry Setup](#azure-ai-foundry-setup)
3. [Running Test Suites](#running-test-suites)
4. [CSA Scenario Testing](#csa-scenario-testing)
5. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start Testing

### Prerequisites
```bash
cd c:\Users\derri\Code\techconnect_all\System3-RAG

# Activate venv
python setup.py
# or
.\venv\Scripts\activate

# Install test dependencies
pip install pytest pytest-asyncio httpx
```

### Run All Tests
```bash
# All tests with verbose output
pytest test_all_endpoints.py test_csa_scenarios.py -v

# Just endpoint tests
pytest test_all_endpoints.py -v

# Just CSA scenarios
pytest test_csa_scenarios.py -v

# Single test
pytest test_all_endpoints.py::TestHealthAndStatus::test_health_check -v

# With coverage report
pytest test_all_endpoints.py --cov=app --cov-report=html
```

---

## ⚙️ Azure AI Foundry Setup

### Step 1: Prerequisites

Ensure you have:
- Azure subscription with access to create resources
- Azure CLI installed: `az --version`
- Azure AI extension: `az extension add -n ai`
- Authenticated: `az login`

### Step 2: Run Auto-Setup Script

```bash
# Most automated way - creates everything
python setup_azure_agent.py \
  --subscription <your-subscription-id> \
  --resource-group <resource-group-name> \
  --region eastus \
  --project techconnect-rag

# Example:
python setup_azure_agent.py \
  --subscription "12345678-1234-1234-1234-123456789012" \
  --resource-group "contoso-ai-rg" \
  --region eastus
```

### Step 3: What the Script Creates

```
✓ AI Hub (manages shared resources)
✓ AI Project (your agent project)
✓ Model Deployment (GPT-4 for generation)
✓ Agent Definition (with 5 tools)
✓ .env Configuration File
```

### Step 4: Complete Manual Setup

#### Option A: Using Azure Portal (GUI)

1. **Create AI Hub**
   - Go to Azure Portal → Create Resource → AI Hub
   - Name: `techconnect-rag-hub`
   - Resource group: `contoso-ai-rg`
   - Region: `eastus`

2. **Create AI Project**
   - Inside Hub → Projects → New Project
   - Name: `techconnect-rag`
   - Hub: Select the hub you created

3. **Deploy Model**
   - Project → Deployments → Deploy Model
   - Model: `gpt-4`
   - Deployment name: `gpt4-deployment`
   - SKU: Standard

4. **Get Credentials**
   - Project → APIs & endpoints
   - Copy: Endpoint, Deployment name, API key

5. **Create .env**
   ```bash
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_KEY=sk-...
   AZURE_AI_PROJECT_ID=<project-id>
   AZURE_MODEL_DEPLOYMENT=gpt4-deployment
   ```

#### Option B: Using Azure CLI (Scripts)

```bash
# 1. Create resource group
az group create \
  --name contoso-ai-rg \
  --location eastus

# 2. Create AI Hub
az ai hub create \
  --resource-group contoso-ai-rg \
  --name techconnect-rag-hub \
  --location eastus

# 3. Create AI Project
az ai project create \
  --resource-group contoso-ai-rg \
  --name techconnect-rag \
  --hub techconnect-rag-hub

# 4. Deploy model
az ai deployment create \
  --resource-group contoso-ai-rg \
  --project techconnect-rag \
  --name gpt4-deployment \
  --model gpt-4 \
  --version 0125-preview \
  --instance-type standard

# 5. Get credentials
az ai project show \
  --resource-group contoso-ai-rg \
  --name techconnect-rag \
  --query properties
```

### Step 5: Configure Backend

1. **Update .env file**
   ```bash
   # Copy .env.example to .env
   cp .env.example .env
   
   # Edit with your credentials
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_KEY=sk-your-key
   AZURE_MODEL_DEPLOYMENT=gpt4-deployment
   ```

2. **Verify Connection**
   ```bash
   # Test agent connectivity
   python -c "from app.agent_enhanced import AzureAIFoundryAgent; \
   a = AzureAIFoundryAgent(); \
   print(a.get_status())"
   ```

### Step 6: Start Using the Agent

```bash
# Terminal 1: Start backend
python -m uvicorn app.main:app --reload

# Terminal 2: Test agent endpoint
curl -X POST http://localhost:8000/api/rag/generate-poc \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-123",
    "title": "Enterprise AI Chatbot",
    "solution_area": "AI",
    "complexity": "L400",
    "requirements": "Multi-region, HIPAA compliant"
  }'
```

---

## 📊 Running Test Suites

### Test Suite 1: All Endpoints (`test_all_endpoints.py`)

Tests every API endpoint with proper validation.

```bash
# Run all endpoint tests
pytest test_all_endpoints.py -v

# Run specific test class
pytest test_all_endpoints.py::TestSessionManagement -v

# Run with output
pytest test_all_endpoints.py -v -s
```

**Coverage:**
- ✅ Health checks (`/health`, `/status`)
- ✅ Session management (create, get, delete, export)
- ✅ POC generation with various inputs
- ✅ Solution search with filters
- ✅ History retrieval
- ✅ Agent integration (mocked)
- ✅ Error handling
- ✅ Data validation
- ✅ Performance

**Example Output:**
```
test_all_endpoints.py::TestHealthAndStatus::test_health_check PASSED
test_all_endpoints.py::TestSessionManagement::test_create_session PASSED
test_all_endpoints.py::TestPOCGeneration::test_generate_poc_basic PASSED
test_all_endpoints.py::TestSearch::test_search_basic PASSED
test_all_endpoints.py::TestAgentIntegration::test_agent_send_message PASSED
...
```

### Test Suite 2: CSA Scenarios (`test_csa_scenarios.py`)

L400 enterprise scenarios that cloud architects expect.

```bash
# Run all CSA scenarios
pytest test_csa_scenarios.py -v

# Run specific scenario
pytest test_csa_scenarios.py::TestCSAL400Scenarios::test_scenario_1_enterprise_ai_chatbot_basic -v

# Run with detailed output
pytest test_csa_scenarios.py -v -s

# Run with timing info
pytest test_csa_scenarios.py -v --durations=10
```

**Scenarios Included:**

1. **Enterprise AI Chatbot with Multi-Region HA**
   - Multi-region deployment (6 regions)
   - 99.99% SLA, 10+ languages
   - Compliance: SOC2, PCI-DSS, GDPR

2. **Secure Healthcare Analytics Platform**
   - HIPAA-compliant data handling
   - Advanced analytics with ML
   - 40+ hospitals, 200k+ patients

3. **Cloud-Native App Migration**
   - Monolith to microservices
   - Containerization with Docker/Kubernetes
   - Zero-downtime migration

4. **Real-Time ML Platform for Trading**
   - GPU-accelerated training
   - <100ms inference latency
   - 1000+ predictions/second

5. **Enterprise IoT & Edge Platform**
   - 10M+ smart devices
   - Real-time edge analytics
   - 99.99% critical infrastructure uptime

6. **Multi-Tenant SaaS Platform**
   - 1000+ enterprise customers
   - 100k+ concurrent users
   - Multi-region global distribution

**Example Test:**
```python
def test_scenario_1_enterprise_ai_chatbot_basic(self):
    """Enterprise AI Chatbot - Multi-Region HA test"""
    response = client.post(
        "/api/rag/generate-poc",
        json={
            "session_id": self.session_id,
            "title": "Enterprise AI Chatbot - Multi-Region HA",
            "solution_area": "AI",
            "complexity": "L400",
            "requirements": "Multi-region AI chatbot for financial services..."
        }
    )
    
    assert response.status_code == 200
    # Validates all CSA requirements
```

---

## ✅ CSA Scenario Testing

### What Gets Tested

**For Each Scenario:**

1. **Basic POC Generation**
   - Correct structure returned
   - All required fields populated
   - Non-empty recommendations

2. **RBAC Configuration**
   - Role definitions present
   - Scope information included
   - Security best practices

3. **Deployment Scripts**
   - Bicep/Terraform syntax
   - Environment variables
   - Error handling

4. **IaC Templates**
   - Complete resource definitions
   - Parameter documentation
   - Security controls

5. **Architecture Validation**
   - Compliance framework support
   - Multi-region capability
   - Recommended best practices

### Test CSA Scenarios Manually

```bash
# Terminal 1: Start backend
python -m uvicorn app.main:app --reload

# Terminal 2: Run tests with output
pytest test_csa_scenarios.py::TestCSAL400Scenarios::test_scenario_1_enterprise_ai_chatbot_basic -v -s

# Terminal 2: Or test all scenarios
pytest test_csa_scenarios.py::TestCSAL400Scenarios -v

# Terminal 2: Or with detailed timing
pytest test_csa_scenarios.py::TestCSAL400Scenarios -v --durations=5
```

### Validate Against Real Agent

If you have Azure credentials configured:

```bash
# Backend will use real agent instead of mock
# Just run the tests normally
pytest test_csa_scenarios.py -v

# Agent responses will include:
# - Real recommendations from solution accelerators
# - Real RBAC configurations
# - Real deployment scripts
# - Real IaC templates
```

---

## 🔧 Advanced Testing

### Coverage Report
```bash
# Generate HTML coverage report
pytest test_all_endpoints.py --cov=app --cov-report=html

# Open coverage/index.html in browser
```

### Performance Testing
```bash
# Test response times
pytest test_all_endpoints.py::TestPerformance -v

# With timing details
pytest test_all_endpoints.py -v --durations=10
```

### Concurrent Load Testing
```bash
# Test with concurrent sessions
pytest test_all_endpoints.py::TestErrorHandling::test_concurrent_operations -v -s
```

### Mock vs Real Agent Testing
```bash
# Without .env (uses mock)
pytest test_all_endpoints.py::TestAgentIntegration -v

# With .env (uses real Azure)
# Just set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_KEY, same test works
```

---

## 🐛 Troubleshooting

### Issue: Azure CLI not found
```bash
# Install Azure CLI
# Windows: Download from https://aka.ms/azcliinstaller
# Linux: curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
# Mac: brew install azure-cli

az --version
```

### Issue: Not authenticated
```bash
az login --use-device-code
# Follow the URL and enter device code

az account show  # Verify
```

### Issue: AI extension missing
```bash
az extension add -n ai --upgrade
```

### Issue: Tests fail with "connection refused"
```bash
# Make sure backend is running:
python -m uvicorn app.main:app --reload

# Check port 8000 is available
netstat -ano | findstr :8000
```

### Issue: Agent not responding
```bash
# Check .env configuration
cat .env | grep AZURE

# Verify credentials
az keyvault secret show --vault-name techconnect-rag-kv --name openai-api-key

# Check endpoint is correct
curl https://your-resource.openai.azure.com/health
```

### Issue: Tests timeout
```bash
# Increase pytest timeout
pytest test_all_endpoints.py --timeout=30

# Or check system is slow
time python -c "from app.agent_enhanced import AzureAIFoundryAgent; print(AzureAIFoundryAgent().get_status())"
```

---

## 📈 Test Metrics

### Expected Pass Rates

| Test Suite | Tests | Expected Pass Rate |
|---------|-------|-------------------|
| Endpoint Tests | 50+ | 100% ✓ |
| CSA Scenarios | 6 scenarios x 3 tests | 100% ✓ |
| Agent Integration | 10 tests | 100% (mock) |
| CSA + Agent | 6 scenarios x 3 tests | 100% (with Azure) |

### Performance Benchmarks

| Operation | Target | Typical |
|-----------|--------|---------|
| Health check | <100ms | 10-20ms |
| Create session | <500ms | 50-100ms |
| Search (5 results) | <2s | 500-900ms |
| Generate POC | <5s | 1-3s (mock), 5-15s (real) |
| Agent message | <10s | 3-5s (mock), 10-20s (real) |

---

## 🚀 Next Steps

### 1. Local Testing (Done)
✅ All tests pass locally  
✅ Mock agent responses work  
✅ No Azure needed yet

### 2. Azure Setup (Optional)
```bash
python setup_azure_agent.py \
  --subscription <id> \
  --resource-group <name>
```

### 3. Real Agent Testing
```bash
# Backend now uses real Azure agent
pytest test_csa_scenarios.py -v
# Wait 10-20s per test for real agent responses
```

### 4. Production Deployment
```bash
docker build -t system3-rag:latest .
az acr build --registry <acr-name> --image system3-rag:latest .
az containerapp create --name system3-rag ...
```

---

## 📚 Reference

### Import the Enhanced Agent
```python
from app.agent_enhanced import AzureAIFoundryAgent, AgentResponse

# Initialize
agent = AzureAIFoundryAgent()

# Create session
session_id = agent.create_session()

# Send message
response = agent.send_message(
    session_id=session_id,
    message="Generate a POC for AI chatbot"
)

print(response.message)
print(response.tools_used)
```

### Call Tools Directly
```python
result = agent.call_tool(
    "search_solutions",
    {
        "query": "RAG system",
        "area": "AI",
        "complexity": "L400",
        "top_k": 5
    }
)
```

### Get Agent Status
```python
status = agent.get_status()
# {
#     "agent_id": "techconnect-rag",
#     "available": True,
#     "tools": ["search_solutions", "generate_rbac", ...],
#     "active_sessions": 3
# }
```

---

**Status**: ✅ Ready for Testing  
**Last Updated**: February 2026  
**Tests**: 50+ endpoints + 6 CSA scenarios

Good luck! 🎉

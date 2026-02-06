# System3-RAG: Azure AI Foundry Agent-Based POC Generator

**Next Generation POC Generator with Streamlit UI and Azure AI Foundry Agents**

AI-powered, agent-based architecture that combines intelligent orchestration with a beautiful, responsive user interface.

---

## 🎯 Quick Start (5 Minutes)

### Setup with Virtual Environment

```bash
# Run setup script (creates venv automatically)
python setup.py

# Or manually:
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\Activate.ps1 on Windows
pip install -r requirements.txt
```

### Run (Two Terminals)

**Terminal 1 - FastAPI Backend:**
```bash
python -m uvicorn app.main:app --reload
```

**Terminal 2 - Streamlit Frontend:**
```bash
streamlit run streamlit_app.py
```

**Open browser:** http://localhost:8501

---

## 🎨 User Interface (Streamlit)

The frontend is built with **Streamlit**, a Python framework for building interactive apps instantly.

### Tab 1: 🚀 Generate POC
Generate enterprise-grade POCs with agent intelligence
- Input: Solution area, title, detailed requirements, number of results
- Output: Recommendations, RBAC roles, deployment scripts, IaC templates, cost estimates

### Tab 2: 💬 Agent Chat  
Multi-turn conversation with Azure AI Foundry agents
- Ask about solutions, architecture, best practices
- Agent maintains conversation context
- Responses grounded in solution catalog

### Tab 3: 🔍 Search Solutions
Search the 15-solution Microsoft accelerators catalog
- Semantic search across solutions
- Configurable result count
- Optional agent synthesis of recommendations

### Tab 4: 📋 History
View all POCs generated in current session
- Complete generation history with timestamps
- Status tracking (completed, in-progress, failed)
- Export individual POCs or entire session

### Tab 5: ⚙️ System Status
Monitor system health and configuration
- API endpoint health checks
- Session information
- Configuration validation

---

## 📁 Project Structure

```
System3-RAG/
├── app/
│   ├── __init__.py                    # Package marker
│   ├── main.py                        # FastAPI server (15KB)
│   ├── agent.py                       # Azure AI Foundry client (12KB)
│   └── session.py                     # Session management (18KB)
│
├── streamlit_app.py                   # Main Streamlit UI (20KB)
│
├── .streamlit/
│   └── config.toml                    # Streamlit configuration
│
├── setup.py                           # Cross-platform setup script
├── setup.ps1                          # Windows PowerShell setup
├── setup.sh                           # Linux/MacOS setup
│
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment template
├── Dockerfile                         # Container build
├── docker-compose.yml                 # Docker Compose setup
│
└── README.md                          # This file
```

---

## 🚀 Features

### Agent-Powered Intelligence
✅ Multi-turn conversations with Azure AI Foundry agents  
✅ Tool invocation (search, RBAC generation, scripts, IaC)  
✅ Grounded responses with source citations  

### Session Management
✅ Per-user conversation history  
✅ POC generation tracking with timestamps  
✅ Automatic cleanup of expired sessions  
✅ Export/import full session state  

### Beautiful UI
✅ 5-tab responsive Streamlit interface  
✅ Real-time updates and live feedback  
✅ Native Streamlit components for data display  
✅ Mobile-friendly design  

### Production Ready
✅ Docker containerization  
✅ Health checks for orchestration  
✅ CORS properly configured  
✅ Comprehensive error handling  

---

## 🔧 Configuration

### Environment Variables (.env)

```env
# API Configuration
API_BASE_URL=http://localhost:8000/api

# Azure AI Foundry (optional, for real agent)
AI_FOUNDRY_ENDPOINT=https://your-aifoundry.openai.azure.com/
AI_FOUNDRY_KEY=your-api-key
AI_FOUNDRY_AGENT_ID=your-agent-uuid

# Session Configuration
SESSION_TIMEOUT_MINUTES=60

# Logging
LOG_LEVEL=INFO
```

### Streamlit Configuration (.streamlit/config.toml)

```toml
[theme]
primaryColor = "#4c63d2"
backgroundColor = "#ffffff"
font = "sans serif"

[server]
port = 8501
runOnSave = true
```

---

## 🚢 Docker Deployment

### Local Development

```bash
# Build and run together
docker-compose up --build

# Access:
# Frontend: http://localhost:8501
# Backend:  http://localhost:8000
```

### Build for Azure

```bash
docker build -t system3-rag:latest .

# Push to Azure Container Registry
az acr build --registry myregistry --image system3-rag:latest .
```

---

## 🧪 Testing

### Manual Testing

1. **Start both services**
   ```bash
   # Terminal 1
   python -m uvicorn app.main:app --reload
   
   # Terminal 2
   streamlit run streamlit_app.py
   ```

2. **Test features**
   - Generate POC (demo mode works without Azure)
   - Search solutions
   - View history
   - Export session

### API Endpoint Testing

```bash
# Create session
curl -X POST http://localhost:8000/api/rag/session/create \
  -H "Content-Type: application/json"

# Generate POC
curl -X POST "http://localhost:8000/api/rag/generate-poc?session_id=YOUR_ID" \
  -H "Content-Type: application/json" \
  -d '{"solution_area": "AI", "poc_title": "Test", "query": "automation", "top_results": 5}'
```

---

## 🎓 Next Steps

### Short Term
- [ ] Connect to live Azure AI Foundry agent
- [ ] Index solution catalog to Azure AI Search  
- [ ] Test POC generation with real agent

### Medium Term
- [ ] Add database for session persistence
- [ ] Implement user authentication
- [ ] Add more agent tools

### Long Term
- [ ] Deploy to Azure Container Apps
- [ ] Scale with multiple agent instances
- [ ] Add advanced analytics

---

**Status**: ✅ Streamlit UI Complete  
**Next Phase**: Azure AI Foundry Agent Integration  
**Timeline**: 2-3 days for full agent connectivity

---

*© 2026 System3-RAG | Azure AI Foundry Agent-Based POC Generator | Streamlit + FastAPI + Azure*

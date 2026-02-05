# System3-RAG: Streamlit UI - Quick Start Guide

## ⚡ 3-Minute Setup

### 1. Create Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Linux/MacOS (Bash):**
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Start Two Services

**Terminal 1 - Backend**
```bash
python -m uvicorn app.main:app --reload
```
👉 http://localhost:8000 (API)  
👉 http://localhost:8000/docs (API docs)

**Terminal 2 - Frontend**
```bash
streamlit run streamlit_app.py
```
👉 http://localhost:8501 (Streamlit UI)

### 3. Open Browser
```
http://localhost:8501
```

---

## 🎨 What You Get

### 5 Interactive Tabs

#### Generate POC
- Fill in solution area, title, requirements
- Click "Generate POC with Agent"
- Get recommendations, RBAC, scripts, IaC templates
- Download as JSON

#### Agent Chat
- Click in chat box
- Ask questions: "What's multi-agent automation?"
- Multi-turn conversation
- Connected to Azure AI Foundry (when configured)

#### Search Solutions
- Enter query: "cloud transformation", "AI automation", etc.
- See 15 solutions from catalog
- Optional agent synthesis of recommendations

#### History
- View all POCs generated
- See timestamps and status
- Export session data

#### System Status
- Check API health
- View configuration
- Verify agent readiness

---

## 🔧 Setup Scripts (Automated)

### Cross-Platform Python Script
```bash
python setup.py
# Creates venv + installs dependencies
# Shows status and instructions
```

### Windows PowerShell Script
```powershell
.\setup.ps1
# Creates venv + installs dependencies
# Shows status and instructions
```

### Linux/MacOS Bash Script
```bash
bash setup.sh
# Creates venv + installs dependencies
# Shows status and instructions
```

---

## 📂 Key Files Explained

| File | Purpose |
|------|---------|
| `streamlit_app.py` | Main Streamlit app (20KB) |
| `app/main.py` | FastAPI backend (15KB) |
| `app/agent.py` | Azure AI Foundry client (12KB) |
| `app/session.py` | Session management (18KB) |
| `.streamlit/config.toml` | Streamlit settings |
| `requirements.txt` | All Python packages |

---

## 🚀 Common Commands

### Run with Fresh Venv
```bash
# Windows
python setup.py
.\venv\Scripts\Activate.ps1

# Linux/Mac
python setup.py
source venv/bin/activate
```

### Run Backend Only (API)
```bash
python -m uvicorn app.main:app --reload
```

### Run Frontend Only (Streamlit)
```bash
streamlit run streamlit_app.py
```

### Run Both (Docker)
```bash
docker-compose up --build
```

### Check System Health
```bash
curl http://localhost:8000/health
curl http://localhost:8000/status
```

---

## 🧪 Testing Without Azure

**All features work in demo mode:**
- ✅ Generate POC (mock response)
- ✅ Search solutions (from catalog)
- ✅ Chat tab (mock responses)
- ✅ History (tracks locally)
- ✅ Export session

No Azure credentials needed to test!

---

## 🔌 Connect to Azure (Optional)

### Get Credentials
1. Go to Azure Portal
2. Create Azure AI Foundry resource
3. Create or note Agent ID
4. Get API key and endpoint

### Update .env
```bash
cp .env.example .env
# Edit .env with your values
```

### Set Variables
```env
AI_FOUNDRY_ENDPOINT=https://your-aifoundry.openai.azure.com/
AI_FOUNDRY_KEY=your-api-key
AI_FOUNDRY_AGENT_ID=your-agent-uuid
```

### Restart Backend
```bash
# Kill current process (Ctrl+C)
# Run again
python -m uvicorn app.main:app --reload
```

---

## 🐳 Docker

### Build
```bash
docker build -t system3-rag:latest .
```

### Run Local
```bash
docker run -p 8501:8501 -p 8000:8000 system3-rag:latest
```

### Run with Docker Compose
```bash
docker-compose up --build
# Frontend: http://localhost:8501
# Backend:  http://localhost:8000
```

---

## 🎯 Feature Walkthrough

### 1. Generate POC
1. Click "Generate POC" tab
2. Select "AI" from Solution Area
3. Title: "Enterprise Automation"
4. Requirements: "Multi-agent system for order processing"
5. Click "Generate POC with Agent"
6. See results in tabs:
   - 📚 Recommendations (which solutions)
   - 🔐 RBAC (roles needed)
   - 🚀 Scripts (deployment code)
   - 🏗️ IaC (Bicep/Terraform)
   - 📊 Architecture (summary)

### 2. Search Solutions
1. Click "Search Solutions" tab
2. Enter: "cloud transformation"
3. Set results: 5
4. Check "Include Synthesis"
5. Click "Search"
6. See results with match percentages

### 3. Agent Chat
1. Click "Agent Chat" tab
2. Try: "What is Semantic Kernel?"
3. Get response
4. Ask follow-up questions
5. Multi-turn conversation

### 4. View History
1. Click "POC History" tab
2. See all generated POCs
3. Click export button to download
4. Status shows: completed/failed/in-progress

### 5. System Status
1. Click "System Status" tab
2. Click "Check Health"
3. See API status
4. Verify agent configuration

---

## ❓ Troubleshooting

### "Failed to connect to API"
```bash
# Check backend is running
curl http://localhost:8000/health

# Should see: {"status": "healthy", "service": "System3-RAG"}
```

### Streamlit stuck on loading
```bash
# Press Ctrl+C in Streamlit terminal
# Restart:
streamlit run streamlit_app.py
```

### Port already in use
```bash
# Backend on different port
python -m uvicorn app.main:app --port 9000

# Frontend on different port  
streamlit run streamlit_app.py --server.port 8502
```

### Session not persisting
- Sessions only last ~60 minutes of inactivity
- Refresh clears browser session
- Click "New Session" to start fresh

---

## 📊 Architecture at a Glance

```
Streamlit (UI)
    ↓ HTTP requests
FastAPI (Backend API)
    ↓ Calls
Azure AI Foundry Agent (when configured)
    ↓ Uses
Azure AI Search + 15-solution catalog
```

---

## 🎓 Next Steps

### Try These in Order:
1. ✅ Run both services successfully (this quickstart)
2. ✅ Test Generate POC with mock data
3. ✅ Try searching solutions
4. ⏳ Connect Azure AI Foundry agent
5. ⏳ Test real agent responses
6. ⏳ Deploy to Azure

---

## 📞 Need Help?

### Check These First:
1. Is backend running? `curl http://localhost:8000/health`
2. Is frontend running at 8501? Check terminal output
3. Are both services in same venv? Yes for pip install
4. Browser console (F12) for JavaScript errors

### Common Fixes:
- Kill and restart services
- Clear browser cache (Ctrl+Shift+Del)
- Deactivate and reactivate venv
- `pip install -r requirements.txt` again

---

## 🚀 You're Ready!

**Next: Open http://localhost:8501 and try it out!**

---

*System3-RAG with Streamlit | Feb 2026*

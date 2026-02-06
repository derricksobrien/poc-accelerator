# System3-RAG Quick Start Guide

Get System3-RAG running in 10 minutes without Azure dependencies.

---

## ⚡ 1-Minute Setup

### Windows PowerShell
```powershell
# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run server
python -m uvicorn app.main:app --reload
```

### Linux/MacOS
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run server
python -m uvicorn app.main:app --reload
```

**Server runs at:** `http://localhost:8000`

---

## 🐳 Docker Quick Start (2 Minutes)

```bash
# Build and run with docker-compose
docker-compose up --build

# Or manually:
docker build -t system3-rag:latest .
docker run -p 8000:8000 system3-rag:latest
```

**Access at:** `http://localhost:8000`

---

## 🧪 Test Without Azure

All 5 tabs work in demo mode without Azure credentials:

### Tab 1: Generate POC
1. Navigate to "Generate POC" tab
2. Fill form:
   - Solution Area: "AI"
   - POC Title: "Test POC"
   - Query: "multi-agent system"
   - Top Results: 5
3. Click "Generate POC with Agent"
4. See mock response with recommendations, RBAC, scripts

### Tab 2: Agent Chat
1. Click "Agent Chat" tab
2. Type a message: "What is multi-agent automation?"
3. See mock agent response

### Tab 3: Search Solutions
1. Enter search: "AI automation"
2. See 15 solutions from catalog
3. Check "Include Agent Synthesis" for recommendations

### Tab 4: POC History
1. Generate a few POCs
2. View them in history tab
3. Try "Export" button to download session

### Tab 5: System Status
1. Click "System Status" tab
2. Click "Check Status"
3. See system info and health

---

## 📊 Session Management

**Automatic:**
- ✅ Session ID generated on first visit
- ✅ Stored in localStorage (survives page refresh)
- ✅ POC history tracked per session
- ✅ Sessions expire after 60 minutes of inactivity

**Manual:**
- 🔆 "New Session" button in top bar creates fresh session
- 💾 "Export" button downloads entire session as JSON

---

## 🔌 API Endpoints (With curl)

### Create Session
```bash
curl -X POST http://localhost:8000/api/rag/session/create \
  -H "Content-Type: application/json" \
  -d '{"metadata": {"user": "test"}}'

# Returns: {"session_id": "uuid", "created_at": "...", "user_id": null}
```

### Generate POC
```bash
curl -X POST "http://localhost:8000/api/rag/generate-poc?session_id=YOUR_SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "solution_area": "AI",
    "poc_title": "Enterprise AI",
    "query": "multi-agent automation",
    "top_results": 5
  }'

# Returns: Full POC with recommendations, RBAC, scripts, IaC
```

### Search Solutions
```bash
curl -X POST "http://localhost:8000/api/rag/search?session_id=YOUR_SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "cloud transformation",
    "top_k": 3,
    "include_synthesis": true
  }'

# Returns: Solutions matching query + agent synthesis
```

### Get Session History
```bash
curl http://localhost:8000/api/rag/history?session_id=YOUR_SESSION_ID

# Returns: All POCs generated in session
```

### System Health
```bash
curl http://localhost:8000/health
# Returns: {"status": "healthy", "service": "System3-RAG", "version": "1.0.0"}

curl http://localhost:8000/status
# Returns: Detailed statistics and configuration
```

---

## 🎨 UI Features

### Session Bar (Top)
- Shows current session ID
- "New Session" - Create fresh session
- "Export" - Download all session data as JSON

### 5 Tabs

| Tab | Purpose | Actions |
|-----|---------|---------|
| **Generate POC** | Create enterprise POCs | Submit form → Get recommendations, RBAC, scripts, IaC |
| **Agent Chat** | Multi-turn conversation | Chat with agent about solutions |
| **Search Solutions** | Find relevant solutions | Search + get synthesis |
| **POC History** | Review generated POCs | View all POCs from session |
| **System Status** | Health & diagnostics | Check API health, environment, config |

---

## 📁 Project Structure

```
System3-RAG/
├── app/
│   ├── __init__.py           # Package marker
│   ├── main.py               # FastAPI server (15KB)
│   ├── agent.py              # Azure AI Foundry client (12KB)
│   └── session.py            # Session management (18KB)
├── static/
│   ├── index.html            # 5-tab UI (6KB)
│   ├── script.js             # Client logic (13KB)
│   └── style.css             # Styling (8KB)
├── Dockerfile                # Container build
├── docker-compose.yml        # Local dev setup
├── requirements.txt          # Python dependencies
├── .env.example              # Environment template
├── README.md                 # Architecture overview
├── BUILD_STATUS.md           # Build completion status
└── QUICKSTART.md            # This file
```

---

## 🚀 Next Steps: Connecting to Azure

### When Ready to Connect Azure AI Foundry Agent

1. **Get Agent Credentials**
   ```bash
   # From Azure Portal > AI Foundry > Agent
   # Note: Agent ID, Endpoint, API Key
   ```

2. **Update .env**
   ```bash
   cp .env.example .env
   # Edit .env with real credentials:
   # AI_FOUNDRY_ENDPOINT=https://your-aifoundry.openai.azure.com/
   # AI_FOUNDRY_AGENT_ID=agent-uuid
   # AI_FOUNDRY_KEY=api-key
   ```

3. **Test Agent Connection**
   - Restart server: `python -m uvicorn app.main:app --reload`
   - Open browser, click "System Status" tab
   - Should show "✅ Agent Configured"

4. **Agent Now Powers:**
   - Generate POC → Uses real agent intelligence
   - Search → Gets agent synthesis
   - Chat → Real multi-turn conversation
   - POC History → Agent reasoning included

---

## 🔧 Common Issues

### "Failed to Fetch" Error
**Cause**: Browser trying to reach backend URL incorrectly

**Fix**:
1. Open DevTools (F12)
2. Check Console for `[API]` messages
3. Should show: `API Base URL configured: http://localhost:8000/api`
4. Restart browser if not showing

### Session Not Saving
**Cause**: localStorage disabled or session ID not being passed

**Fix**:
1. Open DevTools > Application > localStorage
2. Should see `system3_session_id` key
3. Check Network tab - POST requests should include `?session_id=...`

### Docker Container Won't Start
**Cause**: Port 8000 already in use

**Fix**:
```bash
# Use different port
docker run -p 9000:8000 system3-rag:latest
# Access at: http://localhost:9000
```

### Slow Performance
**Cause**: Python dependencies compiling on first run

**Fix**:
- First run takes 10-15 seconds
- Subsequent requests are instant
- Check `app/main.py` is using lazy-loading (✅ it does)

---

## 📈 Scaling Up

### Advanced Configuration

**Environment Variables** (in .env):
```env
# Session timeout (default: 60 minutes)
SESSION_TIMEOUT_MINUTES=120

# Server settings
PORT=8000
HOST=0.0.0.0
ENV=production

# Logging
LOG_LEVEL=INFO

# Azure AI Foundry (when ready)
AI_FOUNDRY_ENDPOINT=... (required for agent)
AI_FOUNDRY_KEY=...      (required for agent)
AI_FOUNDRY_AGENT_ID=... (required for agent)
```

### Deployment Options

1. **Local (Development)**
   - `python -m uvicorn app.main:app --reload`

2. **Docker (Staging)**
   - `docker-compose up`

3. **Azure Container Apps (Production)**
   - Build image: `az acr build --registry myregistry --image system3-rag:latest .`
   - Deploy: Standard ACA deployment with env vars

---

## 🎯 What to Try First

### 5-Minute Demo
1. Start server
2. Go to "Generate POC" tab
3. Fill in form and click button
4. See full POC response
5. Click "Download" or "Copy"

### 10-Minute Exploration
1. Try each of the 5 tabs
2. Create 2-3 POCs
3. View them in History
4. Export session
5. Create new session

### Integration (When Azure Ready)
1. Add Azure credentials to .env
2. Implement agent calls in app/main.py
3. Test generate_poc against real agent
4. Update frontend to display agent reasoning

---

## 📞 Need Help?

**Common Questions:**

Q: Can I use this without Azure?
A: Yes! Demo mode works with mock responses. Add Azure credentials for real agent.

Q: How do I save sessions permanently?
A: Currently in-memory. For production, implement database session store (e.g., PostgreSQL).

Q: Can I customize the UI?
A: Yes! Edit static/index.html and static/style.css directly.

Q: How do I add custom solutions to catalog?
A: Copy catalog.json from System2-RAG, edit, restart server.

Q: What Python version is required?
A: Python 3.10+ (tested with 3.12)

---

**Status**: ✅ Ready to Use (Local Mode)  
**Next Phase**: Azure AI Foundry Integration (2-3 days)  
**Final Phase**: Production Deployment (1 day)

Start with local testing, then add Azure credentials when ready!

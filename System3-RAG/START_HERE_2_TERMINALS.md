# 🚀 System3-RAG: 2-Terminal Startup Guide

## ⚡ Fastest Way to Start (2 Methods)

### **METHOD 1: One-Click Startup (Easiest)**

1. **Navigate to:** `C:\Users\derri\Code\techconnect_all\System3-RAG\`
2. **Double-click:** `START_BOTH_TERMINALS.bat` (or `.ps1`)
3. **Wait:** ~5 seconds for both terminals to open
4. **Browser:** Opens automatically to http://localhost:8501
5. **Result:** Both backend and frontend running! 🎉

That's it. You're done.

---

### **METHOD 2: Manual (More Control)**

#### **Terminal 1 - Backend**
```powershell
cd C:\Users\derri\Code\techconnect_all\System3-RAG
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

#### **Terminal 2 - Frontend**
```powershell
cd C:\Users\derri\Code\techconnect_all\System3-RAG
.\.venv\Scripts\Activate.ps1
streamlit run streamlit_app.py
```

#### **Browser**
```
http://localhost:8501
```

---

## 📋 What's Running Where

| Component | Port | Terminal | Command |
|-----------|------|----------|---------|
| **FastAPI Backend** | 8000 | Terminal 1 | `uvicorn app.main:app --reload` |
| **Streamlit Frontend** | 8501 | Terminal 2 | `streamlit run streamlit_app.py` |
| **Agent SDK** | (internal) | Terminal 1 | Runs inside FastAPI |
| **Browser UI** | (local) | Your PC | Auto-opens to :8501 |

---

## ✅ Startup Checklist

### Terminal 1 (Backend) should show:
- [ ] `(.venv)` prefix in prompt
- [ ] `INFO: Uvicorn running on http://127.0.0.1:8000`
- [ ] `INFO: Application startup complete`
- [ ] No red error messages

### Terminal 2 (Frontend) should show:
- [ ] `(.venv)` prefix in prompt
- [ ] `Local URL: http://localhost:8501`
- [ ] `[Ready] ✓` or similar at the top
- [ ] No red error messages

### Browser should show:
- [ ] System3-RAG interface loads
- [ ] 5 tabs visible (Generate POC, Chat, Search, History, Status)
- [ ] No 404 or connection errors

**All checked? You're ready to generate POCs!** 🚀

---

## 🎮 Now What?

### Generate Your First POC

1. **Go to:** 🚀 **Generate POC** tab
2. **Fill in:**
   - Solution Area: Select any option
   - POC Title: Enter something like "Test AI Platform"
   - Requirements: Describe what you want
   - Complexity: Select level
3. **Click:** **"🚀 Generate POC with Multi-Tool Agent"**
4. **Watch:**
   - Terminal 1 shows agent tools executing
   - Terminal 2 shows UI rendering
   - Browser shows results appearing
5. **Explore:**
   - Click tabs to see different outputs
   - Download code sections
   - Edit templates
   - Estimate costs

---

## 📊 Architecture

```
Your Computer (Windows)
├── Terminal 1
│   └─ FastAPI (port 8000)
│      ├─ Azure AI Foundry Agent
│      ├─ Agent Orchestrator (6-step workflow)
│      ├─ Tool Coordina
tor
│      └─ Session Manager
│
├── Terminal 2
│   └─ Streamlit (port 8501)
│      ├─ Rich UI Components
│      ├─ Form Handlers
│      └─ Result Visualization
│
└── Browser
    └─ http://localhost:8501
       └─ System3-RAG Interface
          ├─ 🚀 Generate POC
          ├─ 💬 Agent Chat
          ├─ 🔍 Search Solutions
          ├─ 📋 History
          └─ ⚙️ Status
```

---

## 💡 Important Notes

### Keep Both Running
- **Terminal 1:** Backend must stay open (provides API)
- **Terminal 2:** Frontend must stay open (serves UI)
- If you close either one, that service stops

### Auto-Reload Works
- Change Backend code → Auto-reloads (no restart needed)
- Change Frontend code → Auto-reloads (no restart needed)
- Refresh browser to see changes

### Monitor the Terminals
- **Terminal 1:** Tells you what the API is doing
- **Terminal 2:** Tells you what the UI is doing
- **Red text** = Error (something broke)
- **Yellow text** = Warning (usually OK)
- **Blue/Green text** = Normal operation

---

## 🛠️ Troubleshooting

### "Port 8000 already in use"
```powershell
# In Terminal 1, use a different port:
python -m uvicorn app.main:app --reload --port 8001
# Then access at: http://localhost:8001/docs
```

### "Port 8501 already in use"
```powershell
# In Terminal 2, use a different port:
streamlit run streamlit_app.py --server.port 8502
# Then access at: http://localhost:8502
```

### "Backend and frontend not communicating"
1. Verify Terminal 1 shows "Application startup complete"
2. Verify Terminal 2 shows no red errors
3. Refresh browser (Ctrl+R)
4. Check browser console (F12) for errors
5. Restart both terminals

### "Module not found" error
```powershell
# Make sure you're in System3-RAG directory:
cd C:\Users\derri\Code\techconnect_all\System3-RAG

# And activate venv:
.\.venv\Scripts\Activate.ps1

# Then start the service
```

### "Virtual environment not working"
```powershell
# Try creating a fresh venv:
python -m venv venv_new
.\venv_new\Scripts\Activate.ps1
pip install -r requirements.txt

# Then switch to it
```

---

## 🎯 What's Different Now

### **Before (Simple Chat)**
- ❌ Only conversation interface
- ❌ Limited to chat interactions
- ❌ No code generation
- ❌ No automation features

### **Now (Enterprise POC Generator)**
- ✅ **AI-Powered Agent Orchestration** - 6-step intelligent workflow
- ✅ **Solution Recommendations** - Semantic search with relevance scoring
- ✅ **RBAC Configuration** - Interactive builder with Bicep code generation
- ✅ **Deployment Automation** - Scripts in Bash, PowerShell, validation
- ✅ **IaC Templates** - Bicep, Terraform, ARM with editor & validator
- ✅ **Architecture Validation** - Best practices compliance checks
- ✅ **Cost Estimation** - Component-based with real Azure pricing
- ✅ **Deployment Orchestration** - Step-by-step guided deployment
- ✅ **Export/Download** - All code downloadable in multiple formats
- ✅ **Multi-Session** - Generate multiple POCs, export history

---

## 📚 Files You Need to Know

### Startup Scripts (USE THESE)
- `START_BOTH_TERMINALS.bat` - One-click startup (Windows CMD)
- `START_BOTH_TERMINALS.ps1` - One-click startup (PowerShell)

### Documentation
- `TWO_TERMINAL_SETUP.md` - Detailed setup instructions
- `TWO_TERMINAL_VISUAL_GUIDE.md` - Visual walkthrough with examples
- `ENHANCED_AGENT_FEATURES.md` - Complete feature guide
- `QUICK_REFERENCE.md` - Code examples and quick commands
- `VALIDATION_COMPLETE.md` - Test results and status

### Core Code
- `streamlit_app.py` - Main UI (enhanced)
- `agent_orchestrator.py` - Multi-tool workflow coordinator
- `utils_enhanced.py` - Rich UI components
- `app/main.py` - FastAPI backend
- `app/agent_enhanced.py` - Agent SDK client

---

## 🚀 Quick Commands Reference

```powershell
# Navigate to project
cd C:\Users\derri\Code\techconnect_all\System3-RAG

# Activate environment
.\.venv\Scripts\Activate.ps1

# Terminal 1: Start Backend
python -m uvicorn app.main:app --reload

# Terminal 2: Start Frontend
streamlit run streamlit_app.py

# View API docs (when backend is running)
http://localhost:8000/docs

# Access UI (when frontend is running)
http://localhost:8501

# Run tests (to verify setup)
python test_enhanced_integration.py

# Kill process on a port (if stuck)
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force
```

---

## ⭐ Success Indicators

### You'll know it's working when:

1. **Terminal 1:**
   ```
   INFO:     Uvicorn running on http://127.0.0.1:8000
   INFO:     Application startup complete.
   ```

2. **Terminal 2:**
   ```
   Local URL: http://localhost:8501
   ```

3. **Browser:**
   - System3-RAG interface loads
   - No errors in console (F12)
   - Can click buttons without errors

4. **Generate POC:**
   - Form submits without errors
   - Agent tools execute (see Terminal 1)
   - Results display (see Terminal 2)
   - Tabs populate with code (Bash, Bicep, etc.)

---

## 🎓 Learning Path

### First Time Setup
1. ✅ Read this file
2. ✅ Run startup script
3. ✅ Wait for both terminals
4. ✅ Open browser

### First POC Generation
1. ✅ Go to "Generate POC" tab
2. ✅ Fill in simple details
3. ✅ Click generate button
4. ✅ Watch terminals for output
5. ✅ Explore result tabs

### Going Deeper
1. ✅ Read `ENHANCED_AGENT_FEATURES.md`
2. ✅ Check `QUICK_REFERENCE.md` for code examples
3. ✅ Look at terminals while generating POCs
4. ✅ Edit templates and re-generate
5. ✅ Download and review generated code

---

## 🆘 Getting Help

### Check These First:
- [ ] Both terminals show no red errors?
- [ ] Browser shows UI without errors?
- [ ] Followed the startup steps exactly?
- [ ] Waiting long enough for services to start?

### Then Check:
- [ ] `TWO_TERMINAL_VISUAL_GUIDE.md` - Detailed troubleshooting
- [ ] Browser console (F12) - JavaScript errors?
- [ ] Terminal output - What exact error message?
- [ ] File paths - Are you in right directory?

### Terminal Debugging:
```powershell
# See more detailed logs
python -m uvicorn app.main:app --reload --log-level debug

# Or run tests first
python test_enhanced_integration.py
```

---

## 📊 System Status Commands

While running, check status:

```powershell
# Check if backend is responding
Invoke-WebRequest http://localhost:8000/health

# Check if frontend is running
Invoke-WebRequest http://localhost:8501

# See all Python processes
Get-Process python

# Kill all Python processes (nuclear option)
Get-Process python | Stop-Process -Force
```

---

## ✨ Next Steps After Startup

1. **Explore the UI** - Click each tab
2. **Generate POCs** - Try different inputs
3. **Download Code** - Save generated templates
4. **Edit Templates** - Customize for your needs
5. **Review Costs** - Understand pricing
6. **Check Validation** - See requirements

---

## 🎉 You're Ready!

Everything is set up and ready to go. Just:

1. **Run the startup script** (METHOD 1 above)
2. **Wait for both terminals** to show ready status
3. **Open browser** to http://localhost:8501
4. **Start generating POCs!**

The agent orchestrator handles all the complexity behind the scenes. You just interact with the beautiful UI.

---

## 📞 Quick Reference

**Need to start?**
→ Double-click `START_BOTH_TERMINALS.bat`

**Need detailed instructions?**
→ Read `TWO_TERMINAL_SETUP.md`

**Need visual walkthrough?**
→ Read `TWO_TERMINAL_VISUAL_GUIDE.md`

**Need code examples?**
→ Read `QUICK_REFERENCE.md`

**Need feature details?**
→ Read `ENHANCED_AGENT_FEATURES.md`

**Need to verify setup?**
→ Run `python test_enhanced_integration.py`

---

**Status:** ✅ Ready for Production  
**Version:** System3-RAG v1.0 Enhanced  
**Last Updated:** February 5, 2026

**Let's build some enterprise POCs!** 🚀

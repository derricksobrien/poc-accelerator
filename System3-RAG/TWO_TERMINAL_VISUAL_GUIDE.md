# 📺 VISUAL: Running 2 Terminals Side-by-Side

## What Your Screen Will Look Like

```
┌───────────────────────────────────────────────┬───────────────────────────────────────────────┐
│ TERMINAL 1: Backend (PowerShell)              │ TERMINAL 2: Frontend (PowerShell)             │
├───────────────────────────────────────────────┼───────────────────────────────────────────────┤
│                                               │                                               │
│ PS C:\Users\derri\Code\...\System3-RAG>       │ PS C:\Users\derri\Code\...\System3-RAG>       │
│ .\.venv\Scripts\Activate.ps1                  │ .\.venv\Scripts\Activate.ps1                  │
│                                               │                                               │
│ (.venv) PS System3-RAG>                       │ (.venv) PS System3-RAG>                       │
│ python -m uvicorn app.main:app                │ streamlit run streamlit_app.py                │
│ --reload                                      │                                               │
│                                               │ Collecting usage statistics...                │
│ INFO:     Uvicorn running on                  │ You can now view your Streamlit app in        │
│           http://127.0.0.1:8000               │ your browser.                                 │
│ (Press CTRL+C to quit)                        │                                               │
│                                               │ Local URL: http://localhost:8501              │
│ INFO:     Started server process              │ Network URL:                                  │
│ [12345]                                       │ http://192.168.1.100:8501                     │
│                                               │                                               │
│ INFO:     Waiting for application             │ [Opens browser automatically]                 │
│ startup.                                      │                                               │
│                                               │                                               │
│ INFO:     Application startup                 │ For better performance, install the           │
│ complete.                                     │ Watchdog module:                              │
│                                               │ $ pip install watchdog                        │
│ [Ready for requests...]                       │                                               │
│                                               │ [Running] ⭐ at top right                     │
│                                               │                                               │
│ ← Now go to browser and type:                 │ ← Frontend is serving the UI                  │
│   http://localhost:8501                       │   http://localhost:8501                       │
│                                               │                                               │
│ Watch this terminal for API calls:            │ Watch this terminal for form                  │
│                                               │ submissions and page reloads:                 │
│ INFO: POST /api/rag/session/create            │                                               │
│ INFO: POST /api/rag/generate-poc              │ Script rerun triggered by file                │
│ INFO: Agent search_solutions activated        │ change in streamlit_app.py                    │
│ INFO: Agent generate_rbac activated           │                                               │
│ INFO: Agent generate_iac invoked               │ Rerunning script...                           │
│ INFO: Returning 200 OK                        │                                               │
│                                               │ [Ready] ✓                                     │
│                                               │                                               │
└───────────────────────────────────────────────┴───────────────────────────────────────────────┘
                                ↓
                    ┌───────────────────────────┐
                    │   BROWSER / USER          │
                    ├───────────────────────────┤
                    │                           │
                    │ Address: localhost:8501   │
                    │                           │
                    │  System3-RAG UI           │
                    │  ═══════════════════      │
                    │                           │
                    │  🚀 Generate POC          │
                    │  💬 Agent Chat            │
                    │  🔍 Search                │
                    │  📋 History               │
                    │  ⚙️ Status                │
                    │                           │
                    │ [Form inputs here..]      │
                    │                           │
                    └───────────────────────────┘
```

---

## 🎯 Step-by-Step Execution

### **STEP 1: Open Terminal 1 (Backend)**

**Action:**
```powershell
# Copy and paste this exactly:
cd C:\Users\derri\Code\techconnect_all\System3-RAG
```

**You'll see:**
```
PS C:\Users\derri\Code\techconnect_all\System3-RAG>
```

---

### **STEP 2: Activate Virtual Environment (Terminal 1)**

**Action:**
```powershell
# Copy and paste:
.\.venv\Scripts\Activate.ps1
```

**You'll see:**
```
(.venv) PS C:\Users\derri\Code\techconnect_all\System3-RAG>
```
← Note the `(.venv)` prefix = environment activated ✅

---

### **STEP 3: Start Backend Server (Terminal 1)**

**Action:**
```powershell
# Copy and paste:
python -m uvicorn app.main:app --reload
```

**You'll see:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

✅ **Terminal 1 is now running** - Keep it open!

---

### **STEP 4: Open Terminal 2 (Frontend)**

**Action:**
- Click `+` button in VS Code terminal panel, OR
- Open new PowerShell window
- Type:
```powershell
cd C:\Users\derri\Code\techconnect_all\System3-RAG
```

**You'll see:**
```
PS C:\Users\derri\Code\techconnect_all\System3-RAG>
```

---

### **STEP 5: Activate Virtual Environment (Terminal 2)**

**Action:**
```powershell
.\.venv\Scripts\Activate.ps1
```

**You'll see:**
```
(.venv) PS C:\Users\derri\Code\techconnect_all\System3-RAG>
```

---

### **STEP 6: Start Frontend Server (Terminal 2)**

**Action:**
```powershell
streamlit run streamlit_app.py
```

**You'll see:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.100:8501

  For better performance, install the Watchdog module:

  Is this for a commercial purpose? (y/n) [n]: 
```

✅ **Terminal 2 is now running** - Keep it open!

---

### **STEP 7: Open Browser**

**Action:**
Open your browser and go to: **http://localhost:8501**

**You'll see:**
```
System3-RAG

Azure AI Foundry Agent-Based POC Generator

🚀 Generate POC   💬 Agent Chat   🔍 Search   📋 History   ⚙️ Status
```

✅ **UI is now loaded!**

---

### **STEP 8: Test It Works**

**In Browser:**
1. Click **🚀 Generate POC** tab
2. Fill in:
   - Solution Area: `AI`
   - POC Title: `Test POC`
   - Requirements: `Quick test`
3. Click **Generate POC with Multi-Tool Agent**

**In Terminal 1 (Backend):**
```
INFO: POST /api/rag/session/create HTTP/1.1" 200
INFO: POST /api/rag/generate-poc HTTP/1.1" 200
INFO: Agent tool search_solutions invoked
INFO: Agent tool generate_rbac invoked
[... more info ...]
```

**In Terminal 2 (Frontend):**
```
Script rerun triggered by file change in streamlit_app.py
Rerunning script...
[Ready] ✓
```

**In Browser:**
- See results loading
- Results appear in tabs
- All features working ✅

---

## 🎮 Live Interaction Pattern

```
Browser                 Terminal 2              Terminal 1
(UI)                    (Streamlit)             (FastAPI)
  │                         │                       │
  ├─ Click "Generate"──────>│                       │
  │                         ├─ POST /api/...────────>│
  │                         │                       ├─ Run agent
  │                         │                       ├─ Call tools
  │                         │<─ 200 OK response──────┤
  │                         ├─ Format output        │
  │<─ Display results───────┤                       │
  │                         │                       │
  ├─ Scroll down            │                       │
  ├─ Download code          │                       │
  ├─ Edit template          │                       │
  └─ Ready for next action  │                       │
```

---

## 📊 Real Command Sequences to Copy-Paste

### For Terminal 1 (Backend) - Copy and paste line by line:

```powershell
cd C:\Users\derri\Code\techconnect_all\System3-RAG
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

### For Terminal 2 (Frontend) - Copy and paste line by line:

```powershell
cd C:\Users\derri\Code\techconnect_all\System3-RAG
.\.venv\Scripts\Activate.ps1
streamlit run streamlit_app.py
```

### Then in Browser:

```
http://localhost:8501
```

---

## 🚨 If Something Goes Wrong

### **Backend shows error:**
```
ModuleNotFoundError: No module named 'app'
```
✅ **Fix:** Make sure you're in `System3-RAG` folder (not parent)

### **Frontend won't start:**
```
ModuleNotFoundError: No module named 'streamlit'
```
✅ **Fix:** Run `pip install streamlit` in Terminal 2

### **Port already in use:**
```
Port 8501 is already in use
```
✅ **Fix:** 
```powershell
# Terminal 2: Use different port
streamlit run streamlit_app.py --server.port 8502
# Then visit http://localhost:8502
```

### **Backend and Frontend not communicating:**
1. ✅ Check Terminal 1 says "Application startup complete"
2. ✅ Check Terminal 2 says no red errors
3. ✅ Refresh browser (Ctrl+R or Cmd+R)
4. ✅ Check browser console (F12) for errors

---

## ⏹️ Shutting Down

### To stop everything:

**Terminal 1 (Backend):**
```
Press Ctrl+C
```
You'll see:
```
INFO:     Shutdown complete.
```

**Terminal 2 (Frontend):**
```
Press Ctrl+C
```
The terminal closes.

---

## ✨ What's Happening Behind the Scenes

### **Terminal 1 (Backend at :8000)**
- Running FastAPI web server
- Hosting the REST API endpoints
- Managing agent orchestration
- Coordinating tool calls
- Storing sessions
- Handling authentication
- **Status page:** http://localhost:8000/docs (interactive API explorer)

### **Terminal 2 (Frontend at :8501)**
- Running Streamlit UI framework
- Rendering interactive components
- Managing form submissions
- Sending requests to Backend API
- Displaying results beautifully
- Hot-reloading on code changes

### **Communication Flow**
```
User Action (Fill form) 
    ↓
Streamlit (catch event)
    ↓
POST request to FastAPI (:8000)
    ↓
FastAPI (process request)
    ↓
Agent Orchestrator (run workflow)
    ↓
Return JSON response
    ↓
Streamlit (format & display)
    ↓
Browser (show to user)
```

---

## 🎓 Monitor Each Terminal

### Terminal 1 - Watch for:
- ✅ `INFO: Application startup complete` = Backend ready
- ✅ `INFO: POST /api/...` = API calls happening
- ⚠️ `WARNING: ...` = Something unexpected (usually OK)
- ❌ `ERROR: ...` = Something failed (needs fixing)

### Terminal 2 - Watch for:
- ✅ `Local URL: http://localhost:8501` = Frontend ready
- ✅ `Script rerun triggered` = Code changed, updating
- ✅ `[Ready]` with ✓ = Everything loaded
- ⚠️ Red text = Frontend error (check code)

---

## 🎯 Quick Checklist

- [ ] Terminal 1: `(.venv)` prefix visible?
- [ ] Terminal 1: `Application startup complete` showing?
- [ ] Terminal 2: `(.venv)` prefix visible?
- [ ] Terminal 2: `Local URL: http://localhost:8501` showing?
- [ ] Browser tab opened to http://localhost:8501?
- [ ] Can see System3-RAG interface with 5 tabs?
- [ ] No red error messages in any terminal?

**If all checked:** You're good to go! 🚀

---

## 🚀 First POC Generation

Once everything is running:

1. **Browser** → Go to **🚀 Generate POC** tab
2. **Fill form:**
   - Solution Area: Select any option
   - POC Title: Type something like "Test Platform"
   - Requirements: Type "Test the full workflow"
3. **Click:** **"🚀 Generate POC with Multi-Tool Agent"**
4. **Watch:**
   - Terminal 1 shows agent tools running
   - Terminal 2 shows data flowing
   - Browser shows results populating
5. **Explore:**
   - Click tabs to see different outputs
   - Download code sections
   - Edit templates
   - Calculate costs

---

## 💡 Pro Terminal Tips

### Make Terminals Side-by-Side
1. In VS Code: Click "Split Terminal" button (right side of tab)
2. Or arrange windows: Terminal 1 on left, Terminal 2 on right
3. Or use Windows multimonitor setup

### Resize Terminals
- Drag divider between panes to adjust sizes
- Make Backend terminal smaller (it's read-only mostly)
- Make Frontend terminal larger (don't need to look at it much)

### Watch Terminal Output
- Backend shows what's happening behind scenes
- Frontend shows when UI renders
- Together they tell the story of the request
- Reference them when debugging

---

## 🎉 You're All Set!

You now understand:
- ✅ How to run both terminal sessions
- ✅ What output to expect in each
- ✅ How to know when they're ready
- ✅ How to open the UI
- ✅ How to generate your first POC
- ✅ What to do if something goes wrong

**Next:** Just follow the commands above and start generating POCs! 🚀

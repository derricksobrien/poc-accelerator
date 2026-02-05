# 🚀 Running System3-RAG in 2 Terminal Sessions

## Quick Overview

```
Terminal 1 (Backend)  → FastAPI Server on http://localhost:8000
                        ↓
Terminal 2 (Frontend) → Streamlit UI on http://localhost:8501
                        ↓
                      Browser → http://localhost:8501
```

---

## 📋 Setup Instructions

### Step 1: Open Two Terminal Windows

**Option A: PowerShell (Windows)**
1. Press `Win + X` → Select "Windows PowerShell" twice
2. Or open VS Code terminal, then click `+` to open second terminal

**Option B: Command Prompt**
1. Press `Win + R` → Type `cmd` → Press Enter
2. Then `Win + R` → Type `cmd` → Press Enter again

**Option C: Git Bash**
1. Right-click folder → "Git Bash Here" (twice)

---

## 🔧 Terminal 1: FastAPI Backend

### Commands to Run

```powershell
# Navigate to project
cd C:\Users\derri\Code\techconnect_all\System3-RAG

# Activate virtual environment (if not already active)
.\.venv\Scripts\Activate.ps1

# Start FastAPI backend
python -m uvicorn app.main:app --reload
```

### Expected Output

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### What You'll See

- ✅ Server starts on port **8000**
- 📝 Shows loaded modules (session manager, etc.)
- 🔄 Auto-reloads when you change code
- ⚠️ Shows warnings/errors from API calls

### Keep This Running

**Don't close this terminal!** Leave it running while you use the UI.

---

## 💻 Terminal 2: Streamlit Frontend

### Commands to Run

```powershell
# Navigate to same project
cd C:\Users\derri\Code\techconnect_all\System3-RAG

# Activate virtual environment (if not already active)
.\.venv\Scripts\Activate.ps1

# Start Streamlit frontend
streamlit run streamlit_app.py
```

### Expected Output

```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501

  For better performance, install the Watchdog module:
  $ pip install watchdog
```

### What You'll See

- ✅ Streamlit server starts on port **8501**
- 🌐 Browser tab opens automatically
- 📊 "Running" indicator at top right
- 🔄 Auto-reloads when code changes

### Keep This Running

**Don't close this terminal!** The UI runs here.

---

## 🎯 Visual Terminal Setup

```
┌─────────────────────────────────┬─────────────────────────────────┐
│ Terminal 1: Backend             │ Terminal 2: Frontend            │
├─────────────────────────────────┼─────────────────────────────────┤
│                                 │                                 │
│ $ cd ../System3-RAG             │ $ cd ../System3-RAG             │
│ $ .\.venv\Scripts\Activate.ps1  │ $ .\.venv\Scripts\Activate.ps1  │
│ $ python -m uvicorn ...         │ $ streamlit run streamlit_app.py│
│                                 │                                 │
│ INFO: Uvicorn running on        │ Local URL: http://localhost...  │
│ http://127.0.0.1:8000           │                                 │
│ INFO: Application startup       │ You can now view your Streamlit │
│ complete.                       │ app in your browser.            │
│                                 │                                 │
│ [Waiting for requests...]       │ [Browser opens]                 │
│                                 │                                 │
└─────────────────────────────────┴─────────────────────────────────┘
                                ↓
                        http://localhost:8501
                        (Streamlit App)
```

---

## ✅ Step-by-Step Checklist

- [ ] **Terminal 1 Open** - Backend running on :8000
  - [ ] See "Application startup complete"
  - [ ] No red error messages
  - [ ] Line says "Press CTRL+C to quit"

- [ ] **Terminal 2 Open** - Frontend running on :8501
  - [ ] See "Local URL: http://localhost:8501"
  - [ ] Browser tab opened automatically
  - [ ] "Running" indicator at top right

- [ ] **Browser Open** - http://localhost:8501
  - [ ] See System3-RAG interface load
  - [ ] Tabs visible: Generate POC, Chat, Search, History, Status
  - [ ] No red error messages

---

## 🎮 Now Try It

### In the Browser (http://localhost:8501):

1. Go to **🚀 Generate POC** tab
2. Fill in:
   - Solution Area: "AI"
   - POC Title: "Quick Test"
   - Requirements: "Test the system"
3. Click **"🚀 Generate POC with Multi-Tool Agent"**
4. Watch it work!

### Watch Terminal 1 (Backend):

```
INFO:     POST /api/rag/generate-poc - "HTTP/1.1 200 OK"
INFO:     Started processing...
INFO:     Agent tool: search_solutions invoked
INFO:     Agent tool: generate_rbac invoked
...
```

### Watch Terminal 2 (Frontend):

```
> Running on local URL: http://localhost:8501
> User is running on: Chrome/Safari/etc
> Streamlit version X.XX.X
```

---

## ⏹️ Stopping the Servers

### To Stop Backend (Terminal 1):
```
Press CTRL+C
```

Output:
```
INFO:     Shutdown complete.
```

### To Stop Frontend (Terminal 2):
```
Press CTRL+C
```

Then close the terminal.

---

## 🔄 Restarting

### If Backend Crashes:
1. Fix the code causing error (if any)
2. In Terminal 1: Press `CTRL+C`
3. Run again: `python -m uvicorn app.main:app --reload`

### If Frontend Crashes:
1. Fix the code causing error (if any)
2. In Terminal 2: Press `CTRL+C`
3. Run again: `streamlit run streamlit_app.py`

### If Browser Port is Busy:
```powershell
# Terminal 2: Use different port
streamlit run streamlit_app.py --server.port 8502
```
Then visit: http://localhost:8502

---

## 🐛 Troubleshooting

### Backend Errors

| Error | Solution |
|-------|----------|
| `Address already in use` | Port 8000 taken. `netstat -ano \| findstr 8000` to find process |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| `No route found` | Make sure `app/main.py` exists and has routes |

### Frontend Errors

| Error | Solution |
|-------|----------|
| `Connection refused` | Make sure backend (Terminal 1) is running |
| `Streamlit not found` | Run `pip install streamlit` |
| `Port 8501 in use` | Use `--server.port 8502` or kill process on 8501 |

### Both Not Communicating

1. Check Terminal 1 shows "Application startup complete"
2. Check Terminal 2 shows no red errors
3. In browser, check browser console (F12) for errors
4. Reload browser page (CTRL+R)

---

## 💡 Pro Tips

### Tip 1: Watch Both Terminals
Keep both visible to see what's happening. Side-by-side is best.

### Tip 2: Read Terminal Output
- Red text = Error (check it)
- Yellow text = Warning (usually OK but note it)
- Blue/Green text = Info (normal operation)

### Tip 3: Hot Reload Works
- Change Python code → Auto-reloads
- Change Streamlit code → Auto-reloads
- **No need to restart!** Just refresh browser.

### Tip 4: Monitor Terminal 1
Backend terminal shows:
- ✅ What endpoints are being called
- ✅ If agents are running tools
- ✅ Any errors or warnings
- ✅ Performance/timing info

### Tip 5: Check Logs
For more details, add to Terminal 1:
```powershell
python -m uvicorn app.main:app --reload --log-level debug
```

---

## 🎯 Full Command Sequence (Copy-Paste Ready)

### Terminal 1:
```powershell
cd C:\Users\derri\Code\techconnect_all\System3-RAG
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

### Terminal 2:
```powershell
cd C:\Users\derri\Code\techconnect_all\System3-RAG
.\.venv\Scripts\Activate.ps1
streamlit run streamlit_app.py
```

Then open: **http://localhost:8501**

---

## ✨ What's Running

| Component | Terminal | Port | What It Does |
|-----------|----------|------|------------|
| **FastAPI Backend** | Terminal 1 | 8000 | Handles agent logic, sessions, RAG |
| **Streamlit Frontend** | Terminal 2 | 8501 | User interface, forms, visualization |
| **Agent SDK** | Terminal 1 | (internal) | Coordinates multi-tool workflows |
| **Browser** | Your PC | (local) | Displays UI, runs JavaScript |

---

## 🚀 You're Ready!

Everything is set up. Just:

1. Open **Terminal 1** → Start backend
2. Open **Terminal 2** → Start frontend
3. Open **Browser** → Visit http://localhost:8501
4. **Start generating POCs!**

The agent orchestrator handles all the complexity automatically. ✨

---

**Questions?** Check the terminals for output/errors, or refer to the documentation in the System3-RAG folder.

Happy POC generation! 🎉

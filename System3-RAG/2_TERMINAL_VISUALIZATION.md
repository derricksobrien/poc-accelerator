# 📺 2-TERMINAL EXECUTION: VISUAL GUIDE

## 🎬 Watch This Animation

```
TIME: 0:00 - START
═════════════════════════════════════════════════════════════════════════
Your Desktop
├── File Explorer
│   └── System3-RAG folder
│       ├── START_BOTH_TERMINALS.bat ← DOUBLE-CLICK THIS
│       ├── streamlit_app.py
│       ├── app/
│       └── ...


TIME: 0:05 - FIRST TERMINAL OPENS
═════════════════════════════════════════════════════════════════════════
┌──────────────────────────────────────────┐
│ TERMINAL 1: System3-RAG Backend          │
├──────────────────────────────────────────┤
│                                          │
│ Windows PowerShell                       │
│ Copyright (c) Microsoft...               │
│                                          │
│ (.venv) PS System3-RAG>                  │
│ python -m uvicorn app.main:app --reload  │
│                                          │
│ INFO: Uvicorn running on                 │
│       http://127.0.0.1:8000              │
│ INFO: Application startup complete.      │
│                                          │
│ [Server listening...]                    │
│                                          │
└──────────────────────────────────────────┘


TIME: 0:08 - SECOND TERMINAL OPENS
═════════════════════════════════════════════════════════════════════════
┌──────────────────────────────────────────────────────────────────┐
│ TERMINAL 1: Backend                      TERMINAL 2: Frontend    │
├──────────────────────┬─────────────────────────────────────────┤
│                      │                                          │
│ [Backend running]    │ Windows PowerShell                       │
│ Port: 8000           │ Copyright (c) Microsoft...               │
│ Status: ✓ Ready      │                                          │
│                      │ (.venv) PS System3-RAG>                  │
│                      │ streamlit run streamlit_app.py           │
│                      │                                          │
│ [Waiting...]         │ You can now view your Streamlit app      │
│                      │ Local URL: http://localhost:8501         │
│                      │                                          │
│                      │ [Server listening...]                    │
│                      │                                          │
└──────────────────────┴─────────────────────────────────────────┘


TIME: 0:10 - BROWSER OPENS AUTOMATICALLY
═════════════════════════════════════════════════════════════════════════
Your Browser (Chrome/Edge/Firefox)
┌────────────────────────────────────────────────────────────────┐
│ http://localhost:8501                                   ✓ ✓ ✗ │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│                   System3-RAG                                 │
│            Azure AI Foundry Agent-Based                       │
│               POC Generator                                   │
│                                                                │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  🚀 Generate POC  │  💬 Agent Chat  │  🔍 Search              │
│  📋 History       │  ⚙️ Status                                 │
│                                                                │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Ready to use! ✅                                              │
│                                                                │
└────────────────────────────────────────────────────────────────┘


TIME: 0:15 - USER FILLS FORM
═════════════════════════════════════════════════════════════════════════
Form Input:
├── Solution Area: [AI ▼]
├── POC Title: [Enterprise AI Platform]
├── Requirements: [Multi-tenant, real-time, scalable...]
└── [🚀 Generate POC with Multi-Tool Agent Button]
    ↓ CLICK


TIME: 0:20 - AGENT ORCHESTRATOR RUNS (Watch Terminal 1)
═════════════════════════════════════════════════════════════════════════
Terminal 1 Output:
└── INFO: POST /api/rag/generate-poc HTTP/1.1" 200
    INFO: Agent workflow starting...
    INFO: Step 1/6: search_solutions activated
    ├── Found 3 matching solutions
    INFO: Step 2/6: generate_rbac activated
    ├── Generated 2 RBAC configurations
    INFO: Step 3/6: generate_deployment_script activated
    ├── Created 3 deployment scripts
    INFO: Step 4/6: generate_iac_template activated
    ├── Generated Bicep, Terraform, ARM templates
    INFO: Step 5/6: validate_architecture activated
    ├── Validation passed
    INFO: Step 6/6: Cost estimation complete
    └── Returning results to frontend


TIME: 0:25 - RESULTS DISPLAY (Watch Browser)
═════════════════════════════════════════════════════════════════════════
Browser Update:
├── 📚 Recommendations Tab
│   ├── Solution 1 (85% match)
│   ├── Solution 2 (78% match)
│   └── Solution 3 (72% match)
│
├── 🔐 RBAC Configuration Tab
│   ├── Contributor role
│   ├── Scope: /subscriptions/{...}
│   └── [Copy] [Download]
│
├── 🚀 Deployment Scripts Tab
│   ├── azure-cli-deploy.sh [Download]
│   ├── powershell-setup.ps1 [Download]
│   └── validate.sh [Download]
│
├── 🏗️ IaC Templates Tab
│   ├── main.bicep [View] [Edit] [Download]
│   ├── deployment.tf [View] [Edit] [Download]
│   └── template.json [View] [Edit] [Download]
│
├── ✅ Validation Results Tab
│   ├── ✓ Well-Architected Framework: Pass
│   ├── ✓ Security Best Practices: Pass
│   └── ✓ Performance Requirements: Pass
│
├── 💰 Cost Estimate Tab
│   ├── Compute: $1,500/month
│   ├── Storage: $500/month
│   ├── Networking: $300/month
│   └── Total: $2,300/month ($27,600/year)
│
├── 📋 Workflow Log Tab
│   ├── Step 1: Search Solutions ✓
│   ├── Step 2: Generate RBAC ✓
│   ├── Step 3: Generate Scripts ✓
│   ├── Step 4: Generate Templates ✓
│   ├── Step 5: Validate Architecture ✓
│   └── Step 6: Estimate Costs ✓
│
└── [📥 Download Complete POC as JSON]


TIME: 0:30+ - READY FOR NEXT ACTION
═════════════════════════════════════════════════════════════════════════
You can now:
├── Click different tabs to view different outputs
├── Edit templates using the inline editors
├── Download any generated code
├── Estimate costs with the calculator
├── Generate another POC
├── Chat with the agent
├── Search for more solutions
├── Check system status
└── Continue until satisfied


TERMINALS ARE ALWAYS RUNNING:
═════════════════════════════════════════════════════════════════════════
Terminal 1 (Backend)          Terminal 2 (Frontend)
├── Stays open                ├── Stays open
├── Watching for requests     ├── Watching for new POC requests
├── Running agent tools       ├── Rendering results
├── Managing sessions         ├── Hot-reloading on code changes
└── Logging everything        └── Sending data to backend


TO STOP EVERYTHING:
═════════════════════════════════════════════════════════════════════════
Option 1: Close the terminal windows
Option 2: Press Ctrl+C in each terminal
Result: Services stop, backend and frontend shut down
```

---

## 📊 2-Terminal Communication Flow

```
USER CLICKS BUTTON (Browser)
           ↓
Browser Submits Form
           ↓
JavaScript sends POST to http://localhost:8000/api/...
           ↓
Terminal 2 (Streamlit) receives data
           ↓
Terminal 2 forwards to Terminal 1 (FastAPI)
           ↓
Terminal 1 (FastAPI) processes request
├─ Creates agent session
├─ Runs 6-step workflow
├─ Calls agent tools
│  ├─ search_solutions
│  ├─ generate_rbac
│  ├─ generate_deployment_script
│  ├─ generate_iac_template
│  ├─ validate_architecture
│  └─ estimate_costs
├─ Formats results as JSON
└─ Returns 200 OK response
           ↓
Terminal 2 (Streamlit) receives response
           ↓
Terminal 2 formats for display
           ↓
Terminal 2 updates browser with results
           ↓
Browser displays rich results in tabs
           ↓
USER SEES RESULTS ✅
           ↓
USER CAN DOWNLOAD CODE
```

---

## 🎮 Real Screenshot Simulation

### **What Your Screen Looks Like**

```
┌─────────────────────────────┬─────────────────────────────┐
│                             │                             │
│  Terminal 1 (8000)          │  Terminal 2 (8501)          │
│                             │                             │
│  INFO: Uvicorn running on   │  Local URL: localhost:8501  │
│  http://127.0.0.1:8000      │  NetworkURL: 192.168.x.x    │
│                             │                             │
│  INFO: Application startup  │  Watching for requests...   │
│  complete.                  │                             │
│                             │  Script rerun triggered...  │
│  [Server waiting...]        │  Rerunning script...        │
│                             │  Ready! ✓                   │
└─────────────────────────────┴─────────────────────────────┘
            ↓ Below your terminals ↓
┌───────────────────────────────────────────────────────────┐
│                                                             │
│  Your Browser (http://localhost:8501)                      │
│                                                             │
│  ╔═══════════════════════════════════════════════════════╗ │
│  ║  System3-RAG                                          ║ │
│  ║  🚀 Gen POC │ 💬 Chat │ 🔍 Search │ 📋 His │ ⚙️ Stat ║ │
│  ╠═══════════════════════════════════════════════════════╣ │
│  ║ POC Title: Enterprise AI Platform                     ║ │
│  ║ Solution Area: [AI ▼]                                 ║ │
│  ║ Requirements: ┌─────────────────────────────────────┐ ║ │
│  ║               │ Multi-tenant, real-time, scalable.. │ ║ │
│  ║               │                                     │ ║ │
│  ║               │                                     │ ║ │
│  ║               └─────────────────────────────────────┘ ║ │
│  ║ [🚀 Generate POC with Multi-Tool Agent]              ║ │
│  ╠═══════════════════════════════════════════════════════╣ │
│  ║ Results:                                              ║ │
│  ║ 📚 Recommendations │ 🔐 RBAC │ 🚀 Scripts │...       ║ │
│  ║                                                       ║ │
│  ║ Solution 1 (85% match)                                ║ │
│  ║  ├─ Description...                                    ║ │
│  ║  └─ [View Details] [Copy] [Download]                 ║ │
│  ║                                                       ║ │
│  ║ [📥 Download Complete POC as JSON]                   ║ │
│  ╚═══════════════════════════════════════════════════════╝ │
│                                                             │
└───────────────────────────────────────────────────────────┘
```

---

## ⏱️ Timeline

```
00s:00 - Double-click START_BOTH_TERMINALS.bat
    ↓
00s:03 - Terminal 1 window opens
    ↓
00s:05 - Terminal 1 shows "Application startup complete"
    ↓
00s:08 - Terminal 2 window opens  
    ↓
00s:10 - Terminal 2 shows "Local URL: http://localhost:8501"
    ↓
00s:12 - Browser window opens automatically
    ↓
00s:15 - System3-RAG UI is fully loaded ✅
    ↓
00s:20 - User fills form and clicks "Generate"
    ↓
00s:22 - Terminal 1 starts agent workflow (watch the logs!)
    ↓
00s:25 - Agent completes 6-step workflow
    ↓
00s:27 - Terminal 2 formats results
    ↓
00s:28 - Browser shows results in tabs ✅
    ↓
00s:30+ - User can explore, download, or generate another
```

---

## 🎯 What Happens in Each Terminal

### Terminal 1 (Backend / port 8000)

**Startup:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**While using:**
```
INFO:     POST /api/rag/session/create HTTP/1.1" 200
INFO:     POST /api/rag/generate-poc HTTP/1.1" 200
[Agent processes requests...]
```

**What to look for:**
- ✅ "Application startup complete"
- ✅ "HTTP/1.1 200" (successful)
- ⚠️ "HTTP/1.1 500" (error - check message)
- ❌ Red text = something broke

### Terminal 2 (Frontend / port 8501)

**Startup:**
```
Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
[Ready in X.XX sec]
```

**While using:**
```
Script rerun triggered by file change
Rerunning script...
[Running]
[Ready] ✓
```

**What to look for:**
- ✅ "Local URL: http://localhost:8501"
- ✅ "Ready" or "Running"
- ⚠️ Yellow text = warning
- ❌ Red text = error (check message)

---

## 🔄 Typical Usage Session

```
0. Both terminals already running (from START script)
   ├─ Terminal 1: Shows "Application startup complete"
   └─ Terminal 2: Shows "Ready ✓"

1. Open browser: http://localhost:8501
   └─ System3-RAG UI loads

2. Go to: "🚀 Generate POC" tab
   └─ Form appears

3. Fill form:
   ├─ Solution Area: (select)
   ├─ POC Title: (type)
   ├─ Requirements: (type)
   └─ Complexity: (select)

4. Click: "🚀 Generate POC with Multi-Tool Agent"
   └─ Form submits

5. Watch Terminal 1:
   ├─ INFO: POST /api/rag/generate-poc
   ├─ INFO: Agent workflow starting...
   ├─ INFO: Step 1/6: search_solutions
   ├─ INFO: Step 2/6: generate_rbac
   ├─ [more steps...]
   └─ INFO: Returning 200 OK

6. Watch Terminal 2:
   ├─ Script rerun triggered...
   ├─ Rerunning script...
   └─ Ready ✓

7. Watch Browser:
   ├─ Results loading...
   ├─ Tabs populate with content
   ├─ Code appears in code blocks
   ├─ Buttons become clickable
   └─ Download buttons appear

8. Explore Results:
   ├─ Click tabs to see different outputs
   ├─ Click copy buttons to copy code
   ├─ Click download to save files
   ├─ Edit templates if needed
   └─ Use the generated code in your projects

9. Ready for next POC:
   ├─ Scroll up
   ├─ Change form inputs
   ├─ Click "Generate" again
   └─ Go back to step 5

10. Done!:
    ├─ Close browser tab (UI still runs)
    ├─ Leave terminals open
    └─ or Close terminals to stop everything
```

---

## ✨ The Expected Workflow

```
┌─────────────────────────────────────────────────────────┐
│                   Your Computer                          │
├──────────────────────┬──────────────────────────────────┤
│                      │                                  │
│  Terminal 1          │  Terminal 2                      │
│  ─────────────       │  ──────────────                  │
│                      │                                  │
│  port 8000           │  port 8501                       │
│  FastAPI Backend     │  Streamlit Frontend              │
│                      │                                  │
│  Running now ✓       │  Running now ✓                   │
│                      │                                  │
└──────────────────────┴──────────────────────────────────┘
                │                    │
                └────────┬───────────┘
                         │
                    ┌────▼────┐
                    │ Browser  │
                    │ :8501    │
                    │ Running  │
                    └────┬────┘
                         │
                  ┌──────▼───────┐
                  │  YOU USE IT!  │
                  │  Generate    │
                  │  POCs        │
                  │  Download    │
                  │  Code        │
                  └──────────────┘
```

---

## 📝 Copy-Paste: The Absolute Shortest Version

**Do this:**

1. Open File Explorer
2. Go to: `C:\Users\derri\Code\techconnect_all\System3-RAG`
3. Double-click: `START_BOTH_TERMINALS.bat`
4. Wait ~10 seconds
5. Browser opens to http://localhost:8501
6. You're done! Start generating POCs.

**That's literally it.** Everything else is just detail.

---

**Status: Ready to Use ✅**

You have two terminals running different services that communicate to give you a beautiful AI-powered POC generator interface. It's a complete system working together as one.

🚀 Let's go!

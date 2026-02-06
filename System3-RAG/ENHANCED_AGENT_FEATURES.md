# System3-RAG: Advanced Agent-Driven Frontend

## 🎯 What's New: Enhanced Agent SDK Integration

You now have a production-ready frontend that leverages the Azure AI Foundry Agent SDK with **productivity-focused features beyond simple chat**. Here's what we've built:

---

## 🚀 Core Features

### 1. **Multi-Tool Agent Orchestration**
The frontend now intelligently coordinates multiple agent tools in sequence:

```
User Input → Agent Orchestrator → Multi-Step Workflow:
  ├── 🔍 Search Solutions (search_solutions tool)
  ├── 🔐 Generate RBAC (generate_rbac tool)
  ├── 🚀 Generate Deployment Scripts (generate_deployment_script tool)
  ├── 🏗️ Generate IaC Templates (generate_iac_template tool)
  ├── ✅ Validate Architecture (validate_architecture tool)
  └── 💰 Estimate Costs
```

**Location:** [`agent_orchestrator.py`](agent_orchestrator.py)

### 2. **Rich Code Display with Copy Buttons**
All generated code (Bash, PowerShell, Bicep, Terraform) displays with:
- ✅ Syntax highlighting
- 📋 One-click copy to clipboard
- ⬇️ Download buttons
- 🔢 Line numbers

**Location:** [`utils_enhanced.py`](utils_enhanced.py) → `display_code_with_copy()`

### 3. **RBAC Configuration Builder**
Interactive UI for building Azure RBAC configurations:
- Select roles from comprehensive Azure role list
- Define scopes (Subscription, Resource Group, Resource)
- Configure service principals
- Generate Bicep installation code

**Usage:**
```python
from utils_enhanced import build_rbac_configuration, generate_rbac_script

rbac_config = build_rbac_configuration()
bicep_code = generate_rbac_script(rbac_config)
```

### 4. **IaC Template Editor & Validator**
Edit and validate Infrastructure-as-Code templates:
- **Bicep** templates for Azure
- **Terraform** for multi-cloud
- **ARM templates** for low-level control
- Built-in JSON validation
- Auto-format capability
- Download with one click

**Usage:**
```python
from utils_enhanced import display_iac_template_editor

template_content, is_valid = display_iac_template_editor(template_type="bicep")
```

### 5. **Deployment Orchestrator**
Step-by-step guided deployment UI:
- Visual progress tracking
- Execute deployment steps one-by-one
- View output from each step
- Reset steps if needed
- Copy commands individually

**Usage:**
```python
from utils_enhanced import DeploymentOrchestrator

orchestrator = DeploymentOrchestrator()
orchestrator.add_step(
    name="Create Resource Group",
    description="Create the main Azure resource group",
    command="az group create --name myRG --location eastus"
)
orchestrator.display_orchestrator()
```

### 6. **Interactive Cost Calculator**
Break down infrastructure costs by component:
- **Compute:** VM type and count selection
- **Storage:** GB selection with per-GB pricing
- **Networking:** Monthly data transfer in GB
- **Licenses:** SQL databases and other services
- **Support:** Basic/Standard/Professional tier selection

Displays:
- Per-component costs
- Monthly total
- Yearly projection
- Visual breakdown chart

**Usage:**
```python
from utils_enhanced import display_cost_calculator

costs = display_cost_calculator()
# Returns: {compute, storage, networking, licenses, support, monthly_total}
```

### 7. **Architecture Visualization & Validation**
Display and validate proposed architectures:
- Component visualizer (shows all solution pieces)
- Data flow diagrams (Mermaid support)
- Deployment model summary
- Validation against Azure Well-Architected Framework
- Security best practices check
- Performance recommendations
- Cost optimization suggestions

**Usage:**
```python
from utils_enhanced import display_architecture_summary, display_validation_results

display_architecture_summary(architecture_dict)
display_validation_results(validation_dict)
```

---

## 📊 Frontend Tabs

### Tab 1: 🚀 **Generate POC (Enhanced)**
**Multi-tool workflow with rich output:**
1. **Input:** Solution area, title, requirements, complexity level
2. **Processing:** Agent orchestrator executes 6-step workflow
3. **Output Tabs:**
   - 📚 **Recommendations** - Matched solutions with relevance scores
   - 🔐 **RBAC Configuration** - Roles, scopes, service principals + Bicep code generator
   - 🚀 **Deployment Scripts** - Bash, PowerShell, validation scripts with copy buttons
   - 🏗️ **IaC Templates** - Bicep, Terraform, ARM with editor & validator
   - ✅ **Validation** - Architecture validation against best practices
   - 💰 **Cost Estimate** - Detailed cost breakdown and yearly projection
   - 📋 **Workflow Log** - See what each agent tool did

### Tab 2: 💬 **Agent Chat (Existing)**
Direct conversation with agent for architectural questions.

### Tab 3: 🔍 **Search Solutions (Existing)**
Semantic search across solution catalog with synthesis.

### Tab 4: 📋 **History (Existing)**
View all POCs generated in current session.

### Tab 5: ⚙️ **Status (Existing)**
System health and configuration checks.

---

## 🔧 Architecture

### Agent Orchestrator Pipeline
```
┌─────────────────────────────────────────┐
│   User POC Request (Title + Reqs)      │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  Agent Orchestrator                     │
│  (agent_orchestrator.py)               │
└────────────┬────────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
Step 1-6 Workflow   Result Aggregation
(Tool Calls)        & Parsing
    │                 │
    ├─ Search         │
    ├─ RBAC Gen       │
    ├─ Script Gen     │  → Structured Output
    ├─ IaC Gen        │     with Code Blocks
    ├─ Validate       │
    └─ Cost Est       │
                      │
                      ▼
         ┌────────────────────────────┐
         │  Enhanced UI Components    │
         │  (utils_enhanced.py)       │
         │                            │
         │  ├─ Code Display           │
         │  ├─ RBAC Builder           │
         │  ├─ IaC Editor             │
         │  ├─ Deployment Orch.       │
         │  ├─ Cost Calculator        │
         │  └─ Architecture Viewer    │
         └────────────────────────────┘
```

---

## 🎓 Usage Examples

### Example 1: Generate Complete POC
```python
from agent_orchestrator import AgentOrchestrator
from app.agent_enhanced import AzureAIFoundryAgent

# Initialize
agent = AzureAIFoundryAgent()
batch = AgentOrchestrator(agent)

# Run workflow
result = batch.orchestrate_poc_generation(
    session_id="user-session-123",
    poc_title="Enterprise AI Platform",
    solution_area="AI",
    requirements="Multi-tenant AI service with real-time inference...",
    top_results=5
)

# Access structured outputs
recommendations = result["details"]["recommendations"]
rbac_configs = result["details"]["rbac_requirements"]
scripts = result["details"]["deployment_scripts"]
templates = result["details"]["iac_templates"]
costs = result["details"]["cost_estimate"]
validation = result["details"]["validation_results"]
```

### Example 2: Build and Display RBAC UI
```python
from utils_enhanced import build_rbac_configuration, generate_rbac_script

# User builds RBAC through interactive form
rbac_config = build_rbac_configuration()  # Streamlit widgets

# Generate Bicep code
bicep_template = generate_rbac_script(rbac_config)

# Display with copy button
display_code_with_copy(bicep_template, language="bicep", label="RBAC Bicep")
```

### Example 3: Guided Multi-Step Deployment
```python
from utils_enhanced import DeploymentOrchestrator

# Create orchestrator
orchestrator = DeploymentOrchestrator()

# Add steps
orchestrator.add_step(
    name="Create Resource Group",
    command="az group create --name myRG --location eastus"
)

orchestrator.add_step(
    name="Deploy IaC",
    script=bicep_template_content
)

orchestrator.add_step(
    name="Configure RBAC",
    command="az role assignment create --assignee <id> --role Contributor"
)

# User sees progress UI with ability to execute one-by-one
status = orchestrator.display_orchestrator()
```

### Example 4: Cost Estimation
```python
from utils_enhanced import display_cost_calculator

# Interactive calculator
costs = display_cost_calculator()

print(f"Monthly: ${costs['monthly_total']}")
print(f"Yearly: ${costs['monthly_total']*12}")

# Breakdown
print(f"Compute: ${costs['compute']}")
print(f"Storage: ${costs['storage']}")
```

---

## 📁 File Structure

```
System3-RAG/
├── streamlit_app.py           # Main UI (enhanced with new tabs)
├── agent_orchestrator.py      # NEW: Multi-tool workflow orchestration
├── utils_enhanced.py          # NEW: Rich UI components
├── app/
│   ├── main.py               # FastAPI backend
│   ├── agent_enhanced.py      # Azure AI Foundry agent client
│   └── session.py            # Session management
├── requirements.txt           # Dependencies (no new ones needed)
└── tests/
    └── test_agent_and_frontend.py
```

---

## 🚀 Getting Started

### 1. No New Dependencies Needed
All required packages are already in `requirements.txt`:
- ✅ Streamlit (UI)
- ✅ FastAPI (Backend)
- ✅ Azure AI SDK (Agent)
- ✅ Everything else you need

### 2. Update Streamlit App
The enhanced `streamlit_app.py` is already updated with all new features.

### 3. Run It
```bash
# Terminal 1: Backend
python -m uvicorn app.main:app --reload

# Terminal 2: Frontend
streamlit run streamlit_app.py
```

Visit: `http://localhost:8501`

### 4. Start Generating POCs
Go to **🚀 Generate POC** tab and:
1. Enter solution area, title, requirements
2. Click **Generate POC with Multi-Tool Agent**
3. Watch the agent orchestrator run 6-step workflow
4. Explore all output tabs (Recommendations, RBAC, Scripts, IaC, etc.)
5. Download generated code and templates

---

## 🔌 Integration Points

### Agent Tool Hooks
The orchestrator is wired to call these agent tools:
- **`search_solutions`** - Find matching solutions (step 1)
- **`generate_rbac`** - Create RBAC configs (step 2)
- **`generate_deployment_script`** - Scripts for deployment (step 3)
- **`generate_iac_template`** - Bicep/Terraform/ARM (step 4)
- **`validate_architecture`** - Check against best practices (step 5)
- (Cost estimation uses standard agent message, no tool needed)

Each tool is properly defined in `app/agent_enhanced.py` with parameter schemas.

### Mock vs Real Mode
The agent client automatically operates in:
- **Real Mode:** When Azure endpoints configured (calls actual API)
- **Mock Mode:** When running locally without Azure (safe for testing)

---

## 💡 Future Enhancements

The framework is extensible:

1. **Add more agent tools:**
   ```python
   # In orchestrator, add new step
   def _execute_my_custom_step(self, session_id, context):
       response = self.agent.send_message(
           session_id=session_id,
           message="...",
           tools_to_use=["my_new_tool"]
       )
   ```

2. **Add more UI components:**
   ```python
   # In utils_enhanced.py, add new component
   def my_new_component():
       # Rich UI here
   ```

3. **Store POCs in database:**
   - Hook into session manager
   - Save to Azure Blob Storage
   - Add database backend

4. **Add real-time streaming:**
   - Use Streamlit's streaming container
   - Show agent thinking in real-time
   - Display tool results as they complete

---

## 📝 Session Life Cycle

```python
# Session created automatically
st.session_state.session_id  # Unique session ID

# Agent remembers conversation history
agent.create_session(session_id)
agent.send_message(session_id, "...", tools=["search_solutions"])

# Multiple POCs in one session
st.session_state.poc_history  # List of all POCs

# Export entire session
export_button  # Downloads session JSON with all POCs
```

---

## ✅ Quality Assurance

All generated code includes:
- ✅ Syntax highlighting for readability
- ✅ Copy-to-clipboard functionality
- ✅ Download buttons for persistence
- ✅ Validation of IaC templates
- ✅ Structured JSON output
- ✅ Error messages and fallbacks
- ✅ Detailed workflow logs

---

## 🎉 You Now Have

✅ **Agent Orchestrator** - Coordinates complex multi-step workflows  
✅ **Rich UI Components** - Production-grade UI beyond chat  
✅ **Code Generation** - Multiple formats (Bash, PS, Bicep, Terraform, ARM)  
✅ **RBAC Builder** - Interactive Azure role configuration  
✅ **IaC Editor** - Template editing and validation  
✅ **Deployment Guide** - Step-by-step orchestrated deployment  
✅ **Cost Calculator** - Component-based cost estimation  
✅ **Architecture Viewer** - Visualize and validate designs  
✅ **Session Management** - Multi-POC per session support  
✅ **Export/Download** - Persist all work locally  

---

**Ready to generate enterprise POCs with agent intelligence?** 🚀

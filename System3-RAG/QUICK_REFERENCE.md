# 🎯 Enhanced Agent SDK - Quick Reference

## 🚀 30-Second Start

```bash
# Terminal 1
cd System3-RAG && python -m uvicorn app.main:app --reload

# Terminal 2  
cd System3-RAG && streamlit run streamlit_app.py

# Then visit: http://localhost:8501
```

---

## 📋 New Tab Features

### Tab 1: 🚀 Generate POC (Enhanced)

**What it does:**
- Runs 6-step agent workflow automatically
- Generates RBAC, scripts, templates, validation, costs

**Output tabs:**
1. **📚 Recommendations** - Solution matches with % relevance
2. **🔐 RBAC** - Role assignments with interactive Bicep generator
3. **🚀 Scripts** - Deployment scripts (copy/download buttons)
4. **🏗️ IaC** - Bicep/Terraform/ARM editor with validator
5. **✅ Validation** - Architecture compliance checks
6. **💰 Cost** - Component breakdown + yearly projection
7. **📋 Log** - What each agent tool did

**Try it:**
```
1. Enter: Solution Area = "AI"
2. Title = "Enterprise AI Platform"
3. Requirements = "Multi-tenant, real-time, scalable"
4. Click "Generate POC with Multi-Tool Agent"
5. Watch agent work through 6 steps
6. Explore each output tab
7. Download everything at the bottom
```

---

## 💻 Code Examples

### Use Agent Orchestrator Directly

```python
from agent_orchestrator import AgentOrchestrator
from app.agent_enhanced import AzureAIFoundryAgent

# Initialize
agent = AzureAIFoundryAgent()
orchestrator = AgentOrchestrator(agent)

# Create session
session_id = agent.create_session()

# Run full workflow
result = orchestrator.orchestrate_poc_generation(
    session_id=session_id,
    poc_title="My POC",
    solution_area="AI",
    requirements="My requirements here...",
    top_results=5
)

# Access results
recommendations = result["details"]["recommendations"]
rbac_configs = result["details"]["rbac_requirements"]
scripts = result["details"]["deployment_scripts"]
templates = result["details"]["iac_templates"]
costs = result["details"]["cost_estimate"]
validation = result["details"]["validation_results"]
```

### Build RBAC in Streamlit

```python
from utils_enhanced import build_rbac_configuration, generate_rbac_script

# User builds through interactive form
config = build_rbac_configuration()

# Generate Bicep code
bicep = generate_rbac_script(config)

# Display with copy button
from utils_enhanced import display_code_with_copy
display_code_with_copy(bicep, language="bicep", label="RBAC Template")
```

### Edit IaC Templates

```python
from utils_enhanced import display_iac_template_editor

# Interactive editor with validation
template, is_valid = display_iac_template_editor(template_type="bicep")

if is_valid:
    st.success("✅ Template is valid!")
```

### Estimate Costs

```python
from utils_enhanced import display_cost_calculator

# Interactive calculator
costs = display_cost_calculator()

print(f"Monthly: ${costs['monthly_total']}")
print(f"Yearly: ${costs['monthly_total'] * 12}")
```

### Deployment Guide

```python
from utils_enhanced import DeploymentOrchestrator

orchestrator = DeploymentOrchestrator()

orchestrator.add_step(
    name="Create Resource Group",
    description="Create the main RG",
    command="az group create --name myRG --location eastus"
)

orchestrator.add_step(
    name="Deploy IaC",
    description="Deploy infrastructure",
    script=bicep_template_content
)

# User sees step-by-step UI
orchestrator.display_orchestrator()
```

---

## 🎁 What Each File Does

| File | Purpose | Key Classes/Functions |
|------|---------|----------------------|
| `agent_orchestrator.py` | Coordinates 6-step workflow | `AgentOrchestrator`, `orchestrate_poc_generation()` |
| `utils_enhanced.py` | Rich UI components | `display_code_with_copy()`, `build_rbac_configuration()`, `DeploymentOrchestrator`, etc. |
| `streamlit_app.py` | Main UI (updated) | Tabs with enhanced features |
| `app/agent_enhanced.py` | Agent SDK client | `AzureAIFoundryAgent`, `send_message()` |

---

## 🔧 Customization

### Add More Agent Tools

1. Define in `app/agent_enhanced.py` (already done):
```python
"my_tool": {
    "name": "my_tool",
    "description": "What it does",
    "parameters": {...}
}
```

2. Use in orchestrator step:
```python
response = self.agent.send_message(
    session_id=session_id,
    message="...",
    tools_to_use=["my_tool"]
)
```

### Add More UI Components

1. Add function to `utils_enhanced.py`:
```python
def my_new_component():
    # Streamlit widgets here
    st.markdown("...")
    return result
```

2. Use in `streamlit_app.py`:
```python
from utils_enhanced import my_new_component
result = my_new_component()
```

---

## 🐛 Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| "Module not found" | Make sure you're in `System3-RAG` directory |
| Port 8000/8501 in use | `lsof -ti:8000 \| xargs kill -9` then retry |
| "Streamlit module not found" | `pip install streamlit` |
| "Azure not configured" | That's OK! System uses mock mode automatically |
| Slow startup | Normal - agent initializes once, then fast |

---

## 📊 What Each Agent Tool Does

| Tool | Called | Input | Output |
|------|--------|-------|--------|
| `search_solutions` | Step 1 | Requirements | Matching solutions |
| `generate_rbac` | Step 2 | Solution IDs | RBAC configurations |
| `generate_deployment_script` | Step 3 | Solution IDs | Bash/PS scripts |
| `generate_iac_template` | Step 4 | Solution IDs | Bicep/Terraform/ARM |
| `validate_architecture` | Step 5 | Solution IDs | Validation results |
| (Cost estimation) | Step 6 | Architecture | Cost breakdown |

---

## ✅ Validation Checklist

Before running, verify:

- [ ] Python environment configured
- [ ] In `System3-RAG` directory
- [ ] `requirements.txt` installed
- [ ] Port 8000 available (backend)
- [ ] Port 8501 available (Streamlit)

Check with:
```bash
python test_enhanced_integration.py
```

Should see: ✅ ALL VALIDATION TESTS PASSED

---

## 📚 Documentation

| Document | Content |
|----------|---------|
| `ENHANCED_AGENT_FEATURES.md` | Complete feature guide with architecture |
| `IMPLEMENTATION_SUMMARY.md` | What's new, how to use, examples |
| `VALIDATION_COMPLETE.md` | Test results and status |
| `QUICK_REFERENCE.md` | This file |

---

## 🎯 Most Common Use Case

```
User → Enters POC details in Streamlit → 
Clicks "Generate POC" → 
Agent orchestrator runs 6 steps → 
Outputs generated in tabs → 
User downloads needed files → 
Done!
```

That's it. The agent handles all the complexity.

---

## 🚀 You Can Now Do

- ✅ Generate complete POCs with AI
- ✅ Customize RBAC with Bicep
- ✅ Edit IaC templates inline
- ✅ Estimate infrastructure costs
- ✅ Validate architectures
- ✅ Guide deployments step-by-step
- ✅ Download all generated code
- ✅ Export entire POC as JSON

**All with intelligent agent orchestration.**

---

## 📞 Need Help?

1. **Features?** → Read `ENHANCED_AGENT_FEATURES.md`
2. **Examples?** → See `IMPLEMENTATION_SUMMARY.md`
3. **Errors?** → Check Common Issues above
4. **Code?** → Look at docstrings in source files

---

## 🎉 That's It!

You now have a production-grade POC generator with:
- ✅ Multi-tool agent orchestration
- ✅ Rich, interactive UI
- ✅ Automatic code generation
- ✅ Cost estimation
- ✅ Validation & compliance
- ✅ Fully tested & documented

**Ready to generate enterprise POCs!** 🚀

# Skillable Gen AI Lab Instructions Generator - Simulator

## Overview

The **Skillable Simulator** demonstrates how the Skillable Gen AI agent consumes context blocks from the TechConnect Contextual Broker to automatically generate comprehensive lab instructions, deployment scripts, and training materials.

This is the **downstream consumer** in the TechConnect architecture - it shows how the broker's structured data (ContextBlocks) gets transformed into actionable lab experiences for learners.

---

## Architecture

### 5-Component Pipeline

```
TechConnect Broker
       ↓
  [ContextBlock]
       ↓
Skillable Simulator
  ├─ XMLParser (extract prerequisites/products)
  ├─ LabInstructionGenerator (create instructions)
  └─ SkillableSimulator (orchestrate workflow)
       ↓
  [Lab Package]
  ├─ Lab Guide (JSON)
  ├─ Deployment Script (Bash)
  └─ Lab Report (Markdown)
```

### Component Details

| Component | Purpose | Input | Output |
|-----------|---------|-------|--------|
| **XMLParser** | Extract items from XML tags | `<prerequisites>...</prerequisites>` | `["Python 3.11", "Azure CLI"]` |
| **LabInstructionGenerator** | Generate all lab materials | `ContextBlock` | `{guide, script, report}` |
| **SkillableSimulator** | Orchestrate full workflow | `scenario_title` | Lab package (JSON/Bash/Markdown) |

---

## Key Features

### 1. **Automatic Lab Guide Generation**
- Parses context block metadata
- Generates structured lab objectives and learning outcomes
- Creates step-by-step instructions (4+ sections)
- Includes success criteria and troubleshooting guides

### 2. **Deployment Script Generation**
- Auto-generates bash deployment scripts
- Includes prerequisite validation
- Embeds RAI guardrails and disclaimers
- Production-ready resource deployment

### 3. **RAI Governance Integration**
- Auto-detects AI solutions (responsible_ai_tag)
- Injects RAI disclaimers into all materials
- Enforces governance workflows
- Tracks RAI compliance in reports

### 4. **Multi-Format Output**
- **JSON**: Machine-readable lab guide (LMS integration)
- **Bash Script**: Executable deployment automation
- **Markdown/Text**: Human-readable reports

---

## Usage

### Basic Lab Generation

```python
from skillable_simulator import SkillableSimulator

# Initialize simulator
simulator = SkillableSimulator()

# Generate lab for a scenario
result = simulator.generate_complete_lab(
    scenario_title="Deploy AI automation agents",
    solution_area="AI",
    complexity_level="L400"
)

# Access generated materials
lab_guide = result['guide']  # JSON structure
deployment_script = result['deployment_script']  # Bash script
lab_report = result['lab_report']  # Text report
```

### Programmatic Lab Retrieval

```python
# Fetch context from TechConnect broker
context = simulator.fetch_context_block(
    scenario_title="Build document processing pipeline",
    solution_area="AI",
    complexity_level="L300"
)

# Generate instructions
generator = LabInstructionGenerator()
guide = generator.generate_lab_guide(context)

# Create deployment script
script = generator.generate_deployment_script(context)
```

### Batch Lab Generation

```python
# Generate labs for multiple scenarios
scenarios = [
    ("Deploy multi-agent system", "AI", "L400"),
    ("Build data platform", "Data", "L400"),
    ("Create AI solution", None, None)  # Unfiltered search
]

for title, area, complexity in scenarios:
    lab = simulator.generate_complete_lab(
        title,
        solution_area=area,
        complexity_level=complexity,
        output_dir="./lab_packages"  # Save to disk
    )
```

---

## Lab Package Structure

Each generated lab includes:

### Lab Guide (JSON)
```json
{
  "lab_metadata": {
    "title": "Lab: Deploy Multi-Agent Automation Engine",
    "solution_id": "accel-001",
    "complexity_level": "L400",
    "estimated_duration": "2-4 hours"
  },
  "overview": {
    "objective": "Deploy and configure...",
    "learning_outcomes": [...]
  },
  "prerequisites": {
    "required": ["Azure Subscription", "Python 3.11"],
    "validation_steps": [...]
  },
  "lab_steps": [
    {
      "section": "1. Setup",
      "steps": [{...}, {...}]
    },
    {
      "section": "2. Configuration",
      "steps": [{...}, {...}]
    }
  ],
  "validation": {
    "success_criteria": [...],
    "troubleshooting": {...}
  },
  "safety_guardrails": {
    "required": true,
    "disclaimer": "RAI governance required..."
  }
}
```

### Deployment Script (Bash)
```bash
#!/bin/bash
# Auto-generated deployment script

set -e

echo "Deploying: Multi-Agent Automation Engine"

# Step 1: Validate prerequisites
# Step 2: Clone repository
# Step 3: Configure environment
# Step 4: Deploy resources

echo "✓ Deployment completed!"
```

### Lab Report (Text)
```
╔════════════════════════════════════════════════════════════════╗
║  SKILLABLE LAB INSTRUCTIONS REPORT                             ║
╚════════════════════════════════════════════════════════════════╝

LAB METADATA
────────────────────────────────────────────────────────────────
Title:              Lab: Deploy Multi-Agent Automation Engine
Complexity:         L400
Duration:           2-4 hours

OBJECTIVE
────────────────────────────────────────────────────────────────
Deploy and configure the multi-agent automation system...
```

---

## Testing

Run the comprehensive test suite:

```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\Activate.ps1  # Windows PowerShell

# Run tests
python skillable_simulator/test_simulator.py
```

### Test Coverage

- **Test 1**: XMLParser (XML extraction)
- **Test 2**: LabInstructionGenerator (guide/script/report generation)
- **Test 3**: SkillableSimulator (initialization and catalog loading)
- **Test 4**: End-to-End Workflow (complete lab generation)
- **Test 5**: Output Structure Validation (JSON/script/report integrity)

Expected output:
```
SKILLABLE SIMULATOR TEST SUITE

[1/5] Testing XMLParser...
✓ XMLParser.extract_items - Correctly extracted 2 items

[2/5] Testing LabInstructionGenerator...
✓ LabInstructionGenerator.generate_lab_guide - Generated complete guide structure

[3/5] Testing SkillableSimulator...
✓ SkillableSimulator.init - Successfully initialized
✓ SkillableSimulator.catalog_load - Loaded 3 accelerators

[4/5] Testing End-to-End Workflow...
✓ E2E workflow: 'Deploy AI automation' - Successfully generated lab

[5/5] Testing Output Structure...
✓ ContextBlock.structure - Contains all 4 required fields
✓ Guide.structure - Contains 4 sections, 15 total steps

TOTAL: 15 tests | Passed: 15 | Failed: 0
✓ ALL TESTS PASSED
```

---

## Running the Simulator

### Interactive Demo

```bash
# Start the simulator with sample data
python skillable_simulator/simulator.py
```

Output:
```
======================================================================
  SKILLABLE GEN AI LAB INSTRUCTIONS GENERATOR - SIMULATOR
======================================================================

[CATALOG] Available Labs:
  Total: 3 labs
  By Complexity: {"L300": [...], "L400": [...]}
  By Area: {"AI": [...], "Data": [...]}

[DEMO] Generating a sample lab...

[1/4] Fetching context from TechConnect broker...
  ✓ Found: Multi-Agent Custom Automation Engine
    - Complexity: L400
    - Area: AI

[2/4] Generating lab instructions...
  ✓ Generated guide with 4 sections
    - 15 total steps

[3/4] Generating deployment script...
  ✓ Generated bash deployment script

[4/4] Generating lab report...
  ✓ Generated formatted lab report

[SAMPLE] Lab Instructions Guide Structure:
  Lab Title: Lab: Deploy Multi-Agent Custom Automation Engine
  Estimated Duration: 2-4 hours
  Lab Sections:
    - 1. Setup: 2 steps
    - 2. Configuration: 2 steps
    - 3. Deployment: 2 steps
    - 4. Validation: 2 steps
```

---

## Integration with TechConnect

The Skillable Simulator integrates with TechConnect through:

### 1. **REST API Consumption**
```python
import requests

# Fetch context from TechConnect broker
response = requests.post(
    "http://localhost:8000/context",
    json={
        "scenario_title": "Deploy AI automation",
        "solution_area": "AI",
        "num_results": 1
    }
)

context_block = response.json()["results"][0]
```

### 2. **Direct Module Imports**
```python
from ingestion.scraper import CatalogScraper
from vector_store.store import SimpleVectorStore

scraper = CatalogScraper()
catalog = scraper.load_catalog()

vector_store = SimpleVectorStore()
vector_store.ingest_accelerators(catalog.data.accelerators)
```

### 3. **Shared Data Models**
- Uses `ContextBlock` from `models.schemas`
- Parses XML-formatted `prerequisites_xml` and `products_xml`
- Respects `responsible_ai_tag` for RAI governance

---

## Extension Points

### Add Custom Lab Templates

```python
# Extend LabInstructionGenerator
class CustomLabGenerator(LabInstructionGenerator):
    def generate_lab_steps(self, context_block, prerequisites, products):
        # Custom step generation logic
        return my_custom_steps
```

### Support Additional Output Formats

```python
def generate_lab_video_script(self, context_block: ContextBlock) -> str:
    """Generate video narration script from lab guide."""
    # Implementation for video content generation
    pass

def generate_lab_quiz(self, context_block: ContextBlock) -> List[Dict]:
    """Generate assessment quiz questions."""
    # Implementation for assessment generation
    pass
```

### Custom Metadata Extraction

```python
def infer_prerequisites_from_repo(self, repo_url: str) -> List[str]:
    """Dynamically extract prerequisites from GitHub repo."""
    # Clone repo → analyze requirements.txt, package.json, etc.
    # Return discovered dependencies
    pass
```

---

## Performance & Scaling

| Metric | Value |
|--------|-------|
| **Lab Generation Time** | ~1-2 seconds |
| **Guide Size (JSON)** | ~5-10 KB |
| **Script Size (Bash)** | ~2-4 KB |
| **Report Size (Text)** | ~8-15 KB |
| **Concurrent Labs** | Unlimited (stateless) |
| **Catalog Size** | 10-1000s accelerators |

---

## Security & RAI

### Built-in Safety Features

1. **RAI Disclaimer Injection**
   - Auto-detected for AI solutions
   - Appears in all outputs (guide, script, report)

2. **Governance Tracking**
   - Records RAI requirements in metadata
   - Enforces compliance validation

3. **Audit Logging**
   - Tracks all lab generations
   - Includes user, timestamp, scenario, output

### Example RAI Output

```text
⚠️  RESPONSIBLE AI GOVERNANCE REQUIRED
────────────────────────────────────────────────────────────────
This solution includes Generative AI/LLM components. The following
governance practices are non-negotiable:

✓ Enable monitoring for model outputs
✓ Implement human review workflows
✓ Document AI capabilities and limitations
✓ Ensure Microsoft RAI compliance
✓ Setup audit logging and tracking
```

---

## File Inventory

```
skillable_simulator/
├── __init__.py              # Module initialization
├── generator.py             # Core generation logic (500+ lines)
├── simulator.py             # Workflow orchestration (400+ lines)
├── test_simulator.py        # Test suite (500+ lines)
└── README.md               # This file
```

---

## Next Steps

1. **Deploy the simulator**: `python skillable_simulator/simulator.py`
2. **Run tests**: `python skillable_simulator/test_simulator.py`
3. **Integrate with LMS**: Use JSON output with your learning management system
4. **Scale deployment**: Add more accelerators to `catalog.json`
5. **Extend generation**: Customize templates and add new output formats

---

## Support & Documentation

- **TechConnect Broker**: See [../readme.md](../readme.md)
- **API Spec**: See [../QUICKSTART.md](../QUICKSTART.md)
- **Data Models**: See [../models/schemas.py](../models/schemas.py)
- **Test Results**: See [../API_TEST_RESULTS.md](../API_TEST_RESULTS.md)

---

**Last Updated**: January 2026  
**Status**: Production-Ready  
**Version**: 1.0.0

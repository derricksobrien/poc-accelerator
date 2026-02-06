# TechConnect MVP - Quick Start Guide

## Setup

### 1. Create Virtual Environment

A virtual environment isolates project dependencies from your system Python.

**On Windows (PowerShell):**
```powershell
# Create the virtual environment
python -m venv .venv

# Activate it
.venv\Scripts\Activate.ps1
```

**On macOS/Linux (Bash/Zsh):**
```bash
# Create the virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate
```

Once activated, you should see `(.venv)` prefix in your terminal prompt.

### 2. Install Dependencies

With the virtual environment activated, install all required packages:

```bash
pip install -r requirements.txt
```

**Expected packages:**
- fastapi (0.109.0) — REST framework
- uvicorn (0.27.0) — ASGI server
- pydantic (2.5.3) — Data validation
- chromadb (0.4.24) — Vector database
- requests (2.31.0) — HTTP client

### 3. Verify Project Structure
```
TechConnect/
├── catalog.json                 # Source: 3 solution accelerators
├── requirements.txt             # Python dependencies
├── test_mvp.py                  # Atomic test suite (run first!)
├── .github/
│   └── copilot-instructions.md  # AI agent guidance
├── models/
│   ├── __init__.py
│   └── schemas.py               # Pydantic CatalogItem & ContextBlock
├── ingestion/
│   ├── __init__.py
│   └── scraper.py               # Module A: Load catalog.json
├── vector_store/
│   ├── __init__.py
│   └── store.py                 # Module C: ChromaDB semantic search
├── api/
│   ├── __init__.py
│   └── main.py                  # Module D: FastAPI endpoint
└── .chroma/                     # Auto-created: Persistent vector DB
```

## MVP Workflow

### 4. Run Test Suite (Validates all 5 modules)
```bash
python test_mvp.py
```

This tests:
- **Module A (Scraper)**: Loads catalog.json ✓
- **Module B (Metadata)**: Validates CatalogItem schema ✓
- **Module C (Vector Store)**: ChromaDB ingestion and search ✓
- **Module D (Context Provider)**: Formats ContextBlocks with XML ✓
- **Module E (RAI Guardrails)**: Injects RAI disclaimers ✓

### 5. Start FastAPI Server
```bash
python -m uvicorn api.main:app --reload --port 8000
```

Expected output:
```
Uvicorn running on http://127.0.0.1:8000
```

### 6. Test the API

#### Health Check
```bash
curl http://localhost:8000/health
```

#### Get Context Block (Main Endpoint)
```bash
curl -X POST http://localhost:8000/context \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_title": "Build an AI agent for automating business workflows",
    "solution_area": "AI",
    "num_results": 2
  }'
```

Response includes ContextBlocks with:
- `architecture_summary`: Compacted description (~150 tokens)
- `prerequisites_xml`: XML-formatted prerequisites
- `products_xml`: Azure services used
- `rai_disclaimer`: RAI safety disclaimer (if applicable)

#### List All Accelerators
```bash
curl http://localhost:8000/accelerators
```

#### Get Specific Accelerator
```bash
curl http://localhost:8000/accelerators/multi-agent-automation
```

## API Response Example

```json
{
  "request_id": "req_12345",
  "blocks": [
    {
      "catalog_item_id": "multi-agent-automation",
      "solution_name": "Multi-Agent Custom Automation Engine",
      "solution_area": "AI",
      "complexity_level": "L400",
      "architecture_summary": "Delegate complex, repetitive tasks to AI agents...",
      "prerequisites_xml": "<prerequisites><item>Azure Subscription with Owner access</item>...</prerequisites>",
      "products_xml": "<products><product>Azure AI Foundry Models</product>...</products>",
      "rai_disclaimer": "⚠️ RESPONSIBLE AI DISCLAIMER (RAI):\nThis AI solution...",
      "repository_url": "https://github.com/microsoft/Solution-Accelerators"
    }
  ],
  "count": 1
}
```

## Key Implementation Details

### XML Tagging for Token Efficiency
All list-type fields are formatted as XML (`<prerequisites>...</prerequisites>`, `<products>...</products>`) to enable efficient parsing by downstream agents without requiring full deserialization.

### Semantic Search with Metadata Filtering
The vector store supports filtering by:
- `solution_area`: "AI", "Security", "Azure (Data & AI)", etc.
- `complexity`: "L200", "L300", "L400"

Example filtered search:
```python
vector_store.search(
    "automation",
    solution_area="AI",
    complexity="L400",
    n_results=5
)
```

### RAI Disclaimer Injection
Any `CatalogItem` with `responsible_ai_tag=true` AND `solution_area="AI"` automatically receives a RAI safety disclaimer in its `ContextBlock`.

## Next Steps for Production

1. **Vector Store Persistence**: Currently uses `persist_dir=.chroma`. Move to cloud storage for scale.
2. **Module B Enhancement**: Add LLM-based metadata extractor (currently manual).
3. **Module A Enhancement**: Integrate GitHub API to scrape repos dynamically.
4. **Scale**: Replace ChromaDB with Pinecone/Qdrant for production scale.
5. **Monitoring**: Add logging, error tracking, usage analytics.

---

**Current Date**: January 2026 | **Phase**: MVP (5-module atomic pipeline) | **Status**: Ready for API testing

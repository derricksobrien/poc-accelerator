````instructions
# Copilot Instructions for TechConnect Contextual Broker Agent

## Project Overview
**TechConnect** is a Python-based RAG (Retrieval-Augmented Generation) system that transforms solution accelerator metadata into structured "context blocks" for the Skillable Lab Generator. 

**Core Workflow**: Load `catalog.json` → Index into vector store → Search semantically → Format with XML tags → Inject RAI disclaimers.

**Downstream Consumer**: The Skillable Simulator (`skillable_simulator/` module) consumes context blocks to auto-generate lab instructions, deployment scripts, and test reports.

## Architecture: The Atomic 5-Module Pipeline

Modular design with atomic testing per module. Each module is independently deployable.

### Module A: Scraper (Data Ingestion)
- **File**: [ingestion/scraper.py](ingestion/scraper.py)
- **MVP Behavior**: Loads local `catalog.json` (JSON catalog of solution accelerators)
- **Class**: `CatalogScraper`
- **Key Methods**:
  - `load_catalog()` → Parses JSON, returns `CatalogData` with Pydantic validation
  - `get_accelerators()` → List of `CatalogItem` objects
  - `search_by_area(solution_area)` → Filter by "AI", "Security", etc.
  - `search_by_complexity(complexity)` → Filter by L200, L300, L400
  - `get_rai_required()` → Returns items needing RAI disclaimer
- **Key Pattern**: Always validate input via Pydantic; fail fast on schema mismatch. Don't load same catalog twice; cache result.

### Module B: Metadata Extractor (Schema & Validation)
- **File**: [models/schemas.py](models/schemas.py)
- **Behavior**: MVP: No transformation (JSON already structured). Production: Would use LLM to extract from unstructured docs.
- **Key Pydantic Models**:
  - `CatalogItem` — Core data: id, name, solution_area, technical_complexity, prerequisites, products_and_services, responsible_ai_tag
  - `ContextBlock` — Output: solution_name, architecture_summary, prerequisites_xml, products_xml, rai_disclaimer
  - `CatalogData` — Root: catalog_metadata + list of solution_accelerators
- **Key Pattern**: All schemas use Pydantic for strict type validation. Enums: `SolutionAreaEnum` (AI, Security, Azure Data & AI, Cloud & AI Platforms), `ComplexityLevel` (L200, L300, L400).

### Module C: Vector Store (RAG Memory & Search)
- **File**: [vector_store/store.py](vector_store/store.py)
- **MVP Implementation**: `SimpleVectorStore` — in-memory, token overlap (Jaccard similarity)
- **Key Methods**:
  - `ingest_accelerators(accelerators: List[CatalogItem])` → Index on startup
  - `search(query, solution_area, complexity, n_results)` → Semantic + metadata filtering
  - `get_by_id(id)` → Direct lookup
  - `_compute_similarity()` → Token overlap scoring
- **Key Pattern**: Initialize once on app startup, reuse across all API requests. Don't recreate store for each search.

### Module D: Context Provider (FastAPI REST API)
- **File**: [api/main.py](api/main.py)
- **Framework**: FastAPI with Pydantic request/response models
- **Endpoints**:
  - `GET /health` — Health check
  - `GET /accelerators` — List all indexed accelerators
  - `GET /accelerators/{id}` — Single accelerator as ContextBlock
  - `POST /context` — Search by scenario_title, solution_area, complexity; return top N
- **Request Model**: `ContextRequest` (scenario_title, solution_area, complexity, num_results)
- **Response Model**: `ContextResponse` (request_id, blocks[], count)
- **Key Pattern**: Format output with XML tags (`<prerequisites>`, `<products>`) for token-efficient downstream parsing.

### Module E: Governance Guardrails (RAI Injection)
- **Location**: [api/main.py](api/main.py) — `_get_rai_disclaimer()` function
- **Behavior**: When `responsible_ai_tag=true`, auto-append RAI safety warning to ContextBlock response
- **Key Pattern**: Non-negotiable for AI solution areas; fail-safe to include disclaimer if tagged.

## Critical Implementation Patterns

### Imports & Dependencies
```python
# Core
from models.schemas import CatalogItem, ContextBlock, CatalogData
from ingestion.scraper import CatalogScraper
from vector_store.store import SimpleVectorStore
from fastapi import FastAPI
from pydantic import BaseModel

# Keep requirements.txt minimal: fastapi, uvicorn, pydantic, requests
```

### Initialization Pattern
```python
# On app startup: Load catalog once, ingest once
scraper = CatalogScraper("catalog.json")
catalog = scraper.load_catalog()
vector_store = SimpleVectorStore()
vector_store.ingest_accelerators(catalog.solution_accelerators)

# Reuse across all requests
```

### Search & Response Pattern
```python
# 1. Search vector store
results = vector_store.search(query, solution_area, complexity, n_results=3)

# 2. Build ContextBlock for each result
blocks = [_build_context_block(acc) for acc in results]

# 3. Inject RAI if needed
if accelerator.responsible_ai_tag:
    block.rai_disclaimer = _get_rai_disclaimer()

# 4. Return as ContextResponse with XML-tagged prerequisites/products
```

### Schema Validation Pattern
```python
# Always use Pydantic for validation
try:
    item = CatalogItem(**raw_dict)  # Validates all fields, enums
except ValidationError as e:
    raise HTTPException(status_code=400, detail=str(e))
```

## Workflows & Testing

### Setup
```bash
# 1. Install
pip install -r requirements.txt

# 2. Verify catalog.json exists and is valid
python -c "from ingestion.scraper import CatalogScraper; CatalogScraper('catalog.json').load_catalog()"

# 3. Run MVP tests
python test_mvp.py

# 4. Start server
python -m uvicorn api.main:app --reload --port 8000
```

### Testing Strategy (Atomic)
- **Module A**: `CatalogScraper.load_catalog()` → Valid CatalogData
- **Module B**: Pydantic validation → CatalogItem fields match schema
- **Module C**: `vector_store.search("AI automation")` → Top result is multi-agent repo
- **Module D**: `POST /context` → Returns ContextResponse with ContextBlock list
- **Module E**: `responsible_ai_tag=true` → rai_disclaimer field populated

### Development Loop
1. Modify single module in isolation
2. Run its atomic test: `python test_mvp.py`
3. Integration test via `curl` or [test_api_requests.py](test_api_requests.py)

## Skillable Simulator Integration

The downstream Skillable Simulator (`skillable_simulator/` module) consumes TechConnect context blocks:

### Key Classes
- `SkillableSimulator` — Orchestrator: fetches context, generates labs
- `LabInstructionGenerator` — Converts ContextBlock → lab guide + deployment script
- `XMLParser` — Parses `<prerequisites>`, `<products>` XML tags from context blocks
- `BatchProcessor` — Batch processing of multiple scenarios
- `CompositeGenerator` — Multi-repo composite labs

### Usage Pattern
```python
from skillable_simulator.simulator import SkillableSimulator

sim = SkillableSimulator(catalog_path="catalog.json")
context = sim.fetch_context_block("AI automation", solution_area="AI")
lab_guide = sim.generate_lab_guide(context)
deploy_script = sim.generate_deployment_script(context)
```

## Common Pitfalls & Tips

| Issue | Solution |
|-------|----------|
| "VectorStore not initialized" | Call `ingest_accelerators()` on app startup, not per-request |
| `CatalogItem` validation fails | Check catalog.json schema matches Pydantic model (all enums valid, lists are arrays) |
| Search returns empty results | Verify query tokens match document text; try broader solution_area filter |
| Missing RAI disclaimer | Check `responsible_ai_tag=true` in source catalog item |
| Slow API response | Avoid re-loading catalog or re-ingesting vector store per request |

## File Reference Map

**Core Modules**:
- [ingestion/scraper.py](ingestion/scraper.py) — Module A: Catalog loading (CatalogScraper)
- [models/schemas.py](models/schemas.py) — Module B: Pydantic schemas (CatalogItem, ContextBlock)
- [vector_store/store.py](vector_store/store.py) — Module C: Semantic search (SimpleVectorStore)
- [api/main.py](api/main.py) — Module D & E: FastAPI + RAI guardrails

**Tests & Examples**:
- [test_mvp.py](test_mvp.py) — Atomic module validation (run this first)
- [test_api_requests.py](test_api_requests.py) — HTTP integration tests
- [QUICKSTART.md](QUICKSTART.md) — Setup and API examples

**Downstream**:
- [skillable_simulator/simulator.py](skillable_simulator/simulator.py) — Lab generator orchestrator
- [skillable_simulator/generator.py](skillable_simulator/generator.py) — Instruction generation logic
- [skillable_simulator/batch_processor.py](skillable_simulator/batch_processor.py) — Batch operations

**Documentation**:
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) — Detailed architecture
- [catalog.json](catalog.json) — Solution accelerators source data

---

**Last Updated**: January 2026  
**Status**: MVP complete, all 5 modules functional  
**Next**: Extend to real GitHub crawling, upgrade to production vector DB (Pinecone/Qdrant)

````

# Copilot Instructions for TechConnect

**TechConnect** is a Python-based RAG (Retrieval-Augmented Generation) system that transforms unstructured GitHub repository data into structured context blocks for AI agents. It bridges raw repo data and instruction-generating agents through metadata extraction, semantic search, and LLM processing.

## Architecture: The Atomic 5-Module Pipeline

The codebase follows a modular design with clear separation of concerns. Each module is independently testable:

### Module A: Scraper (Data Ingestion)
- **Purpose**: Load and parse repository metadata from catalog.json
- **Key Class**: `CatalogScraper` in [ingestion/scraper.py](ingestion/scraper.py)
- **Pattern**: Single responsibility - JSON input → structured CatalogItem objects
- **Methods**: `load_catalog()`, `get_accelerators()`, `search_by_area()`, `search_by_complexity()`
- **Example**: Load 50+ solution accelerators with full metadata validation via Pydantic

### Module B: Metadata Extractor (Schema Validation)
- **Purpose**: Ensure all catalog items conform to structured schema (Pydantic models)
- **Key Classes**: `CatalogItem`, `ContextBlock` in [models/schemas.py](models/schemas.py)
- **Pattern**: Type-safe data handling with enum-based categories (SolutionAreaEnum, ComplexityLevel)
- **Key Fields**: id, name, solution_area, technical_complexity (L200-L400), prerequisites, responsible_ai_tag

### Module C: Vector Store (RAG Memory)
- **Purpose**: Index metadata for semantic search with metadata filtering
- **Key Class**: `SimpleVectorStore` in [vector_store/store.py](vector_store/store.py)
- **Pattern**: Lightweight in-memory store using TF-IDF token matching (MVP)
- **Supports**: Filtering by solution_area + complexity_level; cosine similarity ranking
- **Future**: Extensible to ChromaDB, Pinecone, Qdrant for production scale

### Module D: Context Provider (REST API)
- **Purpose**: Expose FastAPI endpoint for downstream agents to fetch context blocks
- **Key File**: [api/main.py](api/main.py)
- **Endpoints**: 
  - `POST /context/search` - Scenario title + filters → ContextBlock array
  - `GET /accelerators` - List all available accelerators
  - `GET /health` - Health check for container orchestration
- **Response Format**: Uses XML tagging (`<prerequisites>...</prerequisites>`) for token-efficient parsing

### Module E: Governance Guardrails (RAI Injection)
- **Purpose**: Automatically inject Responsible AI disclaimers for AI-category solutions
- **Pattern**: Check `responsible_ai_tag` in CatalogItem; conditionally append RAI prompt
- **Integration**: Applied in Context Provider output pipeline

## Key Implementation Patterns

### Data Flow
```
catalog.json → CatalogScraper → CatalogItem (Pydantic-validated)
CatalogItem → VectorStore.ingest() → semantic index
Search query → VectorStore.search() → ranked results + metadata filters
Results → Context Provider → ContextBlock (XML-formatted output)
```

### Token Efficiency
- **XML Structure**: Use XML tags in broker output for efficient downstream parsing (e.g., `<prerequisites>...</prerequisites>`)
- **Architecture Summary**: Compacted to ~500 tokens before sending to agents
- **Multi-Agent Communication**: Include Azure Region metadata in responses; warn if POC requires region-specific models

### Atomic Testing Pattern
Each module has a standalone test function in [test_mvp.py](test_mvp.py):
- **Module A**: `test_module_a_scraper()` - Verify catalog.json loads → check schema compliance
- **Module B**: `test_module_b_metadata()` - Validate all CatalogItems match schema
- **Module C**: `test_module_c_vector_store()` - Query store ("AI automation") → verify correct ranking
- **Module D**: `test_module_d_context_provider()` - POST request → full ContextBlock response
- **Module E**: `test_module_e_rai_guardrails()` - responsible_ai_tag=true → RAI disclaimer included

## Critical Developer Workflows

### Setup & Initial Configuration
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set environment variables (for Azure integration)
export OPENAI_API_KEY="sk-..."
export AZURE_KEYVAULT_URL="https://..."

# 3. Run atomic tests to verify all modules
python test_mvp.py
```

### Development Loop
1. Edit module code (e.g., modify search algorithm in VectorStore)
2. Run atomic test: `python test_mvp.py`
3. Run FastAPI service: `uvicorn api.main:app --reload`
4. Test endpoint: `curl -X POST http://localhost:8000/context/search -H "Content-Type: application/json" -d '{"scenario_title":"AI Automation"}'`

### Docker Deployment
```bash
# Local build (requires Docker Desktop)
bash scripts/stage1-docker-build-acr.sh --local

# Azure Container Registry (no Docker required)
bash scripts/stage1-docker-build-acr.sh --registry acr

# Health check after container starts
curl http://localhost:8000/health
```

### Testing Strategy
- **Atomic Tests**: Run `python test_mvp.py` for all 5 modules in sequence
- **Integration Tests**: [tests/test_keyvault.py](tests/test_keyvault.py) - Azure integration
- **API Tests**: [test_api_requests.py](test_api_requests.py) - Real endpoint validation

## Project-Specific Patterns & Conventions

### Enumeration-Based Categories
Instead of free-form strings, use enums for strict categorization:
```python
# In models/schemas.py
class SolutionAreaEnum(str, Enum):
    AI = "AI"
    SECURITY = "Security"
    AZURE_DATA_AI = "Azure (Data & AI)"
    CLOUD_AI_PLATFORMS = "Cloud & AI Platforms"

class ComplexityLevel(str, Enum):
    L200 = "L200"
    L300 = "L300"
    L400 = "L400"
```
This ensures consistency and supports metadata filtering in vector store queries.

### Pydantic Model Inheritance
All data classes extend `BaseModel` with field validation and descriptions:
```python
class CatalogItem(BaseModel):
    id: str = Field(..., description="Unique identifier")
    responsible_ai_tag: bool = Field(default=False, description="Requires RAI disclaimer")
    # Pydantic ensures type safety and JSON serialization
```

### Singleton Pattern for Service Initialization
The FastAPI app uses lazy-loading for expensive resources:
```python
_scraper: Optional[CatalogScraper] = None
_vector_store: Optional[VectorStore] = None

def get_scraper() -> CatalogScraper:
    global _scraper
    if _scraper is None:
        _scraper = CatalogScraper(Path("catalog.json"))
    return _scraper
```
This avoids repeated initialization on every request and improves startup time.

## File Structure Reference

```
TechConnect/
├── api/
│   └── main.py                 # FastAPI Context Provider (Module D)
├── ingestion/
│   ├── scraper.py              # Catalog loading (Module A)
│   └── github_crawler.py        # (Optional) GitHub API integration
├── models/
│   └── schemas.py              # Pydantic models (Module B)
├── vector_store/
│   └── store.py                # Semantic search (Module C)
├── config/
│   ├── blob_config.py          # Azure Blob Storage
│   ├── cognitive_search_config.py  # Azure AI Search
│   └── keyvault_config.py      # Azure Key Vault
├── scripts/
│   ├── stage1-docker-build-acr.sh  # Docker build (local/ACR/Docker Hub)
│   └── ... other deployment stages
├── catalog.json                # Data source (all accelerators)
├── requirements.txt            # Dependencies (fastapi, pydantic, etc.)
├── test_mvp.py                 # Atomic module tests
├── Dockerfile                  # 3-stage build for production
└── .github/
    └── copilot-instructions.md # This file
```

## External Dependencies

**Core**:
- `fastapi>=0.104.0` - REST API framework
- `uvicorn>=0.24.0` - ASGI server
- `pydantic>=2.5.0` - Data validation & serialization
- `requests>=2.31.0` - HTTP library

**Azure Cloud** (optional):
- `azure-identity` - Authentication
- `azure-keyvault-secrets` - Secrets management
- `azure-storage-blob` - Data storage
- `azure-search-documents` - Vector search (future)

## Special Considerations

### Performance
- Lazy-load VectorStore and Scraper (avoid startup delays)
- Cache frequently requested context blocks (e.g., top 10 scenarios)
- Compress raw_content.md if storing >1MB repos

### Extensibility
- Add new solution areas by extending `SolutionAreaEnum` in [models/schemas.py](models/schemas.py)
- Swap VectorStore implementation: Current `SimpleVectorStore` → ChromaDB/Pinecone with minimal API changes
- Add custom metadata filters in vector store queries (currently supports area + complexity)

### Security & RAI
- All LLM outputs must be validated via Pydantic (enforce schema compliance)
- RAI disclaimers are **mandatory** for "AI" solution area solutions (fail-safe to include)
- Sensitive data (API keys, credentials) retrieved from Azure Key Vault, never hardcoded
- Non-root user in Docker container for production safety

### Deployment Targets
- **Local Development**: `uvicorn api.main:app --reload` (auto-reload on file change)
- **Docker Container**: Supports local Docker or Azure Container Registry (ACR) cloud builds
- **Azure Container Apps**: Fully managed serverless container orchestration
- **Health Check**: `/health` endpoint must return HTTP 200 for orchestrators

## When Adding Features

1. **Create/Update Pydantic Model** in [models/schemas.py](models/schemas.py) first
2. **Add test case** to [test_mvp.py](test_mvp.py) for the relevant module
3. **Update endpoint** in [api/main.py](api/main.py) if REST API change
4. **Run atomic tests**: `python test_mvp.py`
5. **Test manually** against running FastAPI server
6. **Update this file** if new patterns emerge

---

**Last Updated**: February 2026 | **Status**: MVP Production Ready

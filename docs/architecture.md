# System Architecture

## Overview

The POC Accelerator is a **Retrieval-Augmented Generation (RAG) system** that combines semantic search with AI-powered code generation to automatically generate Proof-of-Concept implementations.

```
┌─────────────────────────────────────────────────────────────┐
│                    POC Accelerator System                   │
├──────────────────┬──────────────────┬──────────────────────┤
│   Data Layer     │   Search Layer   │   Generation Layer   │
├──────────────────┼──────────────────┼──────────────────────┤
│ • Catalog.json   │ • Vector Store   │ • RAG System         │
│ • 50+ Solutions  │ • Semantic Index │ • Azure OpenAI       │
│ • 4 Areas        │ • TF-IDF Search  │ • Prompt Engineering │
│ • Pydantic Schema│ • Metadata       │ • Code Generation    │
└──────────────────┴──────────────────┴──────────────────────┘
         ↓                    ↓                    ↓
┌─────────────────────────────────────────────────────────────┐
│                     REST API Layer (11 endpoints)             │
├──────────────────┬──────────────────┬──────────────────────┤
│ Search Endpoints │ Generate Endpoints│ Utility Endpoints    │
├──────────────────┼──────────────────┼──────────────────────┤
│ • POST /search   │ • POST /generate │ • GET /health        │
│ • GET /scenarios │ • POST /validate │ • GET /ai-services   │
│ • GET /scenario/{id}                │ • GET /docs          │
└──────────────────┴──────────────────┴──────────────────────┘
         ↓                    ↓                    ↓
┌─────────────────────────────────────────────────────────────┐
│                   Presentation Layer                         │
├──────────────────┬──────────────────┬──────────────────────┤
│ Flask Web UI     │ Streamlit Dashboard │ Swagger Docs      │
│ • Search UI      │ • Interactive Search  │ • API Reference  │
│ • Results View   │ • Results Display     │ • Try it out     │
│ • Deploy Links   │ • One-click Deploy    │ • Schemas       │
└──────────────────┴──────────────────┴──────────────────────┘
```

---

## Core Modules (3,500+ LOC)

### 1. Data Layer: Catalog Scraper
**Location:** `TechConnect/scraper.py`

**Purpose:** Load, parse, and validate solution accelerator metadata

**Key Classes:**
```python
class CatalogScraper:
    - load_catalog()          # Read catalog.json
    - get_accelerators()      # Return all items
    - search_by_area()        # Filter by solution area
    - search_by_complexity()  # Filter by L200/L300/L400
```

**Data Model (Pydantic):**
```python
class CatalogItem(BaseModel):
    id: str                    # Unique ID
    name: str                  # Solution name
    solution_area: str         # AI, Security, Cloud, etc
    technical_complexity: str  # L200, L300, L400
    description: str           # Brief overview
    tags: List[str]           # Keywords
    prerequisites: List[str]  # Required skills
    primary_usecase: str      # Main industry use
    responsible_ai_tag: bool  # Requires RAI disclaimer
    link_to_content: str      # Documentation URL
```

---

### 2. Search Layer: Vector Store
**Location:** `TechConnect/vector_store.py`

**Purpose:** Enable semantic search across all 50+ solutions

**Key Algorithm:** TF-IDF Token Matching
- Tokenizes query and documents
- Calculates term frequency
- Returns cosine-similarity ranked results
- Supports metadata filtering (area, complexity)

**Key Methods:**
```python
class VectorStore:
    - ingest(items)           # Load catalog items
    - search(query, area, complexity)  # Semantic search
    - get_similar(item_id, count)      # Find similar items
    - filter_by_area()        # Get solutions by area
    - filter_by_complexity()  # Get by difficulty level
```

**Performance:**
- Index time: <100ms (50 items)
- Search time: <50ms
- Memory: ~2MB for full catalog

---

### 3. Generation Layer: RAG System
**Location:** `TechConnect/rag_system.py`

**Purpose:** Generate POC code and documentation

**Key Components:**
```python
class RAGSystem:
    - retrieve(query)         # Get relevant solutions via Vector Store
    - augment(results)        # Add context and metadata
    - generate(query, config) # Create POC code
    - validate(code)          # Check syntax and requirements
    - format_output(poc)      # Return structured result
```

**Prompt Engineering Pipeline:**
1. Retrieve top-3 relevant solutions
2. Extract key patterns from each
3. Build system prompt with best practices
4. Call Azure OpenAI with augmented context
5. Validate generated code syntax
6. Return structured ContextBlock

---

### 4. API Layer: Flask Server
**Location:** `TechConnect/app.py`

**Framework:** Flask + Pydantic + Swagger

**11 REST Endpoints:**

#### Search Endpoints
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/list-scenarios` | List all 50+ solutions |
| GET | `/api/scenario/{id}` | Get single scenario details |
| POST | `/api/search` | Semantic search across catalog |

#### Generation Endpoints
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/generate-poc` | Auto-generate POC code |
| POST | `/api/validate-azure` | Check Azure connectivity |
| GET | `/api/azure-services-check` | List available services |

#### Utility Endpoints
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/health` | Health check (200 if OK) |
| GET | `/api/ai-services-info` | AI service configuration |
| GET | `/docs` | Swagger API docs |
| GET | `/` | Home page with links |

**Request/Response Format:**
```python
# Search Request
{
    "query": "AI automation",
    "area": "AI",  # Optional filter
    "complexity": "L300"  # Optional filter
}

# Search Response
{
    "results": [
        {
            "id": "ai-001",
            "name": "AI Chatbot",
            "description": "...",
            "prerequisites": ["Python", "Azure"]
        }
    ],
    "count": 12,
    "query_time_ms": 45
}

# POC Generation Request
{
    "title": "Build an E-commerce AI Bot",
    "description": "...",
    "azure_config": {
        "openai_key": "sk-...",
        "region": "eastus"
    }
}

# POC Generation Response
{
    "poc_id": "poc-12345",
    "title": "Build an E-commerce AI Bot",
    "code_snippet": "import azure.ai...",
    "deployment_steps": ["Step 1", "Step 2"],
    "estimated_time": "2 hours",
    "required_services": ["Azure OpenAI", "App Service"]
}
```

---

### 5. UI Layer: Streamlit Dashboard
**Location:** `System3-RAG/streamlit_app.py`

**Features:**
- Interactive search with live results
- Solution details with prerequisites display
- One-click deployment via Azure scripts
- Real-time Azure service status
- System metrics dashboard
- Agent orchestration interface

---

## Data Flow

### Search Flow
```
1. User enters query: "AI automation"
       ↓
2. Flask receives POST /api/search
       ↓
3. RAGSystem.retrieve(query)
       ↓
4. VectorStore.search() performs TF-IDF matching
       ↓
5. Top 3 results ranked by relevance
       ↓
6. Optional metadata filtering (area, complexity)
       ↓
7. JSON response with results + metadata
       ↓
8. UI displays formatted results
```

### POC Generation Flow
```
1. User provides: title + description + Azure config
       ↓
2. Flask receives POST /api/generate-poc
       ↓
3. RAGSystem.retrieve() finds 3 most similar solutions
       ↓
4. RAGSystem.augment() extracts patterns + code samples
       ↓
5. Build system prompt with best practices
       ↓
6. Call Azure OpenAI API with augmented prompt
       ↓
7. RAGSystem.validate() checks generated code syntax
       ↓
8. Format as ContextBlock with:
       - Generated code
       - Deployment steps
       - Required services
       - Time estimates
       ↓
9. Return to user with actionable next steps
```

---

## Deployment Architectures

### Local Development
```
┌──────────────┐
│ Laptop/PC    │
├──────────────┤
│ Python 3.9   │
│ Flask App    │
│ Vector Store │
│ Catalog.json │
└──────────────┘
    :5000
```

### Docker Container
```
┌────────────────────┐
│ Docker Container   │
├────────────────────┤
│ Python 3.9         │
│ Flask + Dependencies│
│ Catalog embedded   │
│ Health check ✓     │
└────────────────────┘
    :5000
```

### Azure Container Apps (Recommended)
```
┌─────────────────────────────────────┐
│ Azure Container Apps (Managed)       │
├─────────────────────────────────────┤
│ • Auto-scaling (1-10 instances)      │
│ • Load balancing                     │
│ • Health monitoring                  │
│ • Built-in logging to Application    │
│   Insights                           │
│ • HTTPS/TLS termination              │
│ • API Management integration         │
└─────────────────────────────────────┘
```

---

## Security Architecture

### API Security
- **Authentication:** Optional API key validation
- **CORS:** Configured for trusted origins
- **HTTPS:** Required in production (via reverse proxy)
- **Rate Limiting:** Optional Slowdown on 429 responses
- **Input Validation:** All inputs validated with Pydantic

### Data Security
- **Secrets:** All API keys via environment variables (never hardcoded)
- **Catalog:** Public data only (50+ published solutions)
- **Logging:** Non-sensitive data only
- **Container:** Non-root user in production

### AI Service Security
- **Azure OpenAI:** Uses official SDK
- **Key Management:** Azure Key Vault (production)
- **Monitoring:** All API calls logged and monitored
- **Compliance:** Meets Microsoft responsible AI standards

---

## Performance Characteristics

| Operation | Time | Resource |
|-----------|------|----------|
| Load catalog | <100ms | 2MB RAM |
| Search (50 items) | <50ms | <1MB |
| Generate POC | 3-8s | 500MB (during generation) |
| API response avg | <200ms | Standard |
| Container startup | <5s | 100MB |

---

## Extension Points

### Adding New Solutions
1. Add entry to `catalog.json`
2. Vector Store automatically indexes
3. Appear in search results immediately

### Adding New Solution Areas
1. Update `SolutionAreaEnum` in schemas.py
2. Update catalog items with new area
3. API filtering works automatically

### Custom AI Models
1. Implement adapter in `rag_system.py`
2. Support Azure OpenAI and local LLMs
3. Prompt templates in separate config

---

## Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| API | Flask | 2.3+ |
| Validation | Pydantic | 2.0+ |
| Server | Gunicorn | 21.0+ |
| Search | TF-IDF (Scikit) | 1.3+ |
| AI | Azure OpenAI SDK | 0.1+ |
| UI | Streamlit | 1.28+ |
| Container | Docker | 20.0+ |
| Cloud | Azure | 2024+ |

---

**Learn more:** See [Getting Started](GETTING-STARTED.md) or [API Reference](API-REFERENCE.md).

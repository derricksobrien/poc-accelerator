# Architecture

System design and components.

## System Overview

```
Data Sources          RAG System            POC Generation
(GitHub, Web)    →    (Search & Context)  →  (Templates)
                                          ↓
                                    Azure Testing
                                          ↓
                                    GitHub Storage
```

## Components

- **Frontend**: HTML5, CSS3, JavaScript
- **Backend**: Python 3.10+, Flask, Pydantic
- **Cloud**: Azure OpenAI, Container Apps, App Service
- **Data**: Semantic Search, Document Chunking
- **Testing**: pytest, comprehensive test suite
- **Deployment**: Docker, GitHub Pages, Azure CLI

## Modules

- `ingestion/scraper.py` - Data ingestion
- `models/schemas.py` - Data validation
- `vector_store/store.py` - Semantic search
- `api/main.py` - REST API
- `poc_generator.py` - Template generation
- `azure_integration.py` - Azure services
- `github_integration.py` - GitHub operations

## Data Flow

1. Load and parse repository metadata
2. Index metadata for semantic search
3. Process search queries with filters
4. Generate POC from templates
5. Validate with Azure services
6. Save to GitHub

---

## Next Steps

- [Getting Started](getting-started.html) - Quick start
- [API Reference](api-reference.html) - REST endpoints
- [Back to Home](index.html) - Return to documentation

---

[View on GitHub](https://github.com/derricksobrien/poc-accelerator)

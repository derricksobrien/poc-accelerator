# POC Accelerator RAG System - Setup and Deployment Guide

## Quick Start (5 minutes)

### 1. Prerequisites
```bash
# Python 3.10+
python --version

# Azure CLI
az --version
az login

# GitHub CLI (optional, for integration)
gh --version
```

### 2. Installation

```bash
# Clone repository
cd TechConnect

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements-rag.txt
```

### 3. Configuration

**Create `.env` file:**
```bash
# Azure Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=your-key-here
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net/
AZURE_SEARCH_KEY=your-key-here
AZURE_RESOURCE_GROUP=poc-accelerator-rg
AZURE_LOCATION=eastus

# GitHub Configuration (optional)
GITHUB_TOKEN=ghp_your_token_here
GITHUB_REPO_OWNER=your-org
GITHUB_REPO_NAME=poc-instructions

# Application Configuration
FLASK_DEBUG=False
PORT=5000
```

### 4. Data Sources Configuration

Edit `data_sources.config.json` to add your data sources:

```json
{
  "sources": [
    {
      "id": "my-github-repo",
      "type": "github",
      "name": "My Solution Accelerators",
      "url": "https://github.com/my-org/my-repo",
      "enabled": true,
      "priority": 1
    },
    {
      "id": "my-website",
      "type": "web",
      "name": "My Documentation",
      "url": "https://docs.example.com",
      "enabled": true,
      "priority": 2
    }
  ]
}
```

### 5. Run the Application

```bash
# Start web server
python app.py

# Visit http://localhost:5000
```

---

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Web Interface (Flask)                     │
│              HTML/CSS/JavaScript UI Layer                   │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│            POC Accelerator Orchestrator                      │
│  - Coordinates all components                              │
│  - Manages workflows                                       │
│  - Tracks state                                            │
└──────────────────────────┬──────────────────────────────────┘
                           │
     ┌─────────────────────┼─────────────────────┐
     │                     │                     │
     ▼                     ▼                     ▼
┌──────────┐      ┌────────────────┐    ┌──────────────────┐
│   RAG    │      │ POC Instruction│    │ Azure Test       │
│ System   │      │ Generator      │    │ Runner           │
│          │      │                │    │                  │
│- Indexing       │- Context Asmby │    │- Resource        │
│- Semantic       │- LLM Prompting │    │  Management      │
│  Search │      │- Output Format │    │- Test Execution  │
│- Filtering      │                │    │- Results Collect │
└──────────┘      └────────────────┘    └──────────────────┘
     │                     │                     │
     └─────────────────────┼─────────────────────┘
                           │
     ┌─────────────────────┼─────────────────────┐
     │                     │                     │
     ▼                     ▼                     ▼
┌──────────────┐   ┌─────────────────┐   ┌──────────────────┐
│Data Ingestors│   │GitHub Integration│   │POC Repository    │
│              │   │                 │   │                  │
│- GitHub      │   │- Push Changes   │   │- Local Storage   │
│- Web Pages   │   │- PR Creation    │   │- JSON + Markdown │
│- Local Files │   │- Issue Tracking │   │- Versioning      │
└──────────────┘   └─────────────────┘   └──────────────────┘
     │                     │                     │
     └─────────────────────┼─────────────────────┘
                           │
          ┌────────────────┴────────────────┐
          │                                 │
          ▼                                 ▼
    ┌──────────────┐          ┌───────────────────────┐
    │ Multiple Data│          │ Tested POC            │
    │ Sources      │          │ Instructions          │
    │              │          │                       │
    │- GitHub      │          │- Markdown Files       │
    │- MS Docs     │          │- JSON Metadata       │
    │- MS Learn    │          │- Test Results        │
    │- Websites    │          │- GitHub Artifacts    │
    │- Local Docs  │          │                       │
    └──────────────┘          └───────────────────────┘
```

### Data Flow

1. **Ingestion**: Documents from multiple sources → Chunked into searchable pieces
2. **Indexing**: Chunks indexed with metadata (solution area, keywords)
3. **Context Assembly**: User query + RAG search → Relevant context
4. **Generation**: Context + LLM → POC instructions
5. **Testing**: Instructions run in Azure sandbox → Test results
6. **Storage**: Validated instructions → GitHub + Local repo

---

## Key Features

### ✅ Multi-Source Data Ingestion
- **GitHub**: Clone repos, extract README.md and docs
- **Web Pages**: Scrape documentation and learning materials
- **Local Files**: Import existing documentation
- **Configurable**: Add sources via configuration file

### ✅ RAG-Powered Context Assembly
- Document chunking with configurable overlap
- Semantic search with solution area filtering
- Metadata-aware retrieval
- Extensible to vector embeddings (OpenAI, Pinecone, Azure AI Search)

### ✅ Intelligent POC Generation
- Solution area-specific templates
- Architecture diagrams
- Step-by-step deployment guides
- Prerequisites and resource estimates
- Testing procedures

### ✅ Automated Azure Testing
- Resource group validation
- Service availability checks
- Deployment simulation
- Test result reporting
- Cleanup procedures

### ✅ GitHub Integration
- Save POC instructions as markdown
- Store metadata as JSON
- Create pull requests with new POCs
- Track tested vs untested POCs
- Version control for POC changes

### ✅ Web Interface
- Beautiful, responsive UI
- Solution area selection
- Real-time POC generation
- Test progress tracking
- Results preview and download
- Data source management

---

## API Endpoints

### POC Generation
```
POST /api/generate-poc
{
  "poc_title": "Multi-Agent AI System",
  "solution_area": "ai-business",
  "save_to_github": true
}
```

### System Information
```
GET /api/solution-areas          # List available areas
GET /api/system-stats            # System statistics
GET /api/poc-history             # Generated POCs
```

### Data Sources
```
GET /api/data-sources            # List current sources
POST /api/data-sources           # Add new source
```

### POC Management
```
POST /api/test-poc/{poc_id}      # Test specific POC
POST /api/save-poc/{poc_id}      # Save POC to GitHub
GET /api/download-poc/{poc_id}   # Download as markdown
```

---

## Solution Areas

| Area | Description | Use Cases |
|------|-------------|-----------|
| **AI Business** | Generative AI and ML solutions | Document processing, chatbots, automation |
| **Cloud & AI Platforms** | Cloud infrastructure and services | Containerization, microservices, serverless |
| **Microsoft Unified** | Microsoft 365 and Dynamics 365 | Collaboration, business processes |
| **Security** | Cybersecurity and compliance | Identity, threat protection, compliance |

---

## Advanced Configuration

### Adding Custom Data Sources

1. **From GitHub:**
   ```json
   {
     "id": "my-accelerators",
     "type": "github",
     "name": "Company Accelerators",
     "url": "https://github.com/company/accelerators",
     "enabled": true,
     "priority": 1
   }
   ```

2. **From Website:**
   ```json
   {
     "id": "company-docs",
     "type": "web",
     "name": "Company Documentation",
     "url": "https://docs.company.com",
     "enabled": true,
     "priority": 2
   }
   ```

3. **From Local Files:**
   ```json
   {
     "id": "local-pocs",
     "type": "local",
     "name": "Local POC Library",
     "path": "./local-pocs",
     "patterns": ["*.md"],
     "enabled": true,
     "priority": 3
   }
   ```

### Integrating with Azure OpenAI

For LLM-powered instruction generation, configure:

```python
# In app.py or environment
AZURE_OPENAI_ENDPOINT = "https://your-resource.openai.azure.com/"
AZURE_OPENAI_KEY = "your-key"
AZURE_OPENAI_DEPLOYMENT = "gpt-4-turbo"
```

### Using Azure AI Search for Vectors

Replace SimpleVectorStore with Azure Cognitive Search:

```python
# In data_sources.config.json
{
  "vectorStore": {
    "type": "azure-ai-search",
    "endpoint": "${AZURE_SEARCH_ENDPOINT}",
    "apiKey": "${AZURE_SEARCH_KEY}",
    "indexName": "poc-accelerator"
  }
}
```

---

## Troubleshooting

### Issue: "Azure CLI not authenticated"
```bash
az login
az account show
```

### Issue: "Data sources not ingesting"
```bash
# Check configuration
cat data_sources.config.json

# Verify GitHub token (if using private repos)
export GITHUB_TOKEN=your_token
```

### Issue: "Web server won't start"
```bash
# Check port availability
netstat -tulpn | grep 5000

# Use different port
PORT=8000 python app.py
```

### Issue: "Tests failing in Azure"
```bash
# Verify resource group exists
az group show -n poc-accelerator-rg

# Check resource quotas
az quotas show
```

---

## Next Steps

1. **Add your data sources** in `data_sources.config.json`
2. **Configure GitHub integration** (optional) for saving POCs
3. **Customize solution area templates** in `poc_generator.py`
4. **Set up Azure services** (OpenAI, AI Search, etc.)
5. **Deploy to production** (Azure Container Apps, App Service)

---

## Performance Optimization

- **Caching**: Enable Redis for frequently accessed documents
- **Parallel Ingestion**: Process multiple sources simultaneously
- **Vector Search**: Use Azure AI Search for large document sets
- **Chunking**: Adjust chunk_size based on document types

---

## Security Considerations

- ✅ Store secrets in Azure Key Vault (not in code)
- ✅ Use managed identities for Azure services
- ✅ Enable HTTPS for all API endpoints
- ✅ Implement API authentication
- ✅ Audit all POC generation and testing

---

**Last Updated**: February 2026  
**Version**: 1.0.0

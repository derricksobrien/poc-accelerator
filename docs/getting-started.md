# Getting Started: POC Accelerator

## 5-Minute Quick Start

### Prerequisites
- Python 3.8+
- pip or conda
- Git
- (Optional) Docker Desktop for container deployment

### Installation

1. **Clone the Repository**
```bash
git clone https://github.com/derricksobrien/poc-accelerator.git
cd poc-accelerator
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Set Environment Variables**
```bash
# Linux/Mac
export OPENAI_API_KEY="your-key-here"

# Windows PowerShell
$env:OPENAI_API_KEY="your-key-here"
```

4. **Run the Application**
```bash
# Web API
python app.py
# Visit http://localhost:5000

# OR: Interactive Dashboard
streamlit run streamlit_app.py
# Visit http://localhost:8501
```

---

## What You Get

### 🤖 AI-Powered POC Generator
- Instant POC scenarios from natural language
- 50+ solution accelerators
- Semantic search across all data
- Real-time Azure service validation

### 📊 Interactive Dashboard
- Streamlit-based web interface
- Real-time statistics
- Search across all solutions
- One-click deployment options

### 🔌 REST API
- 11 built-in endpoints
- Swagger documentation
- Health checks
- Azure service validation

### 🐳 Container Ready
- Dockerfile for production deployment
- Docker Compose for local testing
- Azure Container Apps support
- Kubernetes compatible

---

## Common Tasks

### Search for a Solution
```python
from techconnect.vector_store import VectorStore

store = VectorStore("catalog.json")
results = store.search("AI automation", area="AI", complexity="L300")
for result in results:
    print(f"- {result['name']}: {result['description']}")
```

### Generate a POC Automatically
```python
from techconnect.rag_system import RAGSystem

rag = RAGSystem()
poc = rag.generate_poc(
    title="Build an AI Chatbot",
    azure_config={"openai_key": "sk-..."}
)
print(poc)
```

### Run Tests
```bash
# Run all tests
pytest test/

# Run specific test
pytest test/test_rag_system.py -v

# Check coverage
pytest --cov=techconnect test/
```

---

## File Structure

```
poc-accelerator/
├── TechConnect/
│   ├── app.py              # Flask web server
│   ├── rag_system.py       # Core RAG engine
│   ├── vector_store.py     # Semantic search
│   └── poc_generator.py    # POC generation
├── System2-RAG/
│   ├── app/                # Alternative implementation
│   └── catalog.json        # Data source
├── System3-RAG/
│   ├── streamlit_app.py    # Dashboard UI
│   ├── agent_orchestrator.py
│   └── requirements.txt
└── docs/                   # Documentation
```

---

## Configuration

### Azure OpenAI Setup (Optional)
```python
import os
os.environ['OPENAI_API_KEY'] = 'your-key'
os.environ['OPENAI_API_BASE'] = 'https://your-instance.openai.azure.com/'
os.environ['OPENAI_API_VERSION'] = '2024-02-15-preview'
```

### Local Vector Store
```python
from techconnect.vector_store import VectorStore

# Initialize with custom catalog
store = VectorStore("path/to/catalog.json")

# Search with filters
results = store.search(
    query="machine learning",
    area="AI",
    complexity="L300"
)
```

---

## Deployment Options

| Option | Ease | Performance | Cost |
|--------|------|-------------|------|
| Local Flask | ⭐⭐⭐⭐⭐ | Medium | Free |
| Docker Local | ⭐⭐⭐⭐ | High | Free |
| Azure Container Apps | ⭐⭐⭐ | Very High | $$ |
| App Service | ⭐⭐⭐⭐ | High | $$ |

See **Deployment Guide** for detailed instructions.

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'techconnect'"
```bash
pip install -r requirements.txt
# or
python -m pip install --upgrade pip
pip install -e .
```

### "Connection timeout" on Azure calls
- Check API key: `echo $OPENAI_API_KEY`
- Verify network: `curl https://api.openai.com`
- Check service status: Visit health endpoint `/api/health`

### Port already in use
```bash
# Change port (Flask)
python app.py --port 8080

# Change port (Streamlit)
streamlit run streamlit_app.py --server.port 8501
```

See **Troubleshooting Guide** for more help.

---

## Next Steps

1. **Explore the API**
   - Visit http://localhost:5000/docs for Swagger
   - Try /api/list-scenarios endpoint
   - Test search functionality

2. **Deploy Locally**
   - Run with Docker: `docker build -t poc-accelerator . && docker run -p 5000:5000 poc-accelerator`
   - Or use Docker Compose: `docker-compose up`

3. **Use the Dashboard**
   - Run Streamlit: `streamlit run System3-RAG/streamlit_app.py`
   - Search solutions interactively
   - View real-time statistics

4. **Deploy to Azure**
   - See Deployment Guide for step-by-step Azure Container Apps setup
   - Use GitHub Actions for CI/CD
   - Monitor with Azure Application Insights

---

**Need Help?** Check [Troubleshooting Guide](TROUBLESHOOTING.md) or see [API Reference](API-REFERENCE.md).

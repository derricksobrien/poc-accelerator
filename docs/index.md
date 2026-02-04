# POC Accelerator RAG System

**Complete Retrieval-Augmented Generation System for Proof-of-Concept Generation**

---

## 🚀 Quick Start {#quick-start}

Get up and running in 5 minutes:

```bash
cd TechConnect
./quickstart.bat              # Windows
bash quickstart.sh            # Linux/macOS
python app.py
```

Then visit: **http://localhost:5000**

---

## 📚 Table of Contents

- [Quick Start](#quick-start)
- [Key Features](#key-features)
- [Installation](#installation)
- [Getting Started](#getting-started)
- [Deployment](#deployment)
- [API Reference](#api-reference)
- [Architecture](#architecture)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)

---

## ✨ Key Features {#key-features}

✅ **Multi-Source Data Ingestion**
- GitHub repositories
- Web pages
- Local documentation
- 10 pre-configured sources

✅ **Intelligent POC Generation**
- 4 solution area templates
- Architecture diagrams
- Prerequisites and guides
- Cost/time estimates

✅ **Automated Testing**
- Azure validation
- Service availability checks
- Deployment simulation

✅ **Web Interface & API**
- Beautiful, responsive UI
- 11 REST endpoints
- Real-time progress tracking

✅ **Production Ready**
- Docker containerization
- Multiple deployment options
- Security best practices
- Comprehensive testing

---

## 🎯 Use Cases

### 1. Generate POC Instructions
Create complete proof-of-concept guides in seconds

### 2. Test in Azure
Validate prerequisites and resources automatically

### 3. Save to GitHub
Enable team collaboration with version control

### 4. Share with Stakeholders
Download as markdown or share via API

### 5. Build Knowledge Base
Leverage multi-source documentation

---

## 📊 System Overview

```
Data Sources          RAG System            POC Generation
(GitHub, Web)    →    (Search & Context)  →  (Templates)
                                          ↓
                                    Azure Testing
                                          ↓
                                    GitHub Storage
```

---

## 🔧 Technology Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Python 3.10+, Flask, Pydantic |
| **Frontend** | HTML5, CSS3, JavaScript (Axios) |
| **Cloud** | Azure OpenAI, Container Apps, App Service |
| **Data** | Semantic Search, Document Chunking |
| **Testing** | pytest, comprehensive test suite |
| **Deployment** | Docker, GitHub Pages, Azure CLI |

---

## 📖 Installation {#installation}

### Prerequisites
- Python 3.10+
- Git
- Optional: Docker, Azure CLI

### Local Installation

```bash
# Clone repository
git clone https://github.com/derricksobrien/poc-accelerator.git
cd poc-accelerator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py
```

### Docker Installation

```bash
docker build -t poc-accelerator .
docker run -p 5000:5000 poc-accelerator
```

---

## 📚 Getting Started {#getting-started}

### Your First POC (2 minutes)

1. **Start the application**
   ```bash
   python app.py
   ```

2. **Open browser**
   Navigate to: http://localhost:5000

3. **Generate a POC**
   - Enter a scenario title (e.g., "AI Automation for Sales")
   - Select solution area
   - Select complexity level
   - Click "Generate"

4. **Review Results**
   - View generated POC
   - Check architecture diagram
   - Review prerequisites
   - Download or save to GitHub

### Key Capabilities

✅ **Multi-Source Data Ingestion**
- GitHub repositories
- Web pages
- Local documentation
- 10 pre-configured sources

✅ **Intelligent POC Generation**
- 4 solution area templates
- Architecture diagrams
- Prerequisites and guides
- Cost/time estimates

✅ **Automated Testing**
- Azure validation
- Service availability checks
- Deployment simulation

---

## 🚀 Deployment {#deployment}

### Option 1: Local Development
```bash
python app.py
# Runs on http://localhost:5000
```

### Option 2: Docker
```bash
docker build -t poc-accelerator .
docker run -p 5000:5000 poc-accelerator
```

### Option 3: Azure Container Apps
```bash
az containerapp create \
  --name poc-accelerator \
  --image derricksobrien/poc-accelerator:latest \
  --environment myenv \
  --target-port 5000
```

### Option 4: GitHub Pages (Documentation)
Already deployed at:
```
https://derricksobrien.github.io/poc-accelerator/
```

---

## 📡 API Reference {#api-reference}

### Endpoints

#### Generate POC
```
POST /api/generate
Content-Type: application/json

{
  "scenario": "AI Automation for Sales",
  "area": "AI",
  "complexity": "L300"
}

Response: { "poc_id": "...", "instructions": "..." }
```

#### List POCs
```
GET /api/pocs
Response: [ { "id": "...", "title": "..." }, ... ]
```

#### Get POC Details
```
GET /api/pocs/{id}
Response: { full POC object }
```

#### Save to GitHub
```
POST /api/save-github
Content-Type: application/json

{
  "poc_id": "...",
  "github_token": "...",
  "repo": "my-pocs"
}

Response: { "status": "success", "url": "..." }
```

#### Search Data Sources
```
GET /api/search?q=query&area=AI&complexity=L300
Response: [ { "source": "...", "content": "..." }, ... ]
```

### Response Codes
- **200**: Success
- **400**: Bad request
- **401**: Unauthorized
- **404**: Not found
- **500**: Server error

---

## 🏗️ Architecture {#architecture}

```
┌─────────────────────────────────────┐
│       Web Interface (Frontend)       │
│    HTML5, CSS3, JavaScript (Axios)  │
└──────────────────┬──────────────────┘
                   │
┌──────────────────▼──────────────────┐
│        Flask REST API Server        │
│  (Routes, Request Handling, Auth)   │
└──────────────────┬──────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
   ┌────▼─────┐        ┌──────▼──────┐
   │    RAG    │        │  Generator  │
   │   Search  │        │  Templates  │
   └────┬─────┘        └──────┬──────┘
        │                     │
   ┌────▼──────────────────────▼────┐
   │   Data Sources & Azure OpenAI  │
   │ (GitHub, Web, Local, LLM APIs) │
   └────────────────────────────────┘
```

### Modules

- **ingestion/scraper.py** - Data ingestion from sources
- **models/schemas.py** - Data validation (Pydantic)
- **vector_store/store.py** - Semantic search
- **api/main.py** - REST API endpoints
- **poc_generator.py** - Template-based generation
- **azure_integration.py** - Azure services
- **github_integration.py** - GitHub operations

---

## 🆘 Troubleshooting {#troubleshooting}

### Issue: "Port 5000 already in use"
```bash
# Use different port
flask run --port 5001
```

### Issue: "ModuleNotFoundError"
```bash
# Install missing dependencies
pip install -r requirements.txt
```

### Issue: "Azure authentication failed"
```bash
# Set environment variables
export OPENAI_API_KEY="your-key"
export AZURE_KEYVAULT_URL="your-url"
```

### Issue: "GitHub token invalid"
- Generate new token: https://github.com/settings/tokens
- Token needs: repo, workflow scopes
- Set: `GITHUB_TOKEN` environment variable

### Issue: "POC generation is slow"
- Check internet connection
- Verify Azure API quotas
- Consider caching results
- Check system resources

---

## ❓ FAQ {#faq}

### Q: Can I use this without Azure?
**A**: Yes! Local mode works without Azure. Just skip Azure-dependent features.

### Q: How do I add custom data sources?
**A**: Edit `data_sources.config.json` and implement a data provider class.

### Q: Can I deploy to production?
**A**: Yes! Use Docker or Azure Container Apps. See Deployment section.

### Q: How do I customize POC templates?
**A**: Edit templates in `poc_generator.py` or create new solution areas.

### Q: Is there a CLI tool?
**A**: Yes! Run `python cli.py --help` for CLI commands.

### Q: Can I integrate with my team's tools?
**A**: Yes! REST API supports integration with any tool. See API Reference.

### Q: How do I update documentation?
**A**: Edit `.md` files in `docs/` and push to GitHub. GitHub Pages auto-rebuilds.

---

---

## 📈 What's Included

| Category | Count | Lines |
|----------|-------|-------|
| **Python Modules** | 14 | 8,000+ |
| **Web Assets** | 3 | 1,300+ |
| **Test Modules** | 9 | 600+ |
| **Documentation** | 6 | 1,500+ |
| **Configuration** | 2+ | 500+ |

---

## 🚀 Get Started Now

### Option 1: Local Development
```bash
python app.py
```

### Option 2: Docker
```bash
docker build -t poc-accelerator .
docker run -p 5000:5000 poc-accelerator
```

### Option 3: Azure
See [Deployment Guide](./deployment.md)

---

## 📖 Documentation Structure

```
📚 Documentation
├── Getting Started
│   ├── 5-minute quick start
│   ├── Key capabilities
│   └── Usage examples
├── Setup & Configuration
│   ├── Installation steps
│   ├── Environment setup
│   └── Data source configuration
├── Deployment
│   ├── Local testing
│   ├── Docker deployment
│   ├── Azure Container Apps
│   └── Azure App Service
├── Technical Reference
│   ├── Architecture
│   ├── API endpoints
│   ├── Module breakdown
│   └── Configuration options
└── Project Information
    ├── Full specification
    ├── Delivery summary
    └── Executive overview
```

---

## 💡 Key Concepts

### RAG (Retrieval-Augmented Generation)
Combine retrieval and generation to create context-aware outputs.

### Solution Areas
4 categorized domains for POC generation:
- AI Business Solutions
- Cloud & AI Platforms
- Microsoft Unified
- Security

### POC Instructions
Complete deployment guides with architecture, prerequisites, and steps.

### Data Sources
Configurable content providers (GitHub, web, local files).

---

## 🆘 Need Help?

- **Getting Started**: Read [Getting Started Guide](./getting-started.md)
- **Setup Issues**: Check [Troubleshooting](./troubleshooting.md)
- **Deployment**: See [Deployment Guide](./deployment.md)
- **API Questions**: Review [API Reference](./api-reference.md)
- **Architecture**: Study [Architecture Documentation](./architecture.md)

---

## 🎯 Next Steps

1. **Understand**: Read [Getting Started Guide](./getting-started.md)
2. **Setup**: Follow [Setup Guide](./setup-guide.md)
3. **Deploy**: See [Deployment Guide](./deployment.md)
4. **Extend**: Customize with your own data sources

---

## 📊 Quick Stats

- **8,000+** lines of production code
- **1,500+** lines of documentation
- **9** test modules
- **11** API endpoints
- **4** solution area templates
- **10** pre-configured data sources

---

## 🔐 Security

✅ No hardcoded credentials  
✅ Environment variable configuration  
✅ GitHub token security  
✅ Input validation  
✅ Best practices documented  

---

## 📈 Performance

| Operation | Time |
|-----------|------|
| POC Generation | 3-5 seconds |
| Search Query | <500ms |
| Page Load | 1-2 seconds |
| API Response | <1 second |

---

## 🤝 Contributing

This is a complete, production-ready system. To extend:

1. Add new data sources in `data_sources.config.json`
2. Create custom templates in `poc_generator.py`
3. Integrate custom services via API
4. Submit improvements to documentation

---

## 📝 License

[Your License Here]

---

## 📞 Support

- **Documentation**: See guides above
- **Issues**: Check [Troubleshooting](./troubleshooting.md)
- **Questions**: Review relevant documentation section

---

**Status**: ✅ **Production Ready**  
**Version**: 1.0.0  
**Last Updated**: February 2026

---

## Quick Navigation

- [Back to Top](#top)
- [Quick Start](#quick-start)
- [Features](#key-features)
- [Installation](#installation)
- [Getting Started](#getting-started)
- [Deployment](#deployment)
- [API Reference](#api-reference)
- [Architecture](#architecture)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)

---

[View on GitHub](https://github.com/derricksobrien/poc-accelerator) | [Report Issues](https://github.com/derricksobrien/poc-accelerator/issues)

# Getting Started with POC Accelerator

**Complete 5-minute quick start guide**

---

## Prerequisites

- Python 3.10+ ([Download](https://www.python.org/downloads/))
- Git ([Download](https://git-scm.com/downloads))
- Optional: Azure subscription (for Azure features)
- Optional: GitHub account (for saving POCs)

---

## Installation (5 Minutes)

### Step 1: Clone Repository
```bash
git clone https://github.com/your-username/poc-accelerator.git
cd poc-accelerator/TechConnect
```

### Step 2: Run Setup Script

**Windows:**
```bash
./quickstart.bat
```

**Linux/macOS:**
```bash
bash quickstart.sh
```

### Step 3: Start Application
```bash
python app.py
```

### Step 4: Open Browser
Visit: **http://localhost:5000**

---

## What You'll See

### Dashboard
- System statistics
- Available solution areas
- Recent POC history

### Generator Form
- **Solution Area**: Select from 4 areas
- **POC Title**: Enter your POC name
- **GitHub Save**: Optional checkbox

### Results
- Generated POC instructions
- Architecture overview
- Prerequisites list
- Deployment steps
- Test results (if tested)

---

## Your First POC (2 Minutes)

### 1. Select Solution Area
Click dropdown and choose one:
- **AI Business Solutions** - Chatbots, document processing
- **Cloud & AI Platforms** - Containers, serverless
- **Microsoft Unified** - Teams, collaboration
- **Security** - Identity, compliance

### 2. Enter POC Title
Example:
- "Customer Service Chatbot"
- "Multi-Agent AI System"
- "Microservices on Kubernetes"

### 3. Click Generate
Watch the progress indicator:
- ⏳ Generating...
- ✓ Generated
- ✓ Testing (optional)
- ✓ Saving (optional)

### 4. Review Results
See:
- Architecture diagram
- Prerequisites
- Step-by-step guide
- Azure services
- Time estimates

---

## Key Capabilities

### Generate POCs
Create complete POC instructions in seconds

### Test in Azure
Validate prerequisites and resources (optional)

### Save to GitHub
Enable version control and collaboration (optional)

### Download
Export as markdown for sharing

### Add Data Sources
Customize with your own documentation

---

## API Examples

### Generate POC via API
```bash
curl -X POST http://localhost:5000/api/generate-poc \
  -H "Content-Type: application/json" \
  -d '{
    "poc_title": "AI Chatbot",
    "solution_area": "ai-business",
    "save_to_github": false
  }'
```

### Get Solution Areas
```bash
curl http://localhost:5000/api/solution-areas
```

### Get System Stats
```bash
curl http://localhost:5000/api/system-stats
```

---

## Configuration

### Environment Variables (Optional)
Create `.env` file:
```
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=sk-...
FLASK_DEBUG=False
PORT=5000
```

### Data Sources
Edit `data_sources.config.json` to:
- Add GitHub repositories
- Configure websites
- Add local documentation
- Set refresh intervals

---

## Troubleshooting

### Port Already in Use
```bash
PORT=8000 python app.py
```

### Module Import Error
```bash
pip install -r requirements-rag.txt
```

### Azure Credential Error
```bash
az login
```

### GitHub Push Failed
Check `GITHUB_TOKEN` in `.env`

---

## Next Steps

1. **Setup**: Run installation steps above
2. **Try**: Generate your first POC
3. **Explore**: Check data sources and configuration
4. **Deploy**: See [Deployment Guide](./deployment.md)
5. **Extend**: Add custom data sources

---

## Documentation Map

- **[Setup Guide](./setup-guide.md)** - Detailed configuration
- **[Deployment Guide](./deployment.md)** - Production deployment
- **[API Reference](./api-reference.md)** - REST endpoints
- **[Architecture](./architecture.md)** - System design
- **[Troubleshooting](./troubleshooting.md)** - Common issues

---

**Ready?** Start with step 1 above! 🚀

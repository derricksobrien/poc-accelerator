# Quick Deploy Reference Card

**Save this for future reference!**

---

## 🚀 One-Command Deployment

```bash
cd c:\Users\derri\Code\techconnect_all\System3-RAG

python deploy_app_service.py \
  --resource-group <YOUR-RESOURCE-GROUP> \
  --name system3-rag \
  --region eastus
```

**Replace `<YOUR-RESOURCE-GROUP>` with your Azure resource group name**

**Example:**
```bash
python deploy_app_service.py \
  --resource-group contoso-ai-rg \
  --name system3-rag \
  --region eastus
```

---

## ⏱️ How Long?

- **If new resources**: 10-15 minutes
- **If resources exist**: 3-5 minutes

---

## 📌 Key Information

| Item | Value |
|------|-------|
| **Service Type** | Azure App Service |
| **Runtime** | Python 3.10 |
| **Cost** | $13-$50/month |
| **No containers needed** | ✅ |
| **Auto-scaling** | Optional (S1+) |
| **Deployment time** | 10-15 min |

---

## ✅ Prerequisites

```bash
# Check these before running deployment
az --version                    # Must be installed
az login                        # Must be authenticated
cd System3-RAG                  # Must be here
ls requirements.txt             # Must exist
```

---

## 🌐 After Deployment

Your app will be at:
```
https://system3-rag.azurewebsites.net
```

---

## 🔥 Common Commands

```bash
# Check if app is responding
curl https://system3-rag.azurewebsites.net/health

# View logs (last 100 lines)
az webapp log tail -n system3-rag -g <YOUR-RG>

# Restart app
az webapp restart -n system3-rag -g <YOUR-RG>

# See real-time logs
az webapp log tail -n system3-rag -g <YOUR-RG> --follow
```

---

## 🔧 If App Won't Start

```bash
# Check logs
az webapp log tail -n system3-rag -g <YOUR-RG> --follow

# Wait 2-3 minutes (cold start)
# If still not working, restart:
az webapp restart -n system3-rag -g <YOUR-RG>
```

---

## 📈 If You Need More Power

```bash
# Current: B1 ($13/mo) - Good for testing
# Upgrade to: B2 ($26/mo) or B3 ($52/mo) or S1 ($50/mo with auto-scaling)

az appservice plan update \
  -n system3-rag-plan \
  -g <YOUR-RG> \
  --sku B2
```

---

## 🗑️ If You Want to Delete Everything

```bash
# This removes EVERYTHING (careful!)
az group delete -n <YOUR-RG> --yes --no-wait

# Cost drops to $0 immediately
```

---

## 🚨 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Not authenticated" | Run: `az login` |
| "Resource group not found" | Check spelling: `az group list` |
| "App won't start" | Check logs: `az webapp log tail ...` |
| "Slow response" | Upgrade plan: `az appservice plan update ... --sku B2` |
| "500 error" | Restart: `az webapp restart ...` |

---

## 📊 Monitor Your App

```bash
# Get app status
az webapp show -n system3-rag -g <YOUR-RG> --query state

# View current settings
az webapp config appsettings list -n system3-rag -g <YOUR-RG>

# Check quotas/limits
az appservice plan show -n system3-rag-plan -g <YOUR-RG>
```

---

## 🔐 Add Azure AI Credentials (Optional)

```bash
# If you have Azure OpenAI credentials
az webapp config appsettings set \
  -n system3-rag \
  -g <YOUR-RG> \
  --settings \
    AZURE_OPENAI_ENDPOINT="https://your-openai.openai.azure.com/" \
    AZURE_OPENAI_KEY="sk-your-key-here" \
    AZURE_OPENAI_DEPLOYMENT="gpt-4"
```

Then restart: `az webapp restart -n system3-rag -g <YOUR-RG>`

---

## 📚 Full Guide

See **DEPLOY_STAGES.md** for detailed step-by-step instructions

---

**Quick Deploy Reference**  
*February 2026*  
*Save this file!*

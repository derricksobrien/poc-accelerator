# Azure Deployment Guide for TechConnect Contextual Broker Agent

## Overview
This guide provides step-by-step instructions for deploying the TechConnect Contextual Broker Agent to Azure Container Apps with public HTTPS access and API key authentication.

## Deployment Architecture
- **Compute**: Azure Container Apps (serverless, auto-scaling)
- **Registry**: Azure Container Registry (image storage)
- **Authentication**: API Key via HTTP headers
- **CI/CD**: GitHub Actions (automatic deployment on push)
- **Estimated Cost**: ~$45/month (consumption-based pricing)

---

## Prerequisites

### Required
- Azure Subscription with Owner or Contributor access
- Azure CLI (`az --version`)
- Docker installed locally (optional—Azure can build from source)
- Git and GitHub repository access
- TechConnect code repository cloned locally

### Verify Azure Access
```bash
az login
az account show --query id
```

---

## Step 1: Prepare Azure Resources

### 1.1 Create Resource Group
Choose a region close to your users (e.g., `eastus`, `westus2`, `northeurope`).

```bash
export RESOURCE_GROUP="techconnect-rg"
export LOCATION="eastus"

az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION
```

### 1.2 Create Azure Container Registry (ACR)
This stores your Docker images.

```bash
export REGISTRY_NAME="techconnectregistry"

az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $REGISTRY_NAME \
  --sku Basic
```

**Note**: Replace `techconnectregistry` with a globally unique name (lowercase, no hyphens).

### 1.3 Create Container Apps Environment
This hosts your containerized application.

```bash
export ENVIRONMENT_NAME="techconnect-env"

az containerapp env create \
  --name $ENVIRONMENT_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION
```

---

## Step 2: Configure Application Settings

### 2.1 Create `.env.production` File
Store secure credentials in Azure Key Vault (recommended) or as App Settings.

```bash
# .env.production
OPENAI_API_KEY=your-azure-openai-key
VECTOR_STORE_PATH=/mnt/storage
API_KEY=your-secure-api-key-min-32-chars
ENVIRONMENT=production
```

**Security Best Practice**: Use Azure Key Vault instead of `.env` for production.

### 2.2 Create Azure Key Vault (Optional but Recommended)
```bash
export VAULT_NAME="techconnect-kv"

az keyvault create \
  --resource-group $RESOURCE_GROUP \
  --name $VAULT_NAME \
  --location $LOCATION

# Add secrets
az keyvault secret set \
  --vault-name $VAULT_NAME \
  --name "openai-api-key" \
  --value "your-azure-openai-key"

az keyvault secret set \
  --vault-name $VAULT_NAME \
  --name "api-key" \
  --value "your-secure-api-key-min-32-chars"
```

---

## Step 3: Create Docker Image

### 3.1 Create Dockerfile
Ensure this file exists in your TechConnect root directory:

```dockerfile
# filepath: c:\Users\derri\Code\TechConnect\Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port for FastAPI
EXPOSE 8000

# Start uvicorn server
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 3.2 Create .dockerignore
Optimize image size:

```
# filepath: c:\Users\derri\Code\TechConnect\.dockerignore
__pycache__
.git
.gitignore
.env
.env.local
.env.*.local
*.pyc
*.pyo
*.pyd
.Python
venv/
.venv/
env/
node_modules/
.vscode/
.idea/
*.log
.pytest_cache/
.chroma/
.DS_Store
```

### 3.3 Build and Push Image to ACR

```bash
# Login to ACR
az acr login --name $REGISTRY_NAME

# Build image locally
docker build -t techconnect-api:latest .

# Tag for ACR
docker tag techconnect-api:latest \
  ${REGISTRY_NAME}.azurecr.io/techconnect-api:latest

# Push to ACR
docker push ${REGISTRY_NAME}.azurecr.io/techconnect-api:latest

# Verify push
az acr repository list --name $REGISTRY_NAME
```

---

## Step 4: Deploy to Azure Container Apps

### 4.1 Deploy Container App with API Key

```bash
export CONTAINER_APP_NAME="techconnect-api"
export API_KEY="your-secure-32-character-api-key"
export OPENAI_KEY="your-azure-openai-key"

az containerapp create \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment $ENVIRONMENT_NAME \
  --image ${REGISTRY_NAME}.azurecr.io/techconnect-api:latest \
  --target-port 8000 \
  --ingress external \
  --registry-server ${REGISTRY_NAME}.azurecr.io \
  --registry-username ${REGISTRY_NAME} \
  --registry-password $(az acr credential show -n $REGISTRY_NAME --query "passwords[0].value" -o tsv) \
  --env-vars \
    API_KEY=$API_KEY \
    OPENAI_API_KEY=$OPENAI_KEY \
    ENVIRONMENT=production \
  --cpu 0.5 \
  --memory 1Gi \
  --min-replicas 1 \
  --max-replicas 10
```

### 4.2 Get Public URL

```bash
export CONTAINER_APP_URL=$(az containerapp show \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn \
  -o tsv)

echo "API URL: https://${CONTAINER_APP_URL}"
```

**Example Output**:
```
API URL: https://techconnect-api.happyplant-abc123.eastus.azurecontainerapps.io
```

---

## Step 5: Configure CI/CD with GitHub Actions

### 5.1 Create GitHub Actions Workflow
Create this file in your repository:

```yaml
# filepath: c:\Users\derri\Code\TechConnect\.github\workflows\deploy-azure.yml
name: Deploy TechConnect to Azure Container Apps

on:
  push:
    branches:
      - main
  workflow_dispatch:

env:
  REGISTRY: ${{ secrets.REGISTRY_NAME }}.azurecr.io
  IMAGE_NAME: techconnect-api
  CONTAINER_APP_NAME: techconnect-api
  RESOURCE_GROUP: techconnect-rg

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Login to Azure
      uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}
    
    - name: Login to ACR
      run: |
        az acr login --name ${{ secrets.REGISTRY_NAME }}
    
    - name: Build Docker image
      run: |
        docker build -t ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} .
        docker tag ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest
    
    - name: Push to ACR
      run: |
        docker push ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
        docker push ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest
    
    - name: Deploy to Container Apps
      run: |
        az containerapp update \
          --name ${{ env.CONTAINER_APP_NAME }} \
          --resource-group ${{ env.RESOURCE_GROUP }} \
          --image ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
```

### 5.2 Create Azure Service Principal for GitHub
Required for GitHub Actions to access Azure:

```bash
# Create service principal
az ad sp create-for-rbac \
  --name "github-techconnect-deploy" \
  --role Contributor \
  --scopes /subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP \
  --json-auth > azure-credentials.json

# Copy output and add to GitHub Secrets
cat azure-credentials.json
```

### 5.3 Add GitHub Secrets
1. Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions**
2. Add these secrets:
   - **AZURE_CREDENTIALS**: Paste output from `azure-credentials.json`
   - **REGISTRY_NAME**: Your ACR name (e.g., `techconnectregistry`)
   - **API_KEY**: Your secure API key

---

## Step 6: Test the Deployment

### 6.1 Test API Endpoint
```bash
# Replace with your actual URL and API key
export API_URL="https://techconnect-api.happyplant-abc123.eastus.azurecontainerapps.io"
export API_KEY="your-secure-api-key"

# Test context endpoint
curl -X POST ${API_URL}/context \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${API_KEY}" \
  -d '{
    "scenario_title": "Deploy a multi-agent automation engine",
    "solution_area": "AI",
    "num_results": 2
  }'
```

**Expected Response**: JSON ContextBlock with architecture and prerequisites in XML tags

### 6.2 Test with Missing API Key (Should Fail)
```bash
curl -X POST ${API_URL}/context \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_title": "Test",
    "solution_area": "AI",
    "num_results": 1
  }'
```

**Expected Response**: `{"detail": "Invalid API key"}` (403 Forbidden)

### 6.3 List Accelerators Endpoint
```bash
curl -X GET ${API_URL}/accelerators \
  -H "X-API-Key: ${API_KEY}"
```

### 6.4 Check Container Logs
```bash
az containerapp logs show \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --follow
```

---

## Step 7: Enable Monitoring & Scaling

### 7.1 Enable Application Insights
```bash
export INSIGHTS_NAME="techconnect-insights"

az monitor app-insights component create \
  --app $INSIGHTS_NAME \
  --location $LOCATION \
  --resource-group $RESOURCE_GROUP

# Get instrumentation key
az monitor app-insights component show \
  --app $INSIGHTS_NAME \
  --resource-group $RESOURCE_GROUP \
  --query instrumentationKey
```

### 7.2 Configure Auto-Scaling
```bash
az containerapp update \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --min-replicas 1 \
  --max-replicas 10
```

### 7.3 Set Up Alerts
```bash
az monitor metrics alert create \
  --name "TechConnect-HighCPU" \
  --resource-group $RESOURCE_GROUP \
  --scopes /subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.App/containerApps/$CONTAINER_APP_NAME \
  --condition "avg Percentage CPU > 80" \
  --window-size 5m \
  --evaluation-frequency 1m
```

---

## Step 8: Custom Domain (Optional)

### 8.1 Add Custom Domain
```bash
az containerapp hostname add \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --hostname api.techconnect.dev \
  --certificate-id /subscriptions/.../certificates/your-cert
```

*Requires SSL certificate. Use Azure Key Vault or Let's Encrypt.*

---

## Troubleshooting

### Issue: "Image pull failed"
**Cause**: ACR credentials incorrect or image doesn't exist
**Solution**:
```bash
# Verify image exists in ACR
az acr repository list --name $REGISTRY_NAME

# Verify ACR credentials
az acr credential show --name $REGISTRY_NAME
```

### Issue: "Container fails to start"
**Cause**: Application error, missing environment variables
**Solution**:
```bash
# Check logs
az containerapp logs show \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP

# Verify env vars
az containerapp show \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query properties.template.containers[0].env
```

### Issue: "API Key validation fails"
**Cause**: Key mismatch or case sensitivity
**Solution**:
```bash
# Verify set key matches
az containerapp show \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query properties.template.containers[0].env[0]

# Update if needed
az containerapp update \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --set-env-vars API_KEY="new-key-value"
```

### Issue: Deployment timeout
**Cause**: Resource provisioning delay
**Solution**: Wait 2-3 minutes and check Azure Portal for resource status

---

## Cost Estimation

| Service | Monthly Cost | Notes |
|---------|-------------|-------|
| Azure Container Apps | $36 | 0.5 vCPU, 1 GB memory, 1-10 replicas |
| Container Registry | $5 | Basic SKU with 10 GB storage |
| Application Insights (optional) | $0-10 | Pay-as-you-go ingestion |
| **Total** | **~$41-51** | Consumption-based pricing |

---

## Cleanup (Delete Resources)

To stop incurring charges:

```bash
# Delete entire resource group (deletes all resources)
az group delete \
  --name $RESOURCE_GROUP \
  --yes --no-wait

# Or delete individual resources
az containerapp delete --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP
az acr delete --name $REGISTRY_NAME --resource-group $RESOURCE_GROUP
az containerapp env delete --name $ENVIRONMENT_NAME --resource-group $RESOURCE_GROUP
```

---

## Security Best Practices

1. **API Key Management**
   - Use Azure Key Vault for secrets, not hardcoded values
   - Rotate keys every 90 days
   - Never commit `.env` files to Git

2. **Network Security**
   - Enable VNet integration for private deployments
   - Use private endpoints for Azure services
   - Configure firewall rules on ACR

3. **Identity & Access**
   - Use Managed Identities (not service principals) when possible
   - Implement role-based access control (RBAC)
   - Audit logs in Azure Monitor

4. **Container Security**
   - Scan images for vulnerabilities: `az acr scan --registry $REGISTRY_NAME`
   - Use minimal base images (Alpine, distroless)
   - Run containers as non-root user

5. **RAI Compliance**
   - All AI-based endpoints log requests for audit trails
   - Implement request rate limiting
   - Document model limitations and capabilities
   - Inject RAI disclaimers for solution_area="AI" with responsible_ai_tag=true

---

## Next Steps

1. ✅ Deploy to Azure Container Apps
2. ✅ Set up GitHub Actions CI/CD
3. ✅ Configure monitoring and alerting
4. ✅ Map custom domain (optional)
5. ✅ Implement rate limiting middleware
6. ✅ Add request authentication/audit logging
7. ✅ Scale based on usage patterns

---

## Support & Resources

- **Azure Documentation**: https://learn.microsoft.com/azure/container-apps/
- **GitHub Actions**: https://docs.github.com/actions
- **FastAPI Deployment**: https://fastapi.tiangolo.com/deployment/
- **Azure CLI Reference**: https://learn.microsoft.com/cli/azure/reference-index
- **TechConnect Repository**: Your repo URL

---

*Last Updated: January 20, 2026 | Owner: TechConnect Development Team | Status: Complete*
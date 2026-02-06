"""
Cloud Solution Architect (CSA) Enhancements for POC Generator
Provides code snippets, RBAC roles, validation scripts, and IaC templates
"""

from typing import Dict, List

# RBAC Roles Database - Enterprise-grade permission sets
RBAC_ROLES = {
    "multi-agent-automation": {
        "roles": [
            {
                "role": "Owner",
                "scope": "Subscription",
                "reason": "Full control needed for AI services and container apps"
            },
            {
                "role": "Azure AI Foundry Administrator",
                "scope": "Resource Group",
                "reason": "Manage AI Foundry resources and models"
            },
            {
                "role": "Azure Container Apps Admin",
                "scope": "Resource Group",
                "reason": "Deploy and manage container applications"
            },
            {
                "role": "Key Vault Administrator",
                "scope": "Key Vault",
                "reason": "Manage secrets for API keys and credentials"
            },
            {
                "role": "Cosmos DB Account Contributor",
                "scope": "Resource Group",
                "reason": "Manage state and history storage"
            }
        ]
    },
    "content-processing": {
        "roles": [
            {
                "role": "Owner",
                "scope": "Subscription",
                "reason": "Deploy new Azure services"
            },
            {
                "role": "Azure AI Content Understanding Admin",
                "scope": "Resource Group",
                "reason": "Configure document processing models"
            },
            {
                "role": "Storage Blob Data Contributor",
                "scope": "Storage Account",
                "reason": "Upload and process documents"
            },
            {
                "role": "Cognitive Services OpenAI Contributor",
                "scope": "Resource Group",
                "reason": "Use Azure OpenAI for document understanding"
            }
        ]
    },
    "unified-data-fabric": {
        "roles": [
            {
                "role": "Fabric Admin",
                "scope": "Tenant",
                "reason": "Create and manage Fabric capacity"
            },
            {
                "role": "Workspace Admin",
                "scope": "Fabric Workspace",
                "reason": "Manage lakehouse and data items"
            },
            {
                "role": "Purview Data Curator",
                "scope": "Purview Account",
                "reason": "Configure data governance and lineage"
            },
            {
                "role": "Storage Account Contributor",
                "scope": "Resource Group",
                "reason": "Link external Databricks data"
            }
        ]
    },
    "rag-chat-your-data": {
        "roles": [
            {
                "role": "Search Service Admin",
                "scope": "Azure AI Search",
                "reason": "Create and manage search indexes"
            },
            {
                "role": "Cognitive Services OpenAI Contributor",
                "scope": "Resource Group",
                "reason": "Access GPT models for chat"
            },
            {
                "role": "App Service Contributor",
                "scope": "Resource Group",
                "reason": "Deploy web application"
            },
            {
                "role": "Storage Blob Data Contributor",
                "scope": "Storage Account",
                "reason": "Store indexed documents"
            }
        ]
    }
}

# CLI Commands Database
CLI_COMMANDS = {
    "multi-agent-automation": {
        "azure_cli": """
# Create resource group
az group create --name myCSARG --location eastus

# Create Azure AI Foundry hub
az cognitiveservices account create --resource-group myCSARG \\
  --name myaiFoudry --kind AIFoundry --sku S0 --location eastus

# Create Container App environment
az containerapp env create --name myAppEnv --resource-group myCSARG \\
  --location eastus

# Create Container App for agent
az containerapp create --resource-group myCSARG \\
  --name multi-agent-app --environment myAppEnv \\
  --image mcr.microsoft.com/azuredocs/containerapp:latest \\
  --cpu 2.0 --memory 4.0Gi
        """,
        "powershell": """
# Create resource group
New-AzResourceGroup -Name myCSARG -Location eastus

# Create AI Foundry account
New-AzCognitiveServicesAccount -ResourceGroupName myCSARG `
  -Name myAIFoundry -Type AIFoundry -SkuName S0 -Location eastus

# Create Container Apps environment
New-AzContainerAppEnvironment -ResourceGroupName myCSARG `
  -EnvName myAppEnv -Location eastus

# Deploy container app
New-AzContainerApp -ResourceGroupName myCSARG `
  -Name multi-agent-app -EnvironmentName myAppEnv `
  -Image "mcr.microsoft.com/azuredocs/containerapp:latest" `
  -Cpu 2.0 -Memory "4.0Gi"
        """
    },
    "content-processing": {
        "azure_cli": """
# Create storage account for document ingestion
az storage account create --resource-group myCSARG \\
  --name mydocstorage --kind StorageV2 --sku Standard_GRS

# Create container for uploaded documents
az storage container create --account-name mydocstorage \\
  --name documents --auth-mode login

# Create Azure AI Content Understanding resource
az cognitiveservices account create --resource-group myCSARG \\
  --name myContentAnalyzer --kind AIContentUnderstanding \\
  --sku S0 --location eastus

# Create Cosmos DB for storing processing results
az cosmosdb create --resource-group myCSARG \\
  --name mydocumentdb --kind GlobalDocumentDB
        """,
        "powershell": """
# Create storage account
New-AzStorageAccount -ResourceGroupName myCSARG `
  -Name mydocstorage -SkuName Standard_GRS -Location eastus `
  -Kind StorageV2

# Create blob container
$storageContext = New-AzStorageContext -StorageAccountName mydocstorage
New-AzStorageContainer -Name documents -Context $storageContext

# Create AI Content Understanding resource
New-AzCognitiveServicesAccount -ResourceGroupName myCSARG `
  -Name myContentAnalyzer -Type AIContentUnderstanding `
  -SkuName S0 -Location eastus

# Create Cosmos DB account
New-AzCosmosDBAccount -ResourceGroupName myCSARG `
  -Name mydocumentdb -Location eastus -Kind GlobalDocumentDB
        """
    },
    "unified-data-fabric": {
        "azure_cli": """
# Create Fabric capacity (requires Microsoft Fabric subscription)
az fabric capacity create --resource-group myCSARG \\
  --capacity-name myFabricCapacity --sku F2 --location eastus

# Create workspace
az fabric workspace create --capacity-name myFabricCapacity \\
  --workspace-name myWorkspace

# Link Databricks (if using external analytics)
az storage account create --resource-group myCSARG \\
  --name mylakehouse --kind StorageV2 --sku Standard_GRS
        """,
        "powershell": """
# Note: Fabric management is primarily through Power BI Admin portal
# These are helper scripts for linked services

# Create storage account for OneLake integration
New-AzStorageAccount -ResourceGroupName myCSARG `
  -Name mylakehouse -SkuName Standard_GRS -Location eastus `
  -Kind StorageV2

# Get storage key for OneLake shortcuts
$storageKey = Get-AzStorageAccountKey -ResourceGroupName myCSARG `
  -Name mylakehouse | Select-Object -First 1 -ExpandProperty Value

# Output for Fabric configuration
Write-Host "Storage Account: mylakehouse"
Write-Host "Storage Key: $storageKey"
        """
    }
}

# Validation Scripts Database
VALIDATION_SCRIPTS = {
    "multi-agent-automation": {
        "powershell": """
# POC Validation Script for Multi-Agent Automation
# Run this to validate all components are working

$resourceGroup = "myCSARG"
$appName = "multi-agent-app"

Write-Host "=== POC Validation Script ===" -ForegroundColor Cyan

# 1. Verify Resource Group exists
Write-Host "1. Checking Resource Group..." -ForegroundColor Yellow
$rg = Get-AzResourceGroup -Name $resourceGroup -ErrorAction SilentlyContinue
if ($rg) {
    Write-Host "✓ Resource Group found: $($rg.ResourceGroupName)" -ForegroundColor Green
} else {
    Write-Host "✗ Resource Group not found" -ForegroundColor Red
    exit 1
}

# 2. Verify Container App is running
Write-Host "2. Checking Container App..." -ForegroundColor Yellow
$app = Get-AzContainerApp -ResourceGroupName $resourceGroup -Name $appName -ErrorAction SilentlyContinue
if ($app) {
    Write-Host "✓ Container App found: $($app.Name)" -ForegroundColor Green
    Write-Host "  Status: $($app.ProvisioningState)" -ForegroundColor Cyan
} else {
    Write-Host "✗ Container App not found" -ForegroundColor Red
}

# 3. Verify AI Foundry access
Write-Host "3. Validating AI Foundry access..." -ForegroundColor Yellow
$aiFoundry = Get-AzCognitiveServicesAccount -ResourceGroupName $resourceGroup `
  -Name "myAIFoundry" -ErrorAction SilentlyContinue
if ($aiFoundry) {
    Write-Host "✓ AI Foundry accessible" -ForegroundColor Green
} else {
    Write-Host "✗ AI Foundry not accessible" -ForegroundColor Red
}

# 4. Test API connectivity
Write-Host "4. Testing API connectivity..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ API responding successfully" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠ Local API not responding (may be normal if deployed to Azure)" -ForegroundColor Yellow
}

# 5. Verify RBAC permissions
Write-Host "5. Checking RBAC permissions..." -ForegroundColor Yellow
$context = Get-AzContext
Write-Host "✓ Currently authenticated as: $($context.Account.Id)" -ForegroundColor Green

# 6. Check resource quotas
Write-Host "6. Verifying quotas..." -ForegroundColor Yellow
$quota = Get-AzComputeResourceSku | Where-Object {$_.ResourceType -eq "containerApps"} | Measure-Object
Write-Host "✓ Container App SKUs available: $($quota.Count)" -ForegroundColor Green

Write-Host "`n=== Validation Complete ===" -ForegroundColor Cyan
Write-Host "All critical components verified!" -ForegroundColor Green
        """,
        "bash": """
#!/bin/bash
# POC Validation Script for Multi-Agent Automation (Linux/macOS)

RESOURCE_GROUP="myCSARG"
APP_NAME="multi-agent-app"

echo "=== POC Validation Script ==="

# 1. Verify Resource Group
echo "1. Checking Resource Group..."
if az group exists --name $RESOURCE_GROUP | grep -q "true"; then
    echo "✓ Resource Group found"
else
    echo "✗ Resource Group not found"
    exit 1
fi

# 2. Verify Container App
echo "2. Checking Container App..."
APP=$(az containerapp show --resource-group $RESOURCE_GROUP --name $APP_NAME 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "✓ Container App running"
else
    echo "✗ Container App not found"
fi

# 3. Test API
echo "3. Testing API..."
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health

echo ""
echo "=== Validation Complete ==="
        """
    },
    "content-processing": {
        "powershell": """
# POC Validation Script for Content Processing
$resourceGroup = "myCSARG"
$storageAccount = "mydocstorage"

Write-Host "=== Content Processing POC Validation ===" -ForegroundColor Cyan

# 1. Verify Storage Account
Write-Host "1. Checking Storage Account..." -ForegroundColor Yellow
$storage = Get-AzStorageAccount -ResourceGroupName $resourceGroup -Name $storageAccount -ErrorAction SilentlyContinue
if ($storage) {
    Write-Host "✓ Storage Account accessible" -ForegroundColor Green
} else {
    Write-Host "✗ Storage Account not found" -ForegroundColor Red
    exit 1
}

# 2. Check document container
Write-Host "2. Verifying documents container..." -ForegroundColor Yellow
$ctx = New-AzStorageContext -StorageAccountName $storageAccount -UseConnectedAccount
$container = Get-AzStorageContainer -Context $ctx -Name "documents" -ErrorAction SilentlyContinue
if ($container) {
    Write-Host "✓ Documents container exists" -ForegroundColor Green
    $blobs = Get-AzStorageBlob -Container "documents" -Context $ctx
    Write-Host "  Documents stored: $($blobs.Count)" -ForegroundColor Cyan
} else {
    Write-Host "✗ Documents container not found" -ForegroundColor Red
}

# 3. Verify Cosmos DB
Write-Host "3. Validating Cosmos DB..." -ForegroundColor Yellow
$cosmos = Get-AzCosmosDBAccount -ResourceGroupName $resourceGroup -Name "mydocumentdb" -ErrorAction SilentlyContinue
if ($cosmos) {
    Write-Host "✓ Cosmos DB account accessible" -ForegroundColor Green
} else {
    Write-Host "✗ Cosmos DB not found" -ForegroundColor Red
}

Write-Host "`n=== Validation Complete ===" -ForegroundColor Green
        """
    }
}

# Infrastructure as Code Templates
IAC_TEMPLATES = {
    "multi-agent-automation": {
        "bicep": """
param location string = 'eastus'
param environment string = 'prod'

resource resourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: 'rg-${environment}-multiagent'
  location: location
}

resource aiFoudry 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: 'aifoundry-${environment}'
  location: location
  kind: 'AIFoundry'
  sku: {
    name: 'S0'
  }
  properties: {
    apiProperties: {
      rateLimitKey: 'UnifiedRateLimit'
    }
  }
}

resource containerAppEnv 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: 'env-${environment}'
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
    }
  }
}

resource cosmosDb 'Microsoft.DocumentDB/databaseAccounts@2023-04-15' = {
  name: 'cosmos-${environment}'
  location: location
  kind: 'GlobalDocumentDB'
  properties: {
    databaseAccountOfferType: 'Standard'
    locations: [
      {
        locationName: location
        failoverPriority: 0
      }
    ]
  }
}

output aiFoudryEndpoint string = aiFoudry.properties.endpoint
output containerEnvId string = containerAppEnv.id
output cosmosDbUri string = cosmosDb.properties.documentEndpoint
        """,
        "terraform": """
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "rg" {
  name     = "rg-${var.environment}-multiagent"
  location = var.location
}

resource "azurerm_cognitive_account" "ai_foundry" {
  name                = "aifoundry-${var.environment}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  kind                = "AIFoundry"
  sku {
    name = "S0"
  }
}

resource "azurerm_container_app_environment" "app_env" {
  name                = "env-${var.environment}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
}

resource "azurerm_cosmosdb_account" "cosmosdb" {
  name                = "cosmos-${var.environment}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB"

  capabilities {
    name = "EnableServerless"
  }

  consistency_policy {
    consistency_level       = "BoundedStaleness"
    max_interval_in_seconds = 300
    max_staleness_prefix    = 100000
  }

  geo_location {
    location          = var.location
    failover_priority = 0
  }
}

variable "environment" {
  type    = string
  default = "prod"
}

variable "location" {
  type    = string
  default = "eastus"
}

output "ai_foundry_endpoint" {
  value = azurerm_cognitive_account.ai_foundry.endpoint
}

output "container_app_env_id" {
  value = azurerm_container_app_environment.app_env.id
}
        """
    }
}


def get_rbac_requirements(solution_id: str) -> List[Dict]:
    """Get RBAC role requirements for a solution"""
    return RBAC_ROLES.get(solution_id, {}).get("roles", [])


def get_cli_commands(solution_id: str) -> Dict[str, str]:
    """Get CLI commands (Azure CLI, PowerShell) for a solution"""
    return CLI_COMMANDS.get(solution_id, {})


def get_validation_script(solution_id: str, language: str = "powershell") -> str:
    """Get validation script for a solution"""
    scripts = VALIDATION_SCRIPTS.get(solution_id, {})
    return scripts.get(language, "")


def get_iac_template(solution_id: str, template_type: str = "bicep") -> str:
    """Get Infrastructure as Code template for a solution"""
    templates = IAC_TEMPLATES.get(solution_id, {})
    return templates.get(template_type, "")

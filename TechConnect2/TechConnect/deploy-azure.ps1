#!/usr/bin/env powershell
<#
.SYNOPSIS
Deploy TechConnect API to Azure App Service

.DESCRIPTION
Deploys the Docker image from ACR to Azure App Service (production)

.EXAMPLE
.\deploy-azure.ps1
#>

$ErrorActionPreference = "Stop"
$azPath = "C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"

# Configuration
$resourceGroup = "techconnect-rg"
$acrName = "techconnectregistry"
$acrUrl = "$acrName.azurecr.io"
$appServicePlan = "techconnect-plan"
$webAppName = "techconnect-api-prod"

Write-Host "=== TechConnect API - Azure App Service Deployment ===" -ForegroundColor Cyan

# Step 1: Create App Service Plan
Write-Host "`nStep 1: Creating App Service Plan..." -ForegroundColor Green
& $azPath appservice plan create --name $appServicePlan --resource-group $resourceGroup --sku B1 --is-linux --output none 2>&1 | Out-Null
Write-Host "App Service Plan created/updated" -ForegroundColor Green

# Step 2: Create Web App
Write-Host "`nStep 2: Creating Web App..." -ForegroundColor Green
& $azPath webapp create --resource-group $resourceGroup --plan $appServicePlan --name $webAppName --deployment-container-image-name "$acrUrl/techconnect-api:latest" --output none 2>&1 | Out-Null
Write-Host "Web App created/updated" -ForegroundColor Green

# Step 3: Get ACR Credentials
Write-Host "`nStep 3: Retrieving ACR credentials..." -ForegroundColor Green
$acrPassword = & $azPath acr credential show --resource-group $resourceGroup --name $acrName --query "passwords[0].value" -o tsv
Write-Host "Credentials retrieved" -ForegroundColor Green

# Step 4: Configure Container Settings
Write-Host "`nStep 4: Configuring container settings..." -ForegroundColor Green
& $azPath webapp config container set --name $webAppName --resource-group $resourceGroup --docker-custom-image-name "$acrUrl/techconnect-api:latest" --docker-registry-server-url "https://$acrUrl" --docker-registry-server-user $acrName --docker-registry-server-password $acrPassword --enable-app-service-storage false --output none 2>&1 | Out-Null
Write-Host "Container settings configured" -ForegroundColor Green

# Step 5: Configure Port Settings
Write-Host "`nStep 5: Configuring port settings..." -ForegroundColor Green
& $azPath webapp config appsettings set --name $webAppName --resource-group $resourceGroup --settings WEBSITES_PORT=8000 PORT=8000 --output none 2>&1 | Out-Null
Write-Host "Port settings configured" -ForegroundColor Green

# Step 6: Get Web App URL
Write-Host "`nStep 6: Retrieving Web App URL..." -ForegroundColor Green
$appUrl = & $azPath webapp show --resource-group $resourceGroup --name $webAppName --query "defaultHostName" -o tsv
Write-Host "Web App URL: https://$appUrl" -ForegroundColor Cyan

# Step 7: Summary
Write-Host "`n=== Deployment Complete ===" -ForegroundColor Green
Write-Host "`nWeb App Details:" -ForegroundColor Cyan
Write-Host "  Name:           $webAppName" -ForegroundColor Gray
Write-Host "  URL:            https://$appUrl" -ForegroundColor Gray
Write-Host "  Resource Group: $resourceGroup" -ForegroundColor Gray

Write-Host "`nTest These Endpoints:" -ForegroundColor Cyan
Write-Host "  Health:   curl https://$appUrl/health" -ForegroundColor Gray
Write-Host "  List:     curl https://$appUrl/accelerators" -ForegroundColor Gray

Write-Host "`nView Logs:" -ForegroundColor Cyan
Write-Host "  az webapp log tail --name $webAppName --resource-group $resourceGroup" -ForegroundColor Gray

Write-Host "`nNote: App startup may take 3-5 minutes. Wait before testing.`n" -ForegroundColor Yellow

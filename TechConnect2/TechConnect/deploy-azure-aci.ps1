#!/usr/bin/env powershell
<#
.SYNOPSIS
Deploy TechConnect API to Azure Container Instances (ACI)

.DESCRIPTION
Alternative deployment to ACI when App Service has quota issues.
Cost: ~$0.20/hour vs App Service at $12.75/month

.EXAMPLE
.\deploy-azure-aci.ps1
#>

$ErrorActionPreference = "Stop"
$azPath = "C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"

# Configuration
$resourceGroup = "techconnect-rg"
$acrName = "techconnectregistry"
$acrUrl = "$acrName.azurecr.io"
$containerName = "techconnect-api-prod"
$containerPort = 8000

Write-Host "`n=== TechConnect API - Azure Container Instances Deployment ===" -ForegroundColor Cyan

# Step 1: Check Container Instance Provider
Write-Host "`nStep 1: Checking Container Instance Provider..." -ForegroundColor Green
$providerStatus = & $azPath provider show --namespace Microsoft.ContainerInstance --query "registrationState" -o tsv
if ($providerStatus -ne "Registered") {
    Write-Host "  Registering provider (may take a few minutes)..." -ForegroundColor Yellow
    & $azPath provider register --namespace Microsoft.ContainerInstance --output none
    Start-Sleep -Seconds 30
}
Write-Host "  Provider ready" -ForegroundColor Green

# Step 2: Get ACR Credentials
Write-Host "`nStep 2: Retrieving ACR credentials..." -ForegroundColor Green
$acrPassword = & $azPath acr credential show `
    --resource-group $resourceGroup `
    --name $acrName `
    --query "passwords[0].value" -o tsv
Write-Host "  Credentials retrieved" -ForegroundColor Green

# Step 3: Deploy Container
Write-Host "`nStep 3: Deploying to Azure Container Instances..." -ForegroundColor Green
Write-Host "  This may take 2-3 minutes..." -ForegroundColor Gray

& $azPath container create `
    --resource-group $resourceGroup `
    --name $containerName `
    --image "$acrUrl/techconnect-api:latest" `
    --cpu 1 `
    --memory 1.5 `
    --registry-login-server "$acrUrl" `
    --registry-username $acrName `
    --registry-password $acrPassword `
    --ports $containerPort `
    --os-type Linux `
    --dns-name-label $containerName `
    --output none 2>&1 | Out-Null

Write-Host "  Container deployment initiated" -ForegroundColor Green

# Step 4: Get Container URL
Write-Host "`nStep 4: Waiting for container to start..." -ForegroundColor Green
Start-Sleep -Seconds 5

$containerStatus = & $azPath container show `
    --resource-group $resourceGroup `
    --name $containerName `
    --query "containers[0].instanceView.currentState.state" -o tsv

$containerUrl = & $azPath container show `
    --resource-group $resourceGroup `
    --name $containerName `
    --query "ipAddress.fqdn" -o tsv

Write-Host "  Container Status: $containerStatus" -ForegroundColor Gray
$url = "http://$containerUrl`:$containerPort"
Write-Host "  Container URL: $url" -ForegroundColor Cyan

# Step 5: Test Endpoints
Write-Host "`nStep 5: Testing API endpoints..." -ForegroundColor Green
Write-Host "  Waiting for container to become healthy..." -ForegroundColor Gray

$maxAttempts = 30
$attempt = 0

while ($attempt -lt $maxAttempts) {
    try {
        $healthUri = "http://$containerUrl`:$containerPort/health"
        $response = Invoke-WebRequest -Uri $healthUri -TimeoutSec 3 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "  API is healthy!" -ForegroundColor Green
            break
        }
    } catch {
        # Container not ready yet
    }
    
    if ($attempt % 10 -eq 0 -and $attempt -gt 0) {
        Write-Host "  Still waiting... ($attempt/$maxAttempts seconds)" -ForegroundColor Gray
    }
    
    $attempt++
    Start-Sleep -Seconds 1
}

# Step 6: Display Summary
Write-Host "`n=== Deployment Complete ===" -ForegroundColor Green
Write-Host "`nContainer Details:" -ForegroundColor Cyan
Write-Host "  Name:     $containerName" -ForegroundColor Gray
Write-Host "  URL:      http://$containerUrl" -ForegroundColor Gray
Write-Host "  Port:     $containerPort" -ForegroundColor Gray
Write-Host "  Status:   $containerStatus" -ForegroundColor Gray

Write-Host "`nTest These Endpoints:" -ForegroundColor Cyan
Write-Host "  Health:       curl http://$containerUrl`:$containerPort/health" -ForegroundColor Gray
Write-Host "  Accelerators: curl http://$containerUrl`:$containerPort/accelerators" -ForegroundColor Gray
Write-Host "  Context:      curl -X POST http://$containerUrl`:$containerPort/context " -ForegroundColor Gray
Write-Host "                  -H 'Content-Type: application/json' " -ForegroundColor Gray
Write-Host "                  -d '{""scenario_title"":""AI automation"",""num_results"":1}'" -ForegroundColor Gray

Write-Host "`nView Logs:" -ForegroundColor Cyan
Write-Host "  az container logs --name $containerName --resource-group $resourceGroup --follow" -ForegroundColor Gray

Write-Host "`nManagement Commands:" -ForegroundColor Cyan
Write-Host "  Restart:  az container restart --name $containerName --resource-group $resourceGroup" -ForegroundColor Gray
Write-Host "  Stop:     az container stop --name $containerName --resource-group $resourceGroup" -ForegroundColor Gray
Write-Host "  Start:    az container start --name $containerName --resource-group $resourceGroup" -ForegroundColor Gray
Write-Host "  Delete:   az container delete --name $containerName --resource-group $resourceGroup --yes" -ForegroundColor Gray

Write-Host "`nEstimated Cost: ~$0.20/hour while running" -ForegroundColor Yellow
Write-Host "Remember to stop/delete container when not in use!`n" -ForegroundColor Yellow

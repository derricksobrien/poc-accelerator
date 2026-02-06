#!/usr/bin/env powershell
<#
.SYNOPSIS
Quick setup script for TechConnect API - Local development with Docker

.DESCRIPTION
Automates:
1. Virtual environment creation
2. Dependency installation
3. Docker build and compose setup
4. Initial testing

.EXAMPLE
.\setup.ps1
.\setup.ps1 -SkipVenv  # Skip venv if already created
#>

param(
    [switch]$SkipVenv,
    [switch]$DockerOnly,
    [string]$Port = 8000
)

$ErrorActionPreference = "Stop"

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║        TechConnect API - Local Development Setup          ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

# Check prerequisites
Write-Host "`n📦 Checking prerequisites..." -ForegroundColor Green

# Python check
try {
    $pythonVersion = python --version
    Write-Host "✓ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Install from https://python.org" -ForegroundColor Red
    exit 1
}

# Docker check
try {
    $dockerVersion = docker --version
    Write-Host "✓ Docker: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker not found. Install from https://docker.com" -ForegroundColor Red
    exit 1
}

# Stage 1: Native Python Setup
if (-not $DockerOnly) {
    Write-Host "`n🐍 Stage 1: Native Python Setup" -ForegroundColor Green
    
    # Create venv
    if (-not $SkipVenv -and -not (Test-Path ".venv")) {
        Write-Host "  Creating virtual environment..." -ForegroundColor Gray
        python -m venv .venv
        Write-Host "  ✓ Virtual environment created" -ForegroundColor Green
    } else {
        Write-Host "  ✓ Virtual environment exists (or skipped)" -ForegroundColor Green
    }
    
    # Activate venv
    Write-Host "  Activating virtual environment..." -ForegroundColor Gray
    & .\.venv\Scripts\Activate.ps1
    
    # Install dependencies
    Write-Host "  Installing dependencies..." -ForegroundColor Gray
    pip install -q -r requirements.txt
    Write-Host "  ✓ Dependencies installed" -ForegroundColor Green
    
    # Run tests
    Write-Host "`n🧪 Running tests..." -ForegroundColor Green
    python test_mvp.py
    
    Write-Host "`n✓ Native setup complete!" -ForegroundColor Green
    Write-Host "  To start API: python -m uvicorn api.main:app --port $Port" -ForegroundColor Cyan
}

# Stage 2: Docker Setup
Write-Host "`n🐳 Stage 2: Docker Setup" -ForegroundColor Green

# Create data directory
if (-not (Test-Path "data\chroma")) {
    Write-Host "  Creating data directory..." -ForegroundColor Gray
    New-Item -ItemType Directory -Path "data\chroma" -Force | Out-Null
    Write-Host "  ✓ Data directory created" -ForegroundColor Green
}

# Build Docker image
Write-Host "  Building Docker image..." -ForegroundColor Gray
docker build -t techconnect-api:latest . | Out-Null
Write-Host "  ✓ Docker image built" -ForegroundColor Green

# Start services with docker-compose
Write-Host "  Starting services with docker-compose..." -ForegroundColor Gray
docker-compose up -d
Write-Host "  ✓ Services started" -ForegroundColor Green

# Wait for startup
Write-Host "  Waiting for API to be ready..." -ForegroundColor Gray
$maxAttempts = 30
$attempt = 0
while ($attempt -lt $maxAttempts) {
    try {
        $response = curl -s http://localhost:8000/health -ErrorAction SilentlyContinue
        if ($response) {
            Write-Host "  ✓ API is healthy" -ForegroundColor Green
            break
        }
    } catch {
        $null  # API not ready yet, continue waiting
    }
    $attempt++
    Start-Sleep -Seconds 1
}

if ($attempt -eq $maxAttempts) {
    Write-Host "  ⚠ API startup timeout. Checking logs..." -ForegroundColor Yellow
    docker-compose logs api
}

# Test API
Write-Host "`n🧪 Testing API endpoints..." -ForegroundColor Green
try {
    $health = curl -s http://localhost:8000/health
    Write-Host "  ✓ GET /health" -ForegroundColor Green
    
    $accs = curl -s http://localhost:8000/accelerators
    Write-Host "  ✓ GET /accelerators" -ForegroundColor Green
    
    $context = curl -s -X POST http://localhost:8000/context `
        -H "Content-Type: application/json" `
        -d '{"scenario_title":"test","num_results":1}'
    Write-Host "  ✓ POST /context" -ForegroundColor Green
} catch {
    Write-Host "  ✗ API test failed" -ForegroundColor Red
    docker-compose logs api
}

# Summary
Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                  🎉 Setup Complete!                        ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green

Write-Host "`n📍 Next Steps:" -ForegroundColor Cyan
Write-Host "  1. API running at:        http://localhost:8000" -ForegroundColor Gray
Write-Host "  2. View logs:             docker-compose logs -f api" -ForegroundColor Gray
Write-Host "  3. Stop services:         docker-compose down" -ForegroundColor Gray
Write-Host "  4. Run Skillable:         python skillable_simulator\demo.py" -ForegroundColor Gray
Write-Host "  5. Deploy to Azure:       See AZURE_DEPLOYMENT.md" -ForegroundColor Gray

Write-Host "`n📚 Documentation:" -ForegroundColor Cyan
Write-Host "  - Local Development:      SETUP_LOCAL.md" -ForegroundColor Gray
Write-Host "  - API Guide:              .github/copilot-instructions.md" -ForegroundColor Gray
Write-Host "  - Azure Deployment:       AZURE_DEPLOYMENT.md" -ForegroundColor Gray

Write-Host ""

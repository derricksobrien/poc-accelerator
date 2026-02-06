# System3-RAG Startup Script (PowerShell Version)
# Usage: powershell -ExecutionPolicy Bypass -File START_BOTH_TERMINALS.ps1
# Or: Right-click → Run with PowerShell

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                  SYSTEM3-RAG STARTUP SCRIPT                 ║" -ForegroundColor Cyan
Write-Host "║            Starting FastAPI Backend + Streamlit UI          ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Change to System3-RAG directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Verify we're in the right place
if (-not (Test-Path "app\main.py")) {
    Write-Host "ERROR: Could not find app\main.py" -ForegroundColor Red
    Write-Host "Make sure this script is in the System3-RAG directory" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✓ Found System3-RAG directory" -ForegroundColor Green
Write-Host "✓ Ready to start services" -ForegroundColor Green
Write-Host ""

# Function to start a terminal with a command
function Start-ServiceTerminal {
    param(
        [string]$Title,
        [string]$Command,
        [string]$Port
    )
    
    $psPath = (Get-Command powershell).Source
    
    Start-Process -FilePath $psPath -ArgumentList "-NoExit", "-Command", @"
        `$ProfilePath = `$PROFILE.CurrentUserAllHosts
        if (Test-Path `$ProfilePath) { . `$ProfilePath }
        .\.venv\Scripts\Activate.ps1
        Write-Host ""
        Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
        Write-Host "║  $($Title.PadRight(58))║" -ForegroundColor Green
        Write-Host "╠════════════════════════════════════════════════════════════╣" -ForegroundColor Green
        Write-Host "║  Port: $($Port.PadRight(53))║" -ForegroundColor Cyan
        Write-Host "║  Command: $($Command.PadRight(48))║" -ForegroundColor Cyan
        Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
        Write-Host ""
        $Command
"@ -WindowStyle Normal
}

Write-Host "📊 STARTING SERVICES..." -ForegroundColor Yellow
Write-Host ""

# Start Backend Terminal
Write-Host "1️⃣  Starting: FastAPI Backend (Terminal 1)" -ForegroundColor Cyan
Write-Host "   URL: http://localhost:8000" -ForegroundColor Gray
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor Gray
Write-Host ""

Start-ServiceTerminal `
    -Title "SYSTEM3-RAG BACKEND (FastAPI)" `
    -Command "python -m uvicorn app.main:app --reload" `
    -Port "8000"

# Wait for backend to start
Write-Host "⏳ Waiting for backend to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Start Frontend Terminal
Write-Host "2️⃣  Starting: Streamlit Frontend (Terminal 2)" -ForegroundColor Cyan
Write-Host "   URL: http://localhost:8501" -ForegroundColor Gray
Write-Host ""

Start-ServiceTerminal `
    -Title "SYSTEM3-RAG FRONTEND (Streamlit)" `
    -Command "streamlit run streamlit_app.py" `
    -Port "8501"

# Wait a moment for both to start
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                  ✅ SERVICES STARTED                        ║" -ForegroundColor Green
Write-Host "╠════════════════════════════════════════════════════════════╣" -ForegroundColor Green
Write-Host "║                                                            ║" -ForegroundColor Green
Write-Host "║  BACKEND (Terminal 1):                                     ║" -ForegroundColor Green
Write-Host "║    Port: 8000                                              ║" -ForegroundColor Cyan
Write-Host "║    Status: Running (if no errors in that window)           ║" -ForegroundColor Cyan
Write-Host "║    API Docs: http://localhost:8000/docs                    ║" -ForegroundColor Cyan
Write-Host "║                                                            ║" -ForegroundColor Green
Write-Host "║  FRONTEND (Terminal 2):                                    ║" -ForegroundColor Green
Write-Host "║    Port: 8501                                              ║" -ForegroundColor Cyan
Write-Host "║    Status: Running (if no errors in that window)           ║" -ForegroundColor Cyan
Write-Host "║    URL: http://localhost:8501                              ║" -ForegroundColor Cyan
Write-Host "║                                                            ║" -ForegroundColor Green
Write-Host "║  NEXT STEP:                                                ║" -ForegroundColor Green
Write-Host "║    Open browser: http://localhost:8501                     ║" -ForegroundColor Yellow
Write-Host "║                                                            ║" -ForegroundColor Green
Write-Host "║  MONITORING:                                               ║" -ForegroundColor Green
Write-Host "║    - Watch both terminal windows for status                ║" -ForegroundColor Gray
Write-Host "║    - Look for 'Application startup complete'              ║" -ForegroundColor Gray
Write-Host "║    - Watch for any red error messages                     ║" -ForegroundColor Gray
Write-Host "║                                                            ║" -ForegroundColor Green
Write-Host "║  TO STOP:                                                  ║" -ForegroundColor Green
Write-Host "║    - Close either terminal window                          ║" -ForegroundColor Gray
Write-Host "║    - Or press CTRL+C in either window                      ║" -ForegroundColor Gray
Write-Host "║                                                            ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

# Try to open browser
Write-Host "🌐 Attempting to open browser..." -ForegroundColor Yellow
try {
    Start-Process "http://localhost:8501"
    Write-Host "✓ Browser opening..." -ForegroundColor Green
}
catch {
    Write-Host "⚠️  Could not auto-open browser" -ForegroundColor Yellow
    Write-Host "   Please manually visit: http://localhost:8501" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✅ Setup complete! Check the two terminal windows above." -ForegroundColor Green
Write-Host ""

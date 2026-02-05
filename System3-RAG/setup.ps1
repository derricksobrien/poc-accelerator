# Setup and run System3-RAG with Streamlit (Windows PowerShell)

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Green
    python -m venv venv
    Write-Host "Virtual environment created!" -ForegroundColor Green
} else {
    Write-Host "Virtual environment already exists" -ForegroundColor Yellow
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Green
& .\venv\Scripts\Activate.ps1

# Install/upgrade dependencies
Write-Host "Installing dependencies..." -ForegroundColor Green
pip install -q --upgrade pip setuptools wheel
pip install -q -r requirements.txt

Write-Host "" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start the application:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. FastAPI Backend (in one terminal):" -ForegroundColor Cyan
Write-Host "   python -m uvicorn app.main:app --reload" -ForegroundColor White
Write-Host ""
Write-Host "2. Streamlit Frontend (in another terminal):" -ForegroundColor Cyan
Write-Host "   streamlit run streamlit_app.py" -ForegroundColor White
Write-Host ""
Write-Host "Backend will run at: http://localhost:8000" -ForegroundColor Green
Write-Host "Frontend will run at: http://localhost:8501" -ForegroundColor Green
Write-Host ""

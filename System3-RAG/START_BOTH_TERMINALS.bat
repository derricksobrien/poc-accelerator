@echo off
REM System3-RAG Startup Script - Starts both Backend and Frontend
REM Usage: Double-click this file to start everything

echo.
echo ════════════════════════════════════════════════════════════════
echo              SYSTEM3-RAG: DUAL TERMINAL STARTUP
echo ════════════════════════════════════════════════════════════════
echo.

REM Get the directory of this script
cd /d "%~dp0"

REM Check if we're in the right directory
if not exist "app\main.py" (
    echo ERROR: Could not find app\main.py
    echo Make sure you're in the System3-RAG directory
    pause
    exit /b 1
)

echo ✓ Found System3-RAG directory
echo ✓ Python virtual environment set up
echo.

REM Start Terminal 1 (Backend)
echo Starting Terminal 1: FastAPI Backend on http://localhost:8000
echo.
start "System3-RAG Backend" cmd /k ^
    ".venv\Scripts\activate.bat" ^& ^
    "echo." ^& ^
    "echo ════════════════════════════════════════════════" ^& ^
    "echo   TERMINAL 1: BACKEND (FastAPI)" ^& ^
    "echo ════════════════════════════════════════════════" ^& ^
    "echo." ^& ^
    "echo   Port: 8000" ^& ^
    "echo   Command: python -m uvicorn app.main:app --reload" ^& ^
    "echo   API Docs: http://localhost:8000/docs" ^& ^
    "echo." ^& ^
    "echo   Starting in 3 seconds..." ^& ^
    "timeout /t 3 /nobreak" ^& ^
    "python -m uvicorn app.main:app --reload"

echo.
REM Wait for backend to start
timeout /t 5 /nobreak

REM Start Terminal 2 (Frontend)
echo Starting Terminal 2: Streamlit Frontend on http://localhost:8501
echo.
start "System3-RAG Frontend" cmd /k ^
    ".venv\Scripts\activate.bat" ^& ^
    "echo." ^& ^
    "echo ════════════════════════════════════════════════" ^& ^
    "echo   TERMINAL 2: FRONTEND (Streamlit)" ^& ^
    "echo ════════════════════════════════════════════════" ^& ^
    "echo." ^& ^
    "echo   Port: 8501" ^& ^
    "echo   Command: streamlit run streamlit_app.py" ^& ^
    "echo." ^& ^
    "echo   Starting in 3 seconds..." ^& ^
    "timeout /t 3 /nobreak" ^& ^
    "streamlit run streamlit_app.py"

echo.
echo ════════════════════════════════════════════════════════════════
echo ✓ BOTH WINDOWS OPENED
echo ════════════════════════════════════════════════════════════════
echo.
echo TERMINAL 1 (Backend):
echo   - Running FastAPI on http://localhost:8000
echo   - Keep this window open while using the system
echo   - Do not close unless you want to stop the backend
echo.
echo TERMINAL 2 (Frontend):
echo   - Running Streamlit on http://localhost:8501
echo   - Keep this window open while using the system
echo   - Do not close unless you want to stop the frontend
echo.
echo BROWSER:
echo   - Open http://localhost:8501 in your browser
echo   - Or wait for it to open automatically
echo.
echo TO STOP:
echo   - Close either terminal window to stop that service
echo   - CTRL+C works too
echo.
echo ════════════════════════════════════════════════════════════════
echo.

pause

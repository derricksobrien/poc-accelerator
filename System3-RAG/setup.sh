#!/bin/bash

# Setup and run System3-RAG with Streamlit (Linux/MacOS)

echo ""
echo "========================================" 
echo "System3-RAG Setup Script"
echo "========================================" 
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created!"
else
    echo "⚠️  Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "🔧 Installing dependencies..."
pip install -q --upgrade pip setuptools wheel
pip install -q -r requirements.txt

echo ""
echo "========================================"
echo "✅ Setup Complete!"
echo "========================================"
echo ""
echo "To start the application:"
echo ""
echo "1. FastAPI Backend (in one terminal):"
echo "   python -m uvicorn app.main:app --reload"
echo ""
echo "2. Streamlit Frontend (in another terminal):"
echo "   streamlit run streamlit_app.py"
echo ""
echo "Backend will run at: http://localhost:8000"
echo "Frontend will run at: http://localhost:8501"
echo ""

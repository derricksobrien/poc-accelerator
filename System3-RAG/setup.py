#!/usr/bin/env python3
"""
Cross-platform setup script for System3-RAG

This script:
1. Creates a virtual environment if needed
2. Installs dependencies
3. Provides instructions for running the application
"""

import os
import sys
import subprocess
import platform

def run_command(cmd, description=""):
    """Run a shell command."""
    if description:
        print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(e.stderr)
        return False

def main():
    """Main setup function."""
    
    print("\n" + "="*50)
    print("🤖 System3-RAG Setup")
    print("="*50 + "\n")
    
    # Check Python version
    if sys.version_info < (3, 10):
        print("❌ Python 3.10+ required")
        sys.exit(1)
    
    os_name = platform.system()
    venv_path = "venv"
    
    # Create virtual environment
    if not os.path.exists(venv_path):
        print(f"📦 Creating virtual environment ({venv_path})...")
        if os.name == 'nt':  # Windows
            cmd = f"python -m venv {venv_path}"
        else:  # Linux/Mac
            cmd = f"python3 -m venv {venv_path}"
        
        if not run_command(cmd):
            sys.exit(1)
        print("✅ Virtual environment created\n")
    else:
        print(f"⚠️  Virtual environment already exists ({venv_path})\n")
    
    # Determine activation command
    if os.name == 'nt':  # Windows
        activate_cmd = f"{venv_path}\\Scripts\\activate"
        pip_cmd = f"{venv_path}\\Scripts\\pip"
        python_cmd = f"{venv_path}\\Scripts\\python"
    else:  # Linux/Mac
        activate_cmd = f"source {venv_path}/bin/activate"
        pip_cmd = f"{venv_path}/bin/pip"
        python_cmd = f"{venv_path}/bin/python"
    
    # Install dependencies
    print("📦 Installing dependencies...")
    if not run_command(f"{pip_cmd} install -q --upgrade pip setuptools wheel"):
        sys.exit(1)
    
    if not run_command(f"{pip_cmd} install -q -r requirements.txt"):
        sys.exit(1)
    
    print("✅ Dependencies installed\n")
    
    # Print instructions
    print("="*50)
    print("✅ Setup Complete!")
    print("="*50 + "\n")
    
    print("📚 Quick Start Instructions:\n")
    
    print("1️⃣  Activate Virtual Environment:")
    if os.name == 'nt':
        print(f"   {venv_path}\\Scripts\\Activate.ps1")
    else:
        print(f"   source {venv_path}/bin/activate\n")
    
    print("2️⃣  Start FastAPI Backend (Terminal 1):")
    print(f"   {python_cmd} -m uvicorn app.main:app --reload\n")
    
    print("3️⃣  Start Streamlit Frontend (Terminal 2):")
    print(f"   streamlit run streamlit_app.py\n")
    
    print("📖 URLs:")
    print("   Backend API: http://localhost:8000")
    print("   API Docs:    http://localhost:8000/docs")
    print("   Frontend:    http://localhost:8501\n")
    
    print("🚀 Ready to go! Visit http://localhost:8501 in your browser.\n")


if __name__ == "__main__":
    main()

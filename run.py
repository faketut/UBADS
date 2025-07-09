#!/usr/bin/env python3
"""
Startup script for the User Behavior Anomaly Detection System
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import flask
        import pandas
        import numpy
        import sklearn
        print("✅ All required dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install dependencies using: pip install -r requirements.txt")
        return False

def create_directories():
    """Create necessary directories if they don't exist"""
    directories = ['uploads', 'templates', 'static/css', 'static/js', 'static/images']
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directory structure verified")

def check_files():
    """Check if required files exist"""
    required_files = [
        'main.py',
        'app.py', 
        'config.py',
        'templates/index.html',
        'static/css/style.css',
        'static/js/app.js'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    
    print("✅ All required files found")
    return True

def install_dependencies():
    """Install dependencies if requirements.txt exists"""
    if Path('requirements.txt').exists():
        print("📦 Installing dependencies...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False
    else:
        print("⚠️  requirements.txt not found, skipping dependency installation")
        return True

def start_application():
    """Start the Flask application"""
    print("\n🚀 Starting User Behavior Anomaly Detection System...")
    print("=" * 60)
    
    try:
        from app import app
        print("✅ Application loaded successfully")
        print(f"🌐 Server will be available at: http://localhost:5000")
        print("📊 Dashboard: http://localhost:5000")
        print("🔧 API Health: http://localhost:5000/api/health")
        print("\nPress Ctrl+C to stop the server")
        print("=" * 60)
        
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True
        )
        
    except ImportError as e:
        print(f"❌ Failed to import application: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        sys.exit(1)

def main():
    """Main startup function"""
    print("🔍 User Behavior Anomaly Detection System - Startup Check")
    print("=" * 60)
    
    # Check Python version
    check_python_version()
    
    # Check and create directories
    create_directories()
    
    # Check required files
    if not check_files():
        print("\n❌ Please ensure all required files are present")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        print("\n📦 Attempting to install dependencies...")
        if not install_dependencies():
            print("\n❌ Please install dependencies manually:")
            print("   pip install -r requirements.txt")
            sys.exit(1)
    
    print("\n✅ All checks passed!")
    
    # Start the application
    start_application()

if __name__ == "__main__":
    main() 
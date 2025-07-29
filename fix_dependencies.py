#!/usr/bin/env python3
"""
Quick fix script for common dependency issues.
This script resolves version conflicts and missing packages.
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and return success status."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed")
        print(f"Error: {e.stderr}")
        return False

def main():
    print("🚀 LLM Query-Retrieval System - Dependency Fix")
    print("=" * 50)
    
    # Check if we're in a virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    if not in_venv:
        print("⚠️  WARNING: Not in virtual environment")
        print("Recommended: Create and activate virtual environment first")
        print("python -m venv venv && venv\\Scripts\\activate")
        
        use_user = input("Install with --user flag? (y/n): ").lower().startswith('y')
        user_flag = "--user" if use_user else ""
    else:
        print("✅ Virtual environment detected")
        user_flag = ""
    
    # Fix sequence
    fixes = [
        (f"python -m pip install --upgrade pip {user_flag}", "Upgrading pip"),
        (f"pip uninstall -y huggingface-hub {user_flag}", "Removing conflicting huggingface-hub"),
        (f"pip install huggingface-hub==0.17.3 {user_flag}", "Installing compatible huggingface-hub"),
        (f"pip install pydantic-settings==2.1.0 {user_flag}", "Installing pydantic-settings"),
        (f"pip install transformers==4.35.2 {user_flag}", "Installing compatible transformers"),
        (f"pip install torch==2.1.0 {user_flag}", "Installing stable torch"),
        (f"pip install sentence-transformers==2.2.2 {user_flag}", "Reinstalling sentence-transformers"),
        (f"pip install groq==0.4.1 {user_flag}", "Installing Groq"),
        (f"pip install fastapi==0.104.1 uvicorn==0.24.0 {user_flag}", "Installing FastAPI"),
    ]
    
    print(f"\n📦 Running fixes with {'--user flag' if user_flag else 'standard installation'}...")
    
    success_count = 0
    for command, description in fixes:
        if run_command(command, description):
            success_count += 1
        print()  # Add spacing
    
    print("=" * 50)
    print(f"📊 Results: {success_count}/{len(fixes)} fixes successful")
    
    if success_count == len(fixes):
        print("🎉 All fixes applied successfully!")
        print("\n🚀 Next steps:")
        print("1. Copy .env.example to .env")
        print("2. Add your Groq API key to .env")
        print("3. Run: python main.py")
    else:
        print("⚠️  Some fixes failed. Try:")
        print("1. Run as Administrator")
        print("2. Use virtual environment")
        print("3. Install packages individually")
    
    # Test imports
    print("\n🧪 Testing critical imports...")
    test_imports = [
        "fastapi",
        "groq", 
        "sentence_transformers",
        "pydantic_settings"
    ]
    
    for module in test_imports:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Quick fix for Pydantic settings import error.
Run this script to install the missing pydantic-settings package.
"""

import subprocess
import sys
import os

def install_pydantic_settings():
    """Install pydantic-settings package."""
    print("🔧 Installing missing pydantic-settings package...")
    
    try:
        # Try to install with pip
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "pydantic-settings==2.1.0"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ pydantic-settings installed successfully!")
            return True
        else:
            print("❌ Standard installation failed, trying with --user flag...")
            # Try with --user flag for permission issues
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "--user", "pydantic-settings==2.1.0"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ pydantic-settings installed with --user flag!")
                return True
            else:
                print(f"❌ Installation failed: {result.stderr}")
                return False
                
    except Exception as e:
        print(f"❌ Error installing package: {e}")
        return False

def main():
    print("🚀 Pydantic Settings Fix")
    print("=" * 30)
    
    # Check if already installed
    try:
        import pydantic_settings
        print("✅ pydantic-settings is already installed!")
        return
    except ImportError:
        print("⚠️  pydantic-settings not found, installing...")
    
    # Install the package
    if install_pydantic_settings():
        print("\n🎉 Fix completed successfully!")
        print("You can now run: python main.py")
    else:
        print("\n❌ Fix failed. Manual solutions:")
        print("1. Run as administrator: pip install pydantic-settings")
        print("2. Use virtual environment: python -m venv venv && venv\\Scripts\\activate")
        print("3. Install manually: pip install --user pydantic-settings")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Setup script for the LLM-Powered Query-Retrieval System.
This script helps users set up the environment and configuration.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def print_header():
    """Print setup header."""
    print("="*60)
    print("🚀 LLM-Powered Query-Retrieval System Setup")
    print("="*60)

def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required.")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} is compatible")
    return True

def create_virtual_environment():
    """Create virtual environment."""
    print("\n🏗️  Creating virtual environment...")
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("⚠️  Virtual environment already exists")
        return True
    
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to create virtual environment")
        return False

def get_activation_command():
    """Get the command to activate virtual environment."""
    if os.name == 'nt':  # Windows
        return "venv\\Scripts\\activate"
    else:  # Unix/Linux/macOS
        return "source venv/bin/activate"

def install_dependencies():
    """Install Python dependencies."""
    print("\n📦 Installing dependencies...")
    
    # Determine pip path
    if os.name == 'nt':  # Windows
        pip_path = Path("venv/Scripts/pip")
    else:  # Unix/Linux/macOS
        pip_path = Path("venv/bin/pip")
    
    if not pip_path.exists():
        print("❌ Virtual environment not found. Please run setup again.")
        return False
    
    try:
        # Upgrade pip first
        subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True)
        
        # Try standard installation first
        print("Trying standard installation...")
        result = subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
            return True
        else:
            # If standard fails, try with --user flag (Windows permission fix)
            print("Standard installation failed, trying with --user flag...")
            result = subprocess.run([str(pip_path), "install", "--user", "-r", "requirements.txt"], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Dependencies installed successfully with --user flag")
                print("⚠️  Note: Packages installed in user directory")
                return True
            else:
                print(f"❌ Failed to install dependencies:")
                print(f"Error: {result.stderr}")
                print("\n💡 SOLUTIONS:")
                if os.name == 'nt':
                    print("1. Run setup as Administrator")
                    print("2. Use the Windows batch script: setup_windows.bat")
                    print("3. Use Conda: conda create -n bajaj-env python=3.9")
                else:
                    print("1. Check Python and pip installation")
                    print("2. Try: sudo python setup.py (if on Linux)")
                return False
                
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_environment_file():
    """Set up environment configuration file."""
    print("\n⚙️  Setting up environment configuration...")
    
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if env_file.exists():
        print("⚠️  .env file already exists")
        return True
    
    if not env_example.exists():
        print("❌ .env.example file not found")
        return False
    
    try:
        shutil.copy(env_example, env_file)
        print("✅ .env file created from template")
        print("⚠️  Please edit .env file with your API keys:")
        print("   - OPENAI_API_KEY (required)")
        print("   - PINECONE_API_KEY (optional)")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def create_data_directories():
    """Create necessary data directories."""
    print("\n📁 Creating data directories...")
    
    directories = [
        "data",
        "data/uploads",
        "data/faiss_index"
    ]
    
    for directory in directories:
        dir_path = Path(directory)
        dir_path.mkdir(parents=True, exist_ok=True)
    
    print("✅ Data directories created")
    return True

def test_imports():
    """Test if critical imports work."""
    print("\n🧪 Testing critical imports...")
    
    # Use the virtual environment's Python
    if os.name == 'nt':  # Windows
        python_path = Path("venv/Scripts/python")
    else:  # Unix/Linux/macOS
        python_path = Path("venv/bin/python")
    
    if not python_path.exists():
        print("❌ Virtual environment Python not found")
        return False
    
    test_script = '''
import sys
try:
    import fastapi
    import openai
    import numpy
    import tiktoken
    print("✅ All critical imports successful")
    sys.exit(0)
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)
'''
    
    try:
        result = subprocess.run([str(python_path), "-c", test_script], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout.strip())
            return True
        else:
            print(result.stdout.strip())
            return False
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def print_next_steps():
    """Print next steps for the user."""
    print("\n" + "="*60)
    print("🎉 Setup Complete!")
    print("="*60)
    
    activation_cmd = get_activation_command()
    
    print(f"""
📝 Next Steps:

1. Activate the virtual environment:
   {activation_cmd}

2. Edit the .env file with your API keys:
   - Add your OpenAI API key (required)
   - Optionally add Pinecone credentials

3. Start the system:
   python main.py

4. Test the system:
   python examples/usage_examples.py

5. Access the API documentation:
   http://localhost:8000/docs

🔧 Configuration:
   - Edit .env file for API keys and settings
   - Modify src/config.py for advanced configuration

📚 Documentation:
   - README.md contains detailed usage instructions
   - API docs available at /docs endpoint

🆘 Troubleshooting:
   - Check logs in the terminal
   - Verify API keys in .env file
   - Test system health at /health endpoint
""")

def main():
    """Main setup function."""
    print_header()
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Create virtual environment
    if not create_virtual_environment():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Setup environment file
    if not setup_environment_file():
        return False
    
    # Create data directories
    if not create_data_directories():
        return False
    
    # Test imports
    if not test_imports():
        print("⚠️  Some imports failed, but setup continued")
        print("   This might be resolved after configuring API keys")
    
    # Print next steps
    print_next_steps()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ Setup failed. Please check the errors above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Setup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed with unexpected error: {e}")
        sys.exit(1)

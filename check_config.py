#!/usr/bin/env python3
"""
Configuration checker for the LLM-Powered Query-Retrieval System.
Verifies that all required components are properly configured.
"""

import os
import sys
from pathlib import Path
import importlib.util

def check_file_exists(file_path: str, description: str) -> bool:
    """Check if a file exists."""
    if Path(file_path).exists():
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description} missing: {file_path}")
        return False

def check_environment_variables() -> bool:
    """Check required environment variables."""
    print("\n🔧 Checking Environment Variables:")
    
    required_vars = {
        "GROQ_API_KEY": "Groq API key for LLM operations (FREE)"
    }
    
    optional_vars = {
        "OPENAI_API_KEY": "OpenAI API key (optional, for embeddings)",
        "PINECONE_API_KEY": "Pinecone API key (optional)",
        "PINECONE_ENVIRONMENT": "Pinecone environment (optional)"
    }
    
    all_good = True
    
    # Check required variables
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value and value != "your_groq_api_key_here" and not value.startswith("gsk_"):
            print(f"❌ {description}: Invalid format (should start with 'gsk_')")
            all_good = False
        elif value and value.startswith("gsk_"):
            print(f"✅ {description}: Set")
        else:
            print(f"❌ {description}: Not set or using placeholder")
            all_good = False
    
    # Check optional variables
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value and not value.startswith("your_"):
            print(f"✅ {description}: Set")
        else:
            print(f"⚠️  {description}: Not set (optional)")
    
    return all_good

def check_python_packages() -> bool:
    """Check if required Python packages are installed."""
    print("\n📦 Checking Python Packages:")
    
    required_packages = [
        "fastapi",
        "groq", 
        "numpy",
        "tiktoken",
        "pydantic",
        "pydantic_settings"
    ]
    
    optional_packages = [
        "fitz",  # PyMuPDF
        "pdfplumber",
        "sentence_transformers",
        "faiss",
        "pinecone"
    ]
    
    all_good = True
    
    # Check required packages
    for package in required_packages:
        try:
            if package == "fitz":
                import fitz
            else:
                __import__(package)
            print(f"✅ {package}: Installed")
        except ImportError:
            print(f"❌ {package}: Not installed")
            all_good = False
    
    # Check optional packages
    for package in optional_packages:
        try:
            if package == "fitz":
                import fitz
            elif package == "faiss":
                import faiss
            elif package == "pinecone":
                import pinecone
            else:
                __import__(package)
            print(f"✅ {package}: Installed")
        except ImportError:
            print(f"⚠️  {package}: Not installed (optional)")
    
    return all_good

def check_data_directories() -> bool:
    """Check if data directories exist."""
    print("\n📁 Checking Data Directories:")
    
    directories = [
        "data",
        "data/uploads", 
        "data/faiss_index"
    ]
    
    all_good = True
    for directory in directories:
        if check_file_exists(directory, f"Directory {directory}"):
            # Check if directory is writable
            try:
                test_file = Path(directory) / "test_write.tmp"
                test_file.touch()
                test_file.unlink()
                print(f"✅ {directory} is writable")
            except Exception:
                print(f"❌ {directory} is not writable")
                all_good = False
        else:
            all_good = False
    
    return all_good

def check_configuration_files() -> bool:
    """Check configuration files."""
    print("\n⚙️  Checking Configuration Files:")
    
    files = [
        (".env", "Environment configuration"),
        ("src/config.py", "Application config"),
        ("src/models.py", "Data models"),
        ("main.py", "Main application")
    ]
    
    all_good = True
    for file_path, description in files:
        if not check_file_exists(file_path, description):
            all_good = False
    
    return all_good

def test_api_connectivity() -> bool:
    """Test API connectivity (basic)."""
    print("\n🌐 Testing API Connectivity:")
    
    try:
        # Test Groq connection (primary)
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key and groq_key.startswith("gsk_"):
            print("✅ Groq API key format appears valid")
        else:
            print("❌ Groq API key not set or invalid format")
            return False
        
        # Test OpenAI connection (optional)
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key and openai_key.startswith("sk-"):
            print("✅ OpenAI API key format appears valid")
        else:
            print("⚠️  OpenAI API key not set (optional)")
        
        # Test Pinecone connection (if configured)
        pinecone_key = os.getenv("PINECONE_API_KEY")
        if pinecone_key and pinecone_key.startswith("pcsk_"):
            print("✅ Pinecone API key format appears valid")
        else:
            print("⚠️  Pinecone API key not set (optional)")
        
        return True
        
    except Exception as e:
        print(f"❌ API connectivity test failed: {e}")
        return False

def check_system_requirements() -> bool:
    """Check system requirements."""
    print("\n💻 Checking System Requirements:")
    
    # Check Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    if sys.version_info >= (3, 8):
        print(f"✅ Python version: {python_version}")
    else:
        print(f"❌ Python version {python_version} (3.8+ required)")
        return False
    
    # Check available memory (basic)
    try:
        import psutil
        memory = psutil.virtual_memory()
        memory_gb = memory.total / (1024**3)
        if memory_gb >= 4:
            print(f"✅ Available memory: {memory_gb:.1f} GB")
        else:
            print(f"⚠️  Available memory: {memory_gb:.1f} GB (4+ GB recommended)")
    except ImportError:
        print("⚠️  Cannot check memory (psutil not installed)")
    
    # Check disk space
    try:
        import shutil
        disk_usage = shutil.disk_usage(".")
        free_gb = disk_usage.free / (1024**3)
        if free_gb >= 1:
            print(f"✅ Free disk space: {free_gb:.1f} GB")
        else:
            print(f"⚠️  Free disk space: {free_gb:.1f} GB (1+ GB recommended)")
    except Exception:
        print("⚠️  Cannot check disk space")
    
    return True

def print_summary(checks_passed: int, total_checks: int):
    """Print configuration check summary."""
    print("\n" + "="*60)
    print("📋 CONFIGURATION CHECK SUMMARY")
    print("="*60)
    
    print(f"Checks passed: {checks_passed}/{total_checks}")
    
    if checks_passed == total_checks:
        print("✅ All critical checks passed!")
        print("🚀 System should be ready to run")
        print("\n🎯 Next steps:")
        print("1. Run: python main.py")
        print("2. Visit: http://localhost:8000/docs")
        print("3. Test: python examples/usage_examples.py")
    else:
        print("⚠️  Some checks failed")
        print("🔧 Please resolve the issues above before running")
        print("\n💡 Common solutions:")
        print("- Run: pip install -r requirements.txt")
        print("- Configure .env file with API keys")
        print("- Create missing directories")

def main():
    """Main configuration check function."""
    print("🔍 LLM-Powered Query-Retrieval System - Configuration Check")
    print("="*60)
    
    # Load environment variables from .env file if it exists
    if Path(".env").exists():
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Loaded environment variables from .env file")
    else:
        print("⚠️  No .env file found")
    
    checks = [
        ("System Requirements", check_system_requirements),
        ("Configuration Files", check_configuration_files),
        ("Data Directories", check_data_directories),
        ("Python Packages", check_python_packages),
        ("Environment Variables", check_environment_variables),
        ("API Connectivity", test_api_connectivity)
    ]
    
    passed_checks = 0
    total_checks = len(checks)
    
    for check_name, check_function in checks:
        print(f"\n{'='*20} {check_name} {'='*20}")
        try:
            if check_function():
                passed_checks += 1
        except Exception as e:
            print(f"❌ {check_name} check failed with error: {e}")
    
    print_summary(passed_checks, total_checks)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Configuration check interrupted by user.")
    except Exception as e:
        print(f"\n❌ Configuration check failed: {e}")

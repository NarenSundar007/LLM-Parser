@echo off
echo =====================================================
echo  LLM Query-Retrieval System - Windows Setup
echo =====================================================

echo.
echo [1/6] Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo.
echo [2/6] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists, skipping...
) else (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully!
)

echo.
echo [3/6] Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo.
echo [4/6] Upgrading pip...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo WARNING: Failed to upgrade pip, continuing...
)

echo.
echo [5/6] Installing dependencies...
echo Trying standard installation...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Standard installation failed, trying with --user flag...
    pip install --user -r requirements.txt
    if %errorlevel% neq 0 (
        echo.
        echo ERROR: Package installation failed!
        echo.
        echo SOLUTIONS:
        echo 1. Run this script as Administrator
        echo 2. Use Conda instead: conda create -n bajaj-env python=3.9
        echo 3. Install packages individually with --user flag
        echo.
        pause
        exit /b 1
    )
)

echo.
echo [6/6] Creating environment file...
if exist .env (
    echo .env file already exists, skipping...
) else (
    copy .env.example .env
    echo .env file created from template
)

echo.
echo =====================================================
echo  SETUP COMPLETED SUCCESSFULLY!
echo =====================================================
echo.
echo Next steps:
echo 1. Edit .env file with your API keys
echo 2. Run: python main.py
echo 3. Visit: http://localhost:8000/docs
echo.
echo To activate environment in future sessions:
echo   venv\Scripts\activate
echo.
pause

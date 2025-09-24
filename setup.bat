@echo off
REM Setup script for Kajetany BIP project (Windows)
REM This ensures consistent development environment across all developers

echo 🚀 Setting up Kajetany BIP development environment...

REM Check if Python 3.8+ is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH. Please install Python 3.8 or newer.
    pause
    exit /b 1
)

REM Check Python version (basic check)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Found Python %PYTHON_VERSION%
echo ✅ Python version check passed

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install dependencies
echo 📚 Installing dependencies and development tools...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo ❌ Failed to upgrade pip
    pause
    exit /b 1
)

python -m pip install -e ".[dev]"
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

REM Install pre-commit hooks
echo 🪝 Setting up pre-commit hooks...
pre-commit install
if errorlevel 1 (
    echo ⚠️ Warning: Failed to install pre-commit hooks (this is optional)
)

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo 📝 Creating .env file template...
    (
        echo # Email configuration for notifications
        echo SMTP_USER=your-email@gmail.com
        echo SMTP_PASS=your-app-password
        echo.
        echo # Uncomment and modify if needed
        echo # DEBUG=true
    ) > .env
    echo ⚠️ Please edit .env file with your actual credentials
)

echo.
echo 🎉 Setup complete! Your development environment is ready.
echo.
echo 📋 Next steps:
echo    1. Edit .env file with your email credentials
echo    2. Run 'venv\Scripts\activate.bat' to activate the environment
echo    3. Run 'python main.py' to test the application
echo.
echo 🔧 Available commands:
echo    - ruff check . (lint code)
echo    - ruff check . --fix (auto-fix issues)
echo    - ruff format . (format code)
echo    - pre-commit run --all-files (run all checks)
echo.

pause

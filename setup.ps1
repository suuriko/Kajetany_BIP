# Setup script for Kajetany BIP project (Windows PowerShell)
# This ensures consistent development environment across all developers

Write-Host "🚀 Setting up Kajetany BIP development environment..." -ForegroundColor Green

# Check if Python 3.8+ is available
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }

    # Extract version number and check if it's 3.8+
    if ($pythonVersion -match "Python (\d+)\.(\d+)\.(\d+)") {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]

        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 8)) {
            Write-Host "❌ Python 3.8+ is required. Found: $pythonVersion" -ForegroundColor Red
            Write-Host "Please install Python 3.8 or newer from https://python.org" -ForegroundColor Yellow
            Read-Host "Press Enter to exit"
            exit 1
        }
    }

    Write-Host "Found: $pythonVersion" -ForegroundColor Cyan
    Write-Host "✅ Python version check passed" -ForegroundColor Green
}
catch {
    Write-Host "❌ Python is not installed or not in PATH." -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://python.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Activate virtual environment
Write-Host "🔄 Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to activate virtual environment" -ForegroundColor Red
    Write-Host "You may need to run: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Install dependencies
Write-Host "📚 Installing dependencies and development tools..." -ForegroundColor Yellow
python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to upgrade pip" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

python -m pip install -e ".[dev]"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Install pre-commit hooks
Write-Host "🪝 Setting up pre-commit hooks..." -ForegroundColor Yellow
pre-commit install
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️ Warning: Failed to install pre-commit hooks (this is optional)" -ForegroundColor Yellow
}

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "📝 Creating .env file template..." -ForegroundColor Yellow
    @"
# Email configuration for notifications
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password

# Uncomment and modify if needed
# DEBUG=true
"@ | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "⚠️ Please edit .env file with your actual credentials" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 Setup complete! Your development environment is ready." -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "   1. Edit .env file with your email credentials" -ForegroundColor White
Write-Host "   2. Run '.\venv\Scripts\Activate.ps1' to activate the environment" -ForegroundColor White
Write-Host "   3. Run 'python main.py' to test the application" -ForegroundColor White
Write-Host ""
Write-Host "🔧 Available commands:" -ForegroundColor Cyan
Write-Host "   - ruff check . (lint code)" -ForegroundColor White
Write-Host "   - ruff check . --fix (auto-fix issues)" -ForegroundColor White
Write-Host "   - ruff format . (format code)" -ForegroundColor White
Write-Host "   - pre-commit run --all-files (run all checks)" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to continue"

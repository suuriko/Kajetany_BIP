#!/bin/bash

# Setup script for Kajetany BIP project
# This ensures consistent development environment across all developers

echo "🚀 Setting up Kajetany BIP development environment..."

# Check if Python 3.8+ is available
if ! python3 --version | grep -E "Python 3\.(8|9|1[0-9])" > /dev/null; then
    echo "❌ Python 3.8+ is required. Please install Python 3.8 or newer."
    exit 1
fi

echo "✅ Python version check passed"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install pre-commit hooks
echo "🪝 Setting up pre-commit hooks..."
pre-commit install

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file template..."
    cat > .env << EOF
# Email configuration for notifications
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password

# Uncomment and modify if needed
# DEBUG=true
EOF
    echo "⚠️  Please edit .env file with your actual credentials"
fi

echo ""
echo "🎉 Setup complete! Your development environment is ready."
echo ""
echo "📋 Next steps:"
echo "   1. Edit .env file with your email credentials"
echo "   2. Run 'source venv/bin/activate' to activate the environment"
echo "   3. Run 'python main.py' to test the application"
echo ""
echo "🔧 Available commands:"
echo "   - black . (format code)"
echo "   - isort . (sort imports)"
echo "   - ruff . (lint code)"

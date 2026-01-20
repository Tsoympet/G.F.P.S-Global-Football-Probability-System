#!/bin/bash

# GFPS Backend Startup Script
# This script starts the GFPS FastAPI backend server

set -e

echo "🚀 Starting GFPS Backend Server..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Error: Python is not installed or not in PATH"
    echo "Please install Python 3.8 or later from https://www.python.org/downloads/"
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "✅ Found Python: $($PYTHON_CMD --version)"
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 No virtual environment found. Creating one..."
    $PYTHON_CMD -m venv .venv
    echo "✅ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Check if dependencies are installed
if [ ! -f ".venv/.deps_installed" ]; then
    echo "📥 Installing backend dependencies (this may take a few minutes)..."
    pip install --upgrade pip
    pip install -r backend/requirements.txt
    touch .venv/.deps_installed
    echo "✅ Dependencies installed"
    echo ""
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚙️  No .env file found. Creating from template..."
    cp .env.example .env
    
    # Generate a SECRET_KEY if not set
    if ! grep -q "^SECRET_KEY=.\+" .env; then
        echo "🔐 Generating SECRET_KEY..."
        SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || python -c "import secrets; print(secrets.token_hex(32))")
        sed -i.bak "s/^SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env && rm .env.bak 2>/dev/null || sed -i '' "s/^SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
        echo "✅ SECRET_KEY generated"
    fi
    echo ""
fi

# Initialize database if needed
if [ ! -f "gfps.db" ]; then
    echo "🗄️  Initializing database..."
    python -m backend.db_init 2>/dev/null || echo "⚠️  Database initialization skipped (optional)"
    echo ""
fi

echo "🌐 Starting FastAPI backend server..."
echo "📍 Server will be available at: http://localhost:8000"
echo "📍 API documentation: http://localhost:8000/docs"
echo "📍 Health check: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

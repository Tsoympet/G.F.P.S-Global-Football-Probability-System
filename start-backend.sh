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
        # Try openssl first, fall back to Python
        if command -v openssl &> /dev/null; then
            SECRET_KEY=$(openssl rand -hex 32)
        elif [ -n "$PYTHON_CMD" ]; then
            SECRET_KEY=$($PYTHON_CMD -c "import secrets; print(secrets.token_hex(32))")
        else
            echo "❌ Error: Unable to generate SECRET_KEY (openssl and Python not available)"
            exit 1
        fi
        
        if [ -z "$SECRET_KEY" ]; then
            echo "❌ Error: Failed to generate SECRET_KEY"
            exit 1
        fi
        
        # Update the SECRET_KEY line in .env file
        # Using | as delimiter to avoid issues with / in the secret key
        # This sed command works on both GNU sed (Linux) and BSD sed (macOS)
        if sed --version 2>&1 | grep -q GNU; then
            # GNU sed (Linux)
            sed -i "s|^SECRET_KEY=.*|SECRET_KEY=$SECRET_KEY|" .env
        else
            # BSD sed (macOS) requires -i with empty string for in-place editing
            sed -i '' "s|^SECRET_KEY=.*|SECRET_KEY=$SECRET_KEY|" .env
        fi
        echo "✅ SECRET_KEY generated and saved to .env"
    fi
    echo ""
fi

# Initialize database if needed
if [ ! -f "gfps.db" ]; then
    echo "🗄️  Initializing database..."
    # Try to initialize the database, but don't fail if it doesn't work
    # The backend will create tables automatically on first run if init fails
    if ! $PYTHON_CMD -m backend.db_init 2>&1; then
        echo "⚠️  Database initialization had issues, but backend will auto-create on first run"
    else
        echo "✅ Database initialized successfully"
    fi
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

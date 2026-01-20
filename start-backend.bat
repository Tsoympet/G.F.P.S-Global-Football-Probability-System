@echo off
REM GFPS Backend Startup Script for Windows
REM This script starts the GFPS FastAPI backend server

echo.
echo ======================================
echo   GFPS Backend Server Startup
echo ======================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or later from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Found Python: 
python --version
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    echo No virtual environment found. Creating one...
    python -m venv .venv
    echo Virtual environment created
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Check if dependencies are installed
if not exist ".venv\.deps_installed" (
    echo Installing backend dependencies (this may take a few minutes)...
    python -m pip install --upgrade pip
    pip install -r backend\requirements.txt
    echo. > .venv\.deps_installed
    echo Dependencies installed
    echo.
)

REM Check if .env file exists
if not exist ".env" (
    echo No .env file found. Creating from template...
    copy .env.example .env
    
    REM Generate a SECRET_KEY using a helper script for better maintainability
    echo Generating SECRET_KEY...
    python scripts\update_secret_key.py
    echo.
)

REM Initialize database if needed
if not exist "gfps.db" (
    echo Initializing database...
    REM Database initialization is optional - backend will auto-create tables if init fails
    python -m backend.db_init 2>nul || echo Database initialization skipped (backend will auto-create on first run)
    echo.
)

echo.
echo ======================================
echo   Starting FastAPI Backend Server
echo ======================================
echo.
echo Server will be available at: http://localhost:8000
echo API documentation: http://localhost:8000/docs
echo Health check: http://localhost:8000/health
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

@echo off
REM Simple backend startup script

cd backend

REM Create virtual environment if needed
if not exist "venv" (
    echo [*] Creating Python virtual environment...
    python -m venv venv
)

REM Activate venv
call venv\Scripts\activate.bat

REM Install core packages
pip install -q uvicorn fastapi python-dotenv pydantic 2>nul

REM Install all dependencies (ignore errors for optional packages)
pip install -q -r requirements.txt 2>nul

REM Start backend with proper env loading
python start_backend.py

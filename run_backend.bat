@echo off
REM Load environment variables from .env and start backend

setlocal enabledelayedexpansion

echo.
echo ========================================
echo NarrativeWatch AI - Backend Server
echo ========================================
echo.

REM Read .env file and set variables
for /f "delims==" %%A in (.env) do (
    if not "%%A"=="" (
        if not "%%A:~0,1%%" equ "#" (
            set %%A
        )
    )
)

REM Display loaded configuration
echo [*] Configuration loaded:
echo     - Google Cloud Project: %GOOGLE_CLOUD_PROJECT%
echo     - NewsAPI Key: %NEWSAPI_KEY:~0,10%...
echo     - Tavily API Key: %TAVILY_API_KEY:~0,10%...
echo.

REM Navigate to backend directory
cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo [*] Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo [*] Installing dependencies...
pip install -q -r requirements.txt

REM Start the backend server
echo.
echo ========================================
echo Starting Backend Server...
echo ========================================
echo.
echo URL: http://localhost:8000
echo Docs: http://localhost:8000/docs
echo.

python -m uvicorn src.app:app --reload --port 8000

endlocal

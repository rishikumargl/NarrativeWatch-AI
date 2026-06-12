@echo off
REM Load environment variables from .env and start backend

setlocal enabledelayedexpansion

echo.
echo ========================================
echo NarrativeWatch AI - Backend Server
echo ========================================
echo.

REM Navigate to backend directory first
cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo [*] Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Read .env file and set variables properly
echo [*] Loading configuration from .env...
for /f "usebackq delims=" %%A in (..\..env) do (
    set "line=%%A"
    if not "!line:~0,1!"=="#" (
        if not "!line!"=="" (
            for /f "delims== tokens=1,2" %%B in ("!line!") do (
                if "%%C"=="" (
                    set "%%B=%%C"
                ) else (
                    set "%%B=%%C"
                )
            )
        )
    )
)

REM Alternative: Load from parent directory .env
if exist "..\..env" (
    for /f "usebackq delims=" %%x in (..\..env) do (
        set "line=%%x"
        if not "!line:~0,1!"=="#" (
            if not "!line!"=="" (
                for /f "delims== tokens=1*" %%A in ("!line!") do (
                    set "%%A=%%B"
                )
            )
        )
    )
)

REM Display loaded configuration
echo [*] Configuration status:
if defined GOOGLE_CLOUD_PROJECT (
    echo     [✓] Google Cloud Project: %GOOGLE_CLOUD_PROJECT%
) else (
    echo     [!] Google Cloud Project: NOT SET
)

if defined NEWSAPI_KEY (
    echo     [✓] NewsAPI Key: Configured
) else (
    echo     [!] NewsAPI Key: NOT SET
)

if defined TAVILY_API_KEY (
    echo     [✓] Tavily API Key: Configured
) else (
    echo     [!] Tavily API Key: NOT SET
)

echo.

REM Install core dependencies first
echo [*] Installing dependencies...
pip install -q uvicorn fastapi python-dotenv pydantic

REM Install remaining dependencies
pip install -q -r requirements.txt 2>nul || (
    echo [!] Some optional dependencies failed to install, continuing anyway...
)

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

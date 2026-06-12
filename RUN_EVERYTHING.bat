@echo off
REM NarrativeWatch AI - Master Startup Script
REM This script starts both backend and frontend servers

echo.
echo ================================================================================
echo             NARRATIVEWATCH AI - STARTING APPLICATION
echo ================================================================================
echo.

REM Check if .env exists
if not exist ".env" (
    echo [ERROR] .env file not found!
    echo Please ensure .env file is in the project root directory.
    pause
    exit /b 1
)

echo [✓] Configuration file found
echo.

REM Display configuration
for /f "delims== tokens=1,2" %%A in (.env) do (
    if "%%A"=="NEWSAPI_KEY" (
        set "newsapi=%%B"
    )
    if "%%A"=="GOOGLE_CLOUD_PROJECT" (
        set "gcp=%%B"
    )
)

if defined newsapi (
    echo [✓] NewsAPI Key configured
) else (
    echo [!] NewsAPI Key not found
)

if defined gcp (
    echo [✓] Google Cloud Project configured: %gcp%
) else (
    echo [!] Google Cloud Project not found
)

echo.
echo [*] Starting backend server in new window...
start "NarrativeWatch - Backend (Port 8000)" /D "%CD%" cmd /k "call run_backend.bat"

echo [*] Waiting 3 seconds...
timeout /t 3 /nobreak

echo [*] Starting frontend server in new window...
start "NarrativeWatch - Frontend (Port 3000)" /D "%CD%" cmd /k "call run_frontend.bat"

echo.
echo ================================================================================
echo SUCCESS! Both servers are starting...
echo ================================================================================
echo.
echo [✓] Backend will be available at:   http://localhost:8000
echo [✓] Frontend will be available at:  http://localhost:3000
echo [✓] API Documentation:              http://localhost:8000/docs
echo.
echo [*] Two new windows should have opened (Backend and Frontend)
echo [*] If not, manually run:
echo     - run_backend.bat (for backend on port 8000)
echo     - run_frontend.bat (for frontend on port 3000)
echo.
echo Waiting 10 seconds before opening browser...
timeout /t 10 /nobreak

echo [*] Opening application in browser...
start http://localhost:3000

echo.
echo [✓] Application is ready!
echo [✓] Check the backend and frontend windows for server output
echo.
echo Press any key to close this window...
pause >nul


@echo off
REM Start frontend server

echo.
echo ========================================
echo NarrativeWatch AI - Frontend Server
echo ========================================
echo.

cd frontend

REM Install dependencies if needed
echo [*] Checking dependencies...
npm install

REM Start development server
echo.
echo ========================================
echo Starting Frontend Server...
echo ========================================
echo.
echo URL: http://localhost:3000
echo.

npm run dev

pause

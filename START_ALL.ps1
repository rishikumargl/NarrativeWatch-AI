# NarrativeWatch AI - Automated Startup Script (PowerShell)
# Run with: powershell -ExecutionPolicy Bypass -File START_ALL.ps1

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "NARRATIVEWATCH AI - AUTOMATED STARTUP" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if PostgreSQL is running
Write-Host "[1/7] Checking PostgreSQL..." -ForegroundColor Yellow
try {
    $testConn = psql -U postgres -c "SELECT 1;" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[✓] PostgreSQL is running" -ForegroundColor Green

        # Create database
        Write-Host "[2/7] Creating database..." -ForegroundColor Yellow
        psql -U postgres -c "CREATE DATABASE narrativewatch;" 2>$null
        psql -U postgres -d narrativewatch -c "CREATE EXTENSION IF NOT EXISTS vector;" 2>$null
        Write-Host "[✓] Database created/verified" -ForegroundColor Green
    } else {
        Write-Host "[!] PostgreSQL not running or not accessible" -ForegroundColor Red
        Write-Host "    Please start PostgreSQL service and try again" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
} catch {
    Write-Host "[!] Error checking PostgreSQL: $_" -ForegroundColor Red
}

Write-Host ""

# Verify configuration
Write-Host "[3/7] Verifying configuration..." -ForegroundColor Yellow
Push-Location "backend"
python verify_config.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] Configuration verification failed" -ForegroundColor Red
    Pop-Location
    Read-Host "Press Enter to exit"
    exit 1
}
Pop-Location
Write-Host ""

# Install Python dependencies
Write-Host "[4/7] Setting up Python environment..." -ForegroundColor Yellow
Push-Location "backend"

if (!(Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Cyan
    python -m venv venv
}

# Activate venv
& ".\venv\Scripts\Activate.ps1"

Write-Host "Installing dependencies..." -ForegroundColor Cyan
pip install -q -r requirements.txt
Write-Host "[✓] Python environment ready" -ForegroundColor Green

Pop-Location
Write-Host ""

# Install frontend dependencies
Write-Host "[5/7] Installing frontend dependencies..." -ForegroundColor Yellow
Push-Location "frontend"
npm install -q 2>$null
Write-Host "[✓] Frontend dependencies installed" -ForegroundColor Green
Pop-Location
Write-Host ""

# Start backend
Write-Host "[6/7] Starting Backend Server (port 8000)..." -ForegroundColor Yellow
$backendCmd = {
    Push-Location "backend"
    & ".\venv\Scripts\Activate.ps1"
    Write-Host ""
    Write-Host "================================" -ForegroundColor Green
    Write-Host "BACKEND SERVER STARTING" -ForegroundColor Green
    Write-Host "================================" -ForegroundColor Green
    Write-Host "URL: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "Docs: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host ""
    python -m uvicorn src.app:app --reload --port 8000
}

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd

Write-Host "[✓] Backend server process started" -ForegroundColor Green
Start-Sleep -Seconds 2

# Start frontend
Write-Host "[7/7] Starting Frontend Server (port 3000)..." -ForegroundColor Yellow
$frontendCmd = {
    Push-Location "frontend"
    Write-Host ""
    Write-Host "================================" -ForegroundColor Green
    Write-Host "FRONTEND SERVER STARTING" -ForegroundColor Green
    Write-Host "================================" -ForegroundColor Green
    Write-Host "URL: http://localhost:3000" -ForegroundColor Cyan
    Write-Host ""
    npm run dev
}

Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd

Write-Host "[✓] Frontend server process started" -ForegroundColor Green
Write-Host ""

Write-Host "================================================================================" -ForegroundColor Green
Write-Host "SUCCESS! NarrativeWatch AI is starting up!" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Waiting for servers to fully start... (15 seconds)" -ForegroundColor Yellow
Start-Sleep -Seconds 15

Write-Host ""
Write-Host "Opening frontend in browser..." -ForegroundColor Yellow
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "All services are running!" -ForegroundColor Green
Write-Host "Check the backend and frontend windows for server output." -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Enter to close this window (servers will continue running)" -ForegroundColor Yellow
Read-Host


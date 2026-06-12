#!/bin/bash

echo ""
echo "========================================"
echo "  NarrativeWatch AI - Development Setup"
echo "========================================"
echo ""

# Start Backend
echo "[1/2] Starting Backend Server..."
cd backend
python run.py &
BACKEND_PID=$!
sleep 3

# Start Frontend
echo "[2/2] Starting Frontend Server..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!
sleep 5

echo ""
echo "========================================"
echo "  Servers Started Successfully!"
echo "========================================"
echo ""
echo "Backend:   http://localhost:8000"
echo "Frontend:  http://localhost:3000 (or 3001/3002 if in use)"
echo "API Docs:  http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for user interrupt
wait

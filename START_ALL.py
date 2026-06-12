#!/usr/bin/env python
"""
NarrativeWatch AI - Complete Startup Script
Starts backend (FastAPI) and frontend (Vite) with a single command
"""

import subprocess
import os
import sys
import time
import platform
from pathlib import Path


class StarterScript:
    """Manages startup of all services"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        self.is_windows = platform.system() == "Windows"
        self.processes = []

    def print_header(self, text):
        """Print formatted header"""
        print(f"\n{'='*60}")
        print(f"  {text}")
        print(f"{'='*60}\n")

    def check_prerequisites(self):
        """Check if all prerequisites are installed"""
        self.print_header("Checking Prerequisites")

        # Check Python
        print("✓ Python installed")

        # Check PostgreSQL
        try:
            subprocess.run(["psql", "--version"], capture_output=True, check=True)
            print("✓ PostgreSQL installed")
        except:
            print("⚠ PostgreSQL not found - make sure it's installed and in PATH")
            print("  Visit: https://www.postgresql.org/download/")

        # Check Node.js
        try:
            subprocess.run(["node", "--version"], capture_output=True, check=True)
            print("✓ Node.js installed")
        except:
            print("⚠ Node.js not found - install from https://nodejs.org/")

        print()

    def setup_backend(self):
        """Setup backend environment"""
        self.print_header("Setting Up Backend")

        os.chdir(self.backend_dir)

        # Check if venv exists
        venv_path = self.backend_dir / "venv"
        if not venv_path.exists():
            print("Creating virtual environment...")
            subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
            print("✓ Virtual environment created")
        else:
            print("✓ Virtual environment exists")

        # Activate venv and install requirements
        print("\nInstalling dependencies...")
        if self.is_windows:
            pip_exe = venv_path / "Scripts" / "pip"
        else:
            pip_exe = venv_path / "bin" / "pip"

        subprocess.run([str(pip_exe), "install", "-r", "requirements.txt"], check=True)
        print("✓ Dependencies installed")

        os.chdir(self.project_root)

    def setup_frontend(self):
        """Setup frontend environment"""
        self.print_header("Setting Up Frontend")

        os.chdir(self.frontend_dir)

        # Check if node_modules exists
        if not (self.frontend_dir / "node_modules").exists():
            print("Installing npm packages...")
            subprocess.run(["npm", "install"], check=True)
            print("✓ NPM packages installed")
        else:
            print("✓ NPM packages exist")

        os.chdir(self.project_root)

    def check_database(self):
        """Check if database exists and create if needed"""
        self.print_header("Checking Database")

        try:
            # Check if database exists
            result = subprocess.run(
                ["psql", "-U", "postgres", "-lqt"],
                capture_output=True,
                text=True,
                check=True
            )

            if "narrativewatch" in result.stdout:
                print("✓ Database 'narrativewatch' exists")
            else:
                print("Creating database...")
                subprocess.run(
                    ["createdb", "-U", "postgres", "narrativewatch"],
                    check=True
                )
                print("✓ Database created")

            # Enable pgvector extension
            print("Enabling pgvector extension...")
            subprocess.run(
                ["psql", "-U", "postgres", "-d", "narrativewatch",
                 "-c", "CREATE EXTENSION IF NOT EXISTS vector;"],
                check=True
            )
            print("✓ pgvector extension enabled")

        except Exception as e:
            print(f"⚠ Database setup failed: {e}")
            print("  Make sure PostgreSQL is running and configured correctly")

    def start_backend(self):
        """Start FastAPI backend"""
        self.print_header("Starting Backend (FastAPI)")

        os.chdir(self.backend_dir)

        if self.is_windows:
            venv_activate = self.backend_dir / "venv" / "Scripts" / "activate.bat"
            # Use a batch command to activate venv and run uvicorn
            cmd = f'cmd /c "{venv_activate}" && uvicorn src.app:app --reload --host 0.0.0.0 --port 8000'
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            venv_python = self.backend_dir / "venv" / "bin" / "python"
            process = subprocess.Popen(
                [str(venv_python), "-m", "uvicorn", "src.app:app", "--reload",
                 "--host", "0.0.0.0", "--port", "8000"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

        self.processes.append(process)
        print(f"✓ Backend starting on http://localhost:8000")
        print(f"  API Docs: http://localhost:8000/docs")
        time.sleep(2)

        os.chdir(self.project_root)

    def start_frontend(self):
        """Start Vite frontend"""
        self.print_header("Starting Frontend (Vite)")

        os.chdir(self.frontend_dir)

        process = subprocess.Popen(
            ["npm", "run", "dev"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        self.processes.append(process)
        print(f"✓ Frontend starting on http://localhost:5173")
        time.sleep(2)

        os.chdir(self.project_root)

    def show_summary(self):
        """Show startup summary"""
        self.print_header("NarrativeWatch AI is Running")

        print("""
🎉 All services are now running!

📍 ENDPOINTS:
  Frontend:    http://localhost:5173
  API:         http://localhost:8000
  API Docs:    http://localhost:8000/docs
  ReDoc:       http://localhost:8000/redoc

🛠️  SERVICES:
  ✓ Backend (FastAPI) - Running on port 8000
  ✓ Frontend (Vite)   - Running on port 5173
  ✓ PostgreSQL        - Should be running

📖 DOCUMENTATION:
  • SETUP.md          - Quick start guide
  • LLD_AND_TEAM_PLAN.md - Full system design
  • PROJECT_STATUS.md - Current status

🎯 NEXT STEPS:
  1. Open http://localhost:5173 in your browser
  2. Try analyzing articles using the News API
  3. View agent analysis results
  4. Check backend logs for debugging

⚠️  TO STOP:
  Press Ctrl+C to stop all services

📞 FOR HELP:
  • Check logs: backend/logs/ and frontend logs
  • Review error messages above
  • Consult documentation files
        """)

    def cleanup(self, signum=None, frame=None):
        """Cleanup and stop all processes"""
        print("\n\nShutting down services...")
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                process.kill()
        print("✓ All services stopped")
        sys.exit(0)

    def run(self):
        """Run complete startup"""
        try:
            self.check_prerequisites()
            self.setup_backend()
            self.setup_frontend()
            self.check_database()
            self.start_backend()
            self.start_frontend()
            self.show_summary()

            # Keep running and handle signals
            import signal
            signal.signal(signal.SIGINT, self.cleanup)
            signal.signal(signal.SIGTERM, self.cleanup)

            # Wait for all processes
            for process in self.processes:
                process.wait()

        except KeyboardInterrupt:
            self.cleanup()
        except Exception as e:
            print(f"\n❌ Error: {e}")
            self.cleanup()
            sys.exit(1)


if __name__ == "__main__":
    starter = StarterScript()
    starter.run()

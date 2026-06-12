#!/usr/bin/env python3
"""Start NarrativeWatch AI Backend with proper environment loading"""

import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

def main():
    # Get the project root (parent of backend directory)
    backend_dir = Path(__file__).parent
    project_root = backend_dir.parent
    env_file = project_root / ".env"

    print("\n" + "="*50)
    print("NarrativeWatch AI - Backend Startup")
    print("="*50 + "\n")

    # Load environment variables
    if env_file.exists():
        load_dotenv(env_file)
        print(f"[OK] Loaded configuration from: {env_file}")
    else:
        print(f"[ERROR] .env file not found at {env_file}")
        sys.exit(1)

    # Verify required variables
    print("\nConfiguration Status:")
    required_vars = {
        "GROQ_API_KEY": "Groq API Key",
        "NEWSAPI_KEY": "NewsAPI Key",
        "TAVILY_API_KEY": "Tavily API Key",
        "DATABASE_URL": "Database URL",
    }

    all_set = True
    for var, desc in required_vars.items():
        value = os.getenv(var, "")
        if value:
            masked = f"{value[:10]}...{value[-5:]}" if len(value) > 15 else value
            print(f"  [OK] {desc}: {masked}")
        else:
            print(f"  [SKIP] {desc}: NOT SET")
            all_set = False

    if not all_set:
        print("\n[WARN] Some environment variables are not set.")
        print("The application may not work correctly.\n")

    print("\nStarting backend server...")
    print("URL: http://localhost:8000")
    print("Docs: http://localhost:8000/docs\n")

    # Start uvicorn
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "src.app:app",
            "--reload",
            "--port", "8000"
        ])
    except KeyboardInterrupt:
        print("\n\nShutdown requested.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

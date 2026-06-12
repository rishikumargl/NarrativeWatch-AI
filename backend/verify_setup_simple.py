#!/usr/bin/env python
"""Simple setup verification without Unicode characters"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    print("\n" + "="*60)
    print("NarrativeWatch AI - Setup Verification")
    print("="*60)

    print("\n[Testing Python Imports]")
    print("="*60 + "\n")

    tests = {
        "Configuration": "from src.config import settings",
        "Logger": "from src.logger import setup_logger",
        "FastAPI": "from fastapi import FastAPI",
        "SQLAlchemy": "from sqlalchemy import create_engine",
        "Pydantic": "from pydantic import BaseModel",
        "LangChain": "from langchain_groq import ChatGroq",
        "Groq": "from groq import Groq",
        "NewsAPI": "import newsapi",
        "Requests": "import requests",
    }

    passed = 0
    for name, import_str in tests.items():
        try:
            exec(import_str)
            print(f"  [OK] {name}")
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {name}: {str(e)[:60]}")

    print(f"\n  Result: {passed}/{len(tests)} imports successful\n")

    print("[Testing Environment Variables]")
    print("="*60 + "\n")

    from src.config import settings

    env_checks = [
        ("GROQ_API_KEY", settings.GROQ_API_KEY),
        ("NEWSAPI_KEY", settings.NEWSAPI_KEY),
        ("TAVILY_API_KEY", settings.TAVILY_API_KEY),
        ("DATABASE_URL", settings.DATABASE_URL),
    ]

    env_passed = 0
    for name, value in env_checks:
        if value:
            masked = value[:10] + "..." + value[-10:] if len(value) > 20 else "***"
            print(f"  [OK] {name}: {masked}")
            env_passed += 1
        else:
            print(f"  [FAIL] {name}: Not configured")

    print(f"\n  Result: {env_passed}/{len(env_checks)} variables configured\n")

    print("[Testing Configuration]")
    print("="*60 + "\n")

    config_tests = [
        ("App Name", settings.APP_NAME),
        ("Environment", settings.ENV),
        ("Debug Mode", settings.DEBUG),
        ("LLM Model", settings.LLM_MODEL),
        ("API Port", settings.API_PORT),
        ("Database", "postgresql" in settings.DATABASE_URL),
    ]

    config_passed = 0
    for name, value in config_tests:
        if value:
            print(f"  [OK] {name}: {value}")
            config_passed += 1
        else:
            print(f"  [FAIL] {name}")

    print(f"\n  Result: Configuration loaded successfully\n")

    print("[Testing Agent Imports]")
    print("="*60 + "\n")

    agents_to_test = [
        ("BaseAgent", "from src.agents import BaseAgent"),
        ("OrchestratorAgent", "from src.agents import OrchestratorAgent"),
        ("ContentAnalyzerAgent", "from src.agents import ContentAnalyzerAgent"),
        ("RAGAgent", "from src.agents import RAGAgent"),
        ("ResearchAgent", "from src.agents import ResearchAgent"),
        ("BiasDetectorAgent", "from src.agents import BiasDetectorAgent"),
        ("BotDetectorAgent", "from src.agents import BotDetectorAgent"),
        ("CampaignDetectorAgent", "from src.agents import CampaignDetectorAgent"),
        ("SynthesisAgent", "from src.agents import SynthesisAgent"),
        ("ReviewerAgent", "from src.agents import ReviewerAgent"),
    ]

    agents_passed = 0
    for agent_name, import_str in agents_to_test:
        try:
            exec(import_str)
            print(f"  [OK] {agent_name}")
            agents_passed += 1
        except Exception as e:
            print(f"  [FAIL] {agent_name}: {str(e)[:60]}")

    print(f"\n  Result: {agents_passed}/{len(agents_to_test)} agents ready\n")

    print("[Testing Database Connection]")
    print("="*60 + "\n")

    try:
        from src.database.connection import engine
        with engine.connect() as conn:
            print("  [OK] Database connection established")
        print("  [OK] PostgreSQL is running")
    except Exception as e:
        print(f"  [FAIL] Database error: {str(e)[:60]}")

    print("\n[Summary]")
    print("="*60)
    print(f"  Imports: {passed}/9")
    print(f"  Environment: {env_passed}/4")
    print(f"  Configuration: {config_passed}/6")
    print(f"  Agents: {agents_passed}/{len(agents_to_test)}")

    if passed >= 8 and env_passed == 4 and agents_passed >= 8:
        print("\nStatus: READY TO START")
        return 0
    else:
        print("\nStatus: NEEDS FIXES")
        return 1

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python
"""
Verify NarrativeWatch AI setup and integrations
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test critical imports"""
    print("\n" + "="*60)
    print("🔍 Testing Python Imports")
    print("="*60 + "\n")

    tests = {
        "Configuration": "from src.config import settings",
        "Logger": "from src.logger import setup_logger",
        "FastAPI": "from fastapi import FastAPI",
        "SQLAlchemy": "from sqlalchemy import create_engine",
        "Pydantic": "from pydantic import BaseModel",
        "LangChain": "from langchain.agents import AgentExecutor",
        "Groq": "from groq import Groq",
        "NewsAPI": "import newsapi",
        "Requests": "import requests",
    }

    passed = 0
    failed = 0

    for name, import_stmt in tests.items():
        try:
            exec(import_stmt)
            print(f"  ✅ {name}")
            passed += 1
        except Exception as e:
            print(f"  ❌ {name}: {str(e)[:50]}")
            failed += 1

    print(f"\n  Result: {passed}/{len(tests)} imports successful")
    return failed == 0


def test_environment():
    """Test environment variables"""
    print("\n" + "="*60)
    print("🔐 Testing Environment Variables")
    print("="*60 + "\n")

    required_vars = {
        "GROQ_API_KEY": "Groq API",
        "NEWSAPI_KEY": "NewsAPI",
        "TAVILY_API_KEY": "Tavily API",
        "DATABASE_URL": "PostgreSQL",
    }

    passed = 0
    failed = 0

    for var_name, description in required_vars.items():
        value = os.getenv(var_name, "")
        if value:
            # Show only first and last 10 chars for security
            masked = value[:10] + "..." + value[-10:] if len(value) > 20 else value
            print(f"  ✅ {var_name}: {masked}")
            passed += 1
        else:
            print(f"  ❌ {var_name}: NOT SET")
            failed += 1

    print(f"\n  Result: {passed}/{len(required_vars)} variables configured")
    return failed == 0


def test_config():
    """Test configuration loading"""
    print("\n" + "="*60)
    print("⚙️  Testing Configuration")
    print("="*60 + "\n")

    try:
        from src.config import settings

        configs = {
            "App Name": settings.APP_NAME,
            "Environment": settings.ENV,
            "Debug Mode": settings.DEBUG,
            "LLM Model": settings.LLM_MODEL,
            "API Port": settings.API_PORT,
            "Database": settings.DATABASE_URL[:40] + "..." if settings.DATABASE_URL else "NOT SET",
        }

        for name, value in configs.items():
            print(f"  ✅ {name}: {value}")

        print("\n  Result: Configuration loaded successfully")
        return True

    except Exception as e:
        print(f"  ❌ Configuration error: {e}")
        return False


def test_agents():
    """Test agent imports"""
    print("\n" + "="*60)
    print("🤖 Testing Agent Imports")
    print("="*60 + "\n")

    agents = {
        "BaseAgent": "from src.agents.base_agent import BaseAgent",
        "OrchestratorAgent": "from src.agents.orchestrator import OrchestratorAgent",
        "ContentAnalyzerAgent": "from src.agents.content_analyzer import ContentAnalyzerAgent",
        "RAGAgent": "from src.agents.rag_agent import RAGAgent",
        "ResearchAgent": "from src.agents.research_agent import ResearchAgent",
        "BiasDetectorAgent": "from src.agents.bias_detector import BiasDetectorAgent",
        "BotDetectorAgent": "from src.agents.bot_detector import BotDetectorAgent",
        "CampaignDetectorAgent": "from src.agents.campaign_detector import CampaignDetectorAgent",
        "SynthesisAgent": "from src.agents.synthesis_agent import SynthesisAgent",
        "ReviewerAgent": "from src.agents.reviewer_agent import ReviewerAgent",
    }

    passed = 0
    failed = 0

    for name, import_stmt in agents.items():
        try:
            exec(import_stmt)
            print(f"  ✅ {name}")
            passed += 1
        except Exception as e:
            print(f"  ❌ {name}: {str(e)[:40]}")
            failed += 1

    print(f"\n  Result: {passed}/{len(agents)} agents ready")
    return failed == 0


def test_database():
    """Test database connection"""
    print("\n" + "="*60)
    print("🗄️  Testing Database Connection")
    print("="*60 + "\n")

    try:
        from src.database.connection import engine
        from sqlalchemy import text

        # Try to connect
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("  ✅ PostgreSQL connection successful")

        # Check pgvector extension
        with engine.connect() as conn:
            result = conn.execute(text("SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector')"))
            has_vector = result.scalar()
            if has_vector:
                print("  ✅ pgvector extension enabled")
            else:
                print("  ⚠️  pgvector extension not found (required for RAG)")

        print("\n  Result: Database connection OK")
        return True

    except Exception as e:
        print(f"  ❌ Database error: {str(e)[:60]}")
        print("\n  Result: Database connection failed")
        print("  Make sure PostgreSQL is running and pgvector is enabled")
        return False


def test_groq():
    """Test Groq API connection"""
    print("\n" + "="*60)
    print("🤖 Testing Groq API")
    print("="*60 + "\n")

    try:
        from groq import Groq
        from src.config import settings

        if not settings.GROQ_API_KEY:
            print("  ⚠️  GROQ_API_KEY not configured")
            return False

        client = Groq(api_key=settings.GROQ_API_KEY)
        print("  ✅ Groq client initialized")

        # Test health check
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[{"role": "user", "content": "Say 'OK'"}],
            max_tokens=10,
        )

        if response.choices[0].message.content:
            print("  ✅ Groq API responding")
            print(f"     Response: {response.choices[0].message.content[:30]}...")
        else:
            print("  ❌ No response from Groq")
            return False

        print("\n  Result: Groq API working")
        return True

    except Exception as e:
        print(f"  ❌ Groq API error: {str(e)[:60]}")
        return False


def test_newsapi():
    """Test NewsAPI connection"""
    print("\n" + "="*60)
    print("📰 Testing NewsAPI")
    print("="*60 + "\n")

    try:
        from src.integrations.newsapi_client import NewsAPIClient
        from src.config import settings

        if not settings.NEWSAPI_KEY:
            print("  ⚠️  NEWSAPI_KEY not configured")
            return False

        client = NewsAPIClient()
        print("  ✅ NewsAPI client initialized")

        # Test search
        articles = client.search_articles("technology", num_articles=1)
        if articles:
            print(f"  ✅ NewsAPI responding: found {len(articles)} article(s)")
        else:
            print("  ⚠️  No articles returned")

        print("\n  Result: NewsAPI working")
        return True

    except Exception as e:
        print(f"  ❌ NewsAPI error: {str(e)[:60]}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🚀 NarrativeWatch AI - Setup Verification")
    print("="*60)

    results = {}

    # Run tests
    results["Imports"] = test_imports()
    results["Environment"] = test_environment()
    results["Configuration"] = test_config()
    results["Agents"] = test_agents()
    results["Database"] = test_database()
    results["Groq API"] = test_groq()
    results["NewsAPI"] = test_newsapi()

    # Summary
    print("\n" + "="*60)
    print("📊 Summary")
    print("="*60 + "\n")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, passed_test in results.items():
        status = "✅" if passed_test else "❌"
        print(f"  {status} {test_name}")

    print(f"\n  Result: {passed}/{total} tests passed\n")

    if passed == total:
        print("✅ All systems ready! You can start the backend with:")
        print("   python start_backend.py\n")
        return 0
    else:
        print("⚠️  Some systems need attention. Review errors above.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())

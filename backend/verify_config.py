#!/usr/bin/env python3
"""Verify NarrativeWatch AI configuration."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Fix encoding for Windows
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

print("=" * 70)
print("NARRATIVEWATCH AI - CONFIGURATION VERIFICATION")
print("=" * 70)

# Check required environment variables
REQUIRED_VARS = [
    ("GOOGLE_CLOUD_PROJECT", "Google Cloud Project ID"),
    ("GOOGLE_CLOUD_LOCATION", "Google Cloud Location"),
    ("TAVILY_API_KEY", "Tavily API Key"),
    ("NEWSAPI_KEY", "NewsAPI Key"),
    ("EMAIL_ADDRESS", "Email Address"),
    ("DATABASE_URL", "Database URL"),
    ("POSTGRES_USER", "PostgreSQL User"),
    ("POSTGRES_PASSWORD", "PostgreSQL Password"),
]

print("\n📋 CHECKING REQUIRED ENVIRONMENT VARIABLES:\n")

all_present = True
for var_name, var_desc in REQUIRED_VARS:
    value = os.getenv(var_name, "")
    if value:
        # Mask sensitive values
        if any(x in var_name.lower() for x in ["password", "key", "token"]):
            display_value = f"{value[:10]}...{value[-5:]}" if len(value) > 15 else "***"
        else:
            display_value = value
        print(f"  ✅ {var_desc:.<30} {display_value}")
    else:
        print(f"  ❌ {var_desc:.<30} MISSING")
        all_present = False

# Check optional variables
print("\n📋 OPTIONAL VARIABLES:\n")

optional_vars = [
    ("INSTAGRAM_API_TOKEN", "Instagram API Token"),
    ("TWITTER_API_KEY", "Twitter API Key"),
]

for var_name, var_desc in optional_vars:
    value = os.getenv(var_name, "")
    if value:
        display_value = f"{value[:10]}...{value[-5:]}" if len(value) > 15 else "***"
        print(f"  ✅ {var_desc:.<30} {display_value}")
    else:
        print(f"  ⚠️  {var_desc:.<30} NOT SET (optional)")

# Verify Vertex AI configuration
print("\n🔷 VERTEX AI CONFIGURATION:\n")

vertex_ai_project = os.getenv("GOOGLE_CLOUD_PROJECT")
vertex_ai_location = os.getenv("GOOGLE_CLOUD_LOCATION")
use_vertex_ai = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "").lower() == "true"

print(f"  Project:      {vertex_ai_project or 'NOT SET'}")
print(f"  Location:     {vertex_ai_location or 'NOT SET'}")
print(f"  Use Vertex:   {use_vertex_ai}")

# Test imports
print("\n🔍 CHECKING PYTHON DEPENDENCIES:\n")

try:
    from google.cloud import aiplatform
    print("  ✅ Google Cloud AI Platform")
except ImportError as e:
    print(f"  ❌ Google Cloud AI Platform: {e}")

try:
    import tavily
    print("  ✅ Tavily Python Client")
except ImportError as e:
    print(f"  ❌ Tavily Python Client: {e}")

try:
    import psycopg2
    print("  ✅ PostgreSQL Driver (psycopg2)")
except ImportError as e:
    print(f"  ❌ PostgreSQL Driver: {e}")

try:
    import pgvector.sqlalchemy
    print("  ✅ pgvector SQLAlchemy")
except ImportError as e:
    print(f"  ❌ pgvector SQLAlchemy: {e}")

try:
    import fastapi
    print("  ✅ FastAPI")
except ImportError as e:
    print(f"  ❌ FastAPI: {e}")

# Test database connection
print("\n🗄️  DATABASE CONNECTION:\n")

db_url = os.getenv("DATABASE_URL", "")
if db_url:
    try:
        import psycopg2
        from urllib.parse import urlparse

        # Parse database URL
        parsed = urlparse(db_url)

        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            user=parsed.username,
            password=parsed.password,
            database=parsed.path.lstrip("/"),
        )

        # Check for pgvector extension
        cursor = conn.cursor()
        cursor.execute("SELECT version FROM pg_extension WHERE extname='vector';")
        result = cursor.fetchone()

        if result:
            print(f"  ✅ PostgreSQL connected: {result[0]}")
        else:
            print("  ⚠️  pgvector extension not found")
            print("  Run: psql -U postgres -d narrativewatch -c 'CREATE EXTENSION IF NOT EXISTS vector;'")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"  ❌ Database connection failed: {e}")
        print(f"  URL: {db_url}")

# Summary
print("\n" + "=" * 70)

if all_present:
    print("✅ ALL REQUIRED VARIABLES SET - READY TO START!")
    print("\nNext steps:")
    print("  1. Ensure PostgreSQL is running")
    print("  2. Run: python -m uvicorn src.app:app --reload --port 8000")
    print("=" * 70)
    sys.exit(0)
else:
    print("❌ MISSING REQUIRED VARIABLES - CONFIGURATION INCOMPLETE")
    print("\nUpdate .env file with missing values and try again.")
    print("=" * 70)
    sys.exit(1)

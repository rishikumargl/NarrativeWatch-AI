"""Load .env file from parent directory"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"✓ Loaded environment from {env_path}")
else:
    print(f"! .env not found at {env_path}")

# Verify key variables are set
required_vars = [
    "GOOGLE_CLOUD_PROJECT",
    "NEWSAPI_KEY",
    "TAVILY_API_KEY",
]

print("\nConfiguration Status:")
for var in required_vars:
    value = os.getenv(var, "")
    if value:
        masked = f"{value[:10]}...{value[-5:]}" if len(value) > 15 else value
        print(f"  ✓ {var}: {masked}")
    else:
        print(f"  ! {var}: NOT SET")

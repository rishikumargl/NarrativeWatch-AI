# NarrativeWatch AI - Complete Verification Guide

## How to Know Everything is Working Properly

This guide walks you through comprehensive testing and verification to confirm all systems are operational.

---

## Prerequisites

Before testing, ensure:

```bash
# 1. Clone the repository
git clone https://github.com/rishikumargl/NarrativeWatch-AI.git
cd NarrativeWatch-AI

# 2. Create virtual environment
python3.10 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment variables
cp .env.example .env
# Edit .env with your API keys

# 5. Setup PostgreSQL (if not already running)
# Option A: Local installation
psql -U postgres -c "CREATE EXTENSION vector;"  # Install pgvector extension

# Option B: Docker
docker run -p 5432:5432 -e POSTGRES_PASSWORD=postgres pgvector/pgvector:latest

# NOTE: The database 'narrativewatch' will be created automatically on first run!
# No need to manually create it in pgAdmin
```

---

## Quick Start Verification (5 minutes)

### 1. Check Python Installation
```bash
python --version  # Should be 3.10+
```

### 2. Test Dependencies
```bash
python -c "import sqlalchemy; import pgvector; import vertexai; print('✅ All deps installed')"
```

### 3. Verify Database Connection
```bash
python -c "
from src.database.postgres_client import PostgresClient
client = PostgresClient()
print('✅ Database connected')
"
```

### 4. Test API Keys
```bash
python -c "
import os
keys = ['VERTEX_AI_PROJECT_ID', 'INSTAGRAM_ACCESS_TOKEN', 'TAVILY_API_KEY', 'DATABASE_URL']
missing = [k for k in keys if not os.getenv(k)]
if missing:
    print(f'❌ Missing: {missing}')
else:
    print('✅ All API keys configured')
"
```

---

## Unit Tests (10 minutes)

### Run All Tests
```bash
pytest tests/ -v --tb=short
```

### Expected Output
```
tests/test_database.py ✅ PASSED
tests/test_apis.py ✅ PASSED
tests/test_embeddings.py ✅ PASSED
tests/test_rag_pipeline.py ✅ PASSED
tests/test_agents.py ✅ PASSED
tests/test_orchestrator.py ✅ PASSED
tests/test_api.py ✅ PASSED
tests/test_integration_e2e.py ✅ PASSED

====== 100+ passed in X.XXs ======
```

### Check Test Coverage
```bash
pytest tests/ --cov=src --cov-report=term-missing

# Expected: 85%+ coverage
```

---

## Component Testing (Manual Verification)

### 1. Database Layer Test

```python
# test_database_manual.py
from src.database.postgres_client import PostgresClient
from src.database.models import InstagramPost
from datetime import datetime

# Initialize client
client = PostgresClient()

# Test connection
print("✅ Database connected")

# Create tables
client.create_all_tables()
print("✅ Tables created")

# Test pgvector extension
has_extension = client.check_pgvector_extension()
print(f"✅ pgvector extension: {has_extension}")

# Test session management
session = client.get_session()
post = InstagramPost(
    post_id="test_001",
    page_username="testuser",
    caption="Test post",
    posting_time=datetime.utcnow(),
)
session.add(post)
session.commit()
session.close()
print("✅ Database CRUD working")
```

### 2. Embedding Test

```python
# test_embeddings_manual.py
from src.utils.embedding_utils import get_embedding_client

client = get_embedding_client()

# Test single embedding
emb = client.embed_text("Hello world")
print(f"✅ Embedding shape: {len(emb)} dimensions")
assert len(emb) == 1536

# Test batch embedding
embs = client.embed_batch(["Text 1", "Text 2", "Text 3"])
print(f"✅ Batch embeddings: {len(embs)} texts")
assert len(embs) == 3

# Test similarity
sim = client.similarity(emb, embs[0])
print(f"✅ Similarity score: {sim:.2f}")
assert 0 <= sim <= 1
```

### 3. API Clients Test

```python
# test_apis_manual.py
from src.apis.tavily_api import TavilyAPI
from src.apis.instagram_api import InstagramAPI
from src.apis.llm_client import LLMClient

# Test Tavily
tavily = TavilyAPI()
results = tavily.search("climate change")
print(f"✅ Tavily search: {len(results)} results")

# Test Instagram API
instagram = InstagramAPI()
health = instagram.check_health()
print(f"✅ Instagram API: {health}")

# Test LLM
llm = LLMClient()
text = llm.generate("Hello, who are you?")
print(f"✅ LLM response: {text[:50]}...")
health = llm.check_health()
print(f"✅ LLM health: {health}")
```

### 4. RAG Pipeline Test

```python
# test_rag_manual.py
from src.database.rag_pipeline import get_rag_pipeline

pipeline = get_rag_pipeline()

# Test ingestion
post_id = pipeline.ingest_instagram_post(
    post_id="test_post_001",
    page_username="testuser",
    caption="This is a test post about AI and technology",
    hashtags=["#AI", "#technology"],
    likes=100,
    comments=10
)
print(f"✅ Post ingested: {post_id}")

# Test retrieval
from src.utils.embedding_utils import get_embedding_client
client = get_embedding_client()
query_emb = client.embed_text("AI and machine learning")
results = pipeline.search_similar_posts(query_emb, limit=5)
print(f"✅ Search returned: {len(results)} posts")

# Test stats
stats = pipeline.get_rag_stats()
print(f"✅ RAG stats: {stats}")
```

### 5. Orchestrator Test

```python
# test_orchestrator_manual.py
from src.agents.orchestrator import get_orchestrator
from src.agents.example_agents import get_example_agents

orchestrator = get_orchestrator()

# Register agents
bias_agent, bot_agent, misinformation_agent = get_example_agents()
orchestrator.register_bias_agent(bias_agent)
orchestrator.register_bot_agent(bot_agent)
orchestrator.register_misinformation_agent(misinformation_agent)
print("✅ Agents registered")

# Test analysis
analysis = orchestrator.analyze_post(
    post_id="test_123",
    page_username="testuser",
    caption="Buy followers cheap 100% real",
    hashtags=["#growth"],
    likes=5000,
    comments=5
)
print(f"✅ Analysis complete")
print(f"   Risk Level: {analysis.risk_level.value}")
print(f"   Risk Score: {analysis.risk_score:.2f}")
print(f"   Recommendations: {len(analysis.final_recommendations)}")
```

### 6. Flask Server Test

```bash
# Terminal 1: Start the server
python src/server.py

# Terminal 2: Test endpoints
# Health check
curl http://localhost:5000/health

# Expected response:
# {"status": "healthy", "components": {...}}

# Get statistics
curl http://localhost:5000/stats

# Expected response:
# {"status": "success", "data": {"posts": N, "pages": M, ...}}

# Analyze post
curl -X POST http://localhost:5000/analyze/post \
  -H "Content-Type: application/json" \
  -d '{
    "post_id": "test_123",
    "page_username": "testuser",
    "caption": "Test content",
    "hashtags": ["#test"],
    "likes": 100,
    "comments": 10
  }'

# Expected response:
# {"status": "success", "data": {...analysis results...}}
```

---

## Integration Testing (Complete Workflow)

### End-to-End Test Script

```bash
# test_e2e.sh

echo "Starting E2E Test..."

# 1. Check prerequisites
python -c "
import sys
try:
    from src.database.postgres_client import PostgresClient
    from src.utils.embedding_utils import get_embedding_client
    from src.agents.orchestrator import get_orchestrator
    from src.agents.example_agents import get_example_agents
    print('✅ All imports successful')
except Exception as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"

# 2. Test database
python -c "
from src.database.postgres_client import PostgresClient
client = PostgresClient()
client.check_pgvector_extension()
print('✅ Database ready')
"

# 3. Test embeddings
python -c "
from src.utils.embedding_utils import get_embedding_client
client = get_embedding_client()
emb = client.embed_text('test')
print(f'✅ Embeddings working ({len(emb)} dims)')
"

# 4. Test orchestrator
python -c "
from src.agents.orchestrator import get_orchestrator
from src.agents.example_agents import get_example_agents
orch = get_orchestrator()
ba, bo, mi = get_example_agents()
orch.register_bias_agent(ba)
orch.register_bot_agent(bo)
orch.register_misinformation_agent(mi)
analysis = orch.analyze_post(
    post_id='test_e2e',
    page_username='user',
    caption='Test post',
    hashtags=['#test'],
    likes=100,
    comments=10
)
print(f'✅ Analysis complete (Risk: {analysis.risk_level.value})')
"

# 5. Test API server
echo "✅ Starting Flask server..."
timeout 5 python src/server.py &
sleep 2
curl -s http://localhost:5000/health | grep -q "healthy" && echo "✅ API responding" || echo "❌ API not responding"
pkill -f "python src/server.py"

echo ""
echo "🎉 All E2E tests passed!"
```

Run it:
```bash
bash test_e2e.sh
```

---

## Performance Testing

### 1. Database Query Performance

```bash
# Should complete in < 100ms
time python -c "
from src.database.rag_pipeline import get_rag_pipeline
from src.utils.embedding_utils import get_embedding_client
pipeline = get_rag_pipeline()
client = get_embedding_client()
query_emb = client.embed_text('test query')
results = pipeline.search_similar_posts(query_emb, limit=10)
print(f'Found {len(results)} results')
"
```

### 2. Embedding Generation Performance

```bash
# Batch of 100 should complete in < 2 seconds
time python -c "
from src.utils.embedding_utils import get_embedding_client
client = get_embedding_client()
texts = [f'text {i}' for i in range(100)]
embs = client.embed_batch(texts)
print(f'Generated {len(embs)} embeddings')
"
```

### 3. API Response Time

```bash
# Single request should complete in < 30 seconds
time curl -X POST http://localhost:5000/analyze/post \
  -H "Content-Type: application/json" \
  -d '{"post_id":"test","page_username":"user","caption":"test","hashtags":["#test"]}'
```

---

## Health Checks

### Create a Health Check Script

```bash
# health_check.sh

#!/bin/bash

echo "🔍 System Health Check"
echo "===================="

# 1. Database
echo -n "Database: "
python -c "from src.database.postgres_client import PostgresClient; PostgresClient()" > /dev/null 2>&1 && echo "✅" || echo "❌"

# 2. Embeddings
echo -n "Embeddings: "
python -c "from src.utils.embedding_utils import get_embedding_client; get_embedding_client()" > /dev/null 2>&1 && echo "✅" || echo "❌"

# 3. Tavily API
echo -n "Tavily API: "
python -c "from src.apis.tavily_api import TavilyAPI; TavilyAPI().check_health()" > /dev/null 2>&1 && echo "✅" || echo "❌"

# 4. LLM
echo -n "LLM Client: "
python -c "from src.apis.llm_client import LLMClient; LLMClient().check_health()" > /dev/null 2>&1 && echo "✅" || echo "❌"

# 5. Orchestrator
echo -n "Orchestrator: "
python -c "from src.agents.orchestrator import get_orchestrator; get_orchestrator()" > /dev/null 2>&1 && echo "✅" || echo "❌"

# 6. Flask Server
echo -n "Flask Server: "
timeout 2 python src/server.py > /dev/null 2>&1 &
sleep 1
curl -s http://localhost:5000/health > /dev/null 2>&1 && echo "✅" || echo "❌"
pkill -f "python src/server.py" > /dev/null 2>&1

echo ""
echo "Health check complete!"
```

---

## Troubleshooting

### Issue: Database Connection Failed
```bash
# Check PostgreSQL is running
psql -U postgres -c "SELECT 1"

# Check pgvector is installed
psql -U postgres -d narrativewatch -c "SELECT * FROM pg_extension WHERE extname = 'vector';"

# Reinstall pgvector if needed
psql -U postgres -d narrativewatch -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### Issue: API Keys Missing
```bash
# Verify .env file exists
ls -la .env

# Verify all required variables
cat .env | grep -E "VERTEX_AI|INSTAGRAM|TAVILY|DATABASE"

# If missing, update .env
nano .env
```

### Issue: Tests Failing
```bash
# Run specific test for details
pytest tests/test_database.py -v -s

# Check test output for specific error
pytest tests/ -v --tb=long
```

### Issue: Flask Server Not Responding
```bash
# Check if port 5000 is in use
lsof -i :5000

# Kill existing process if needed
kill -9 <PID>

# Start fresh
python src/server.py
```

---

## Validation Checklist

Check these items to confirm everything works:

```
✅ Python Dependencies
   - [ ] pip list shows all packages from requirements.txt
   - [ ] All imports work without errors
   - [ ] No version conflicts

✅ Database
   - [ ] PostgreSQL running and accessible
   - [ ] pgvector extension installed
   - [ ] Tables created successfully
   - [ ] Can insert and query data
   - [ ] Connection pooling works

✅ Embeddings
   - [ ] Can generate single embeddings
   - [ ] Batch processing works
   - [ ] Cache is functioning
   - [ ] Similarity calculation correct
   - [ ] Performance < 2s per 100 texts

✅ APIs
   - [ ] Tavily API responding
   - [ ] Instagram API responding (mocked in tests)
   - [ ] LLM Client operational
   - [ ] Health checks passing
   - [ ] Error handling working

✅ RAG Pipeline
   - [ ] Can ingest posts
   - [ ] Can ingest pages
   - [ ] Can ingest patterns
   - [ ] Similarity search working
   - [ ] Statistics accurate

✅ Agents
   - [ ] Research Agent operational
   - [ ] RAG Agent operational
   - [ ] Orchestrator coordinating
   - [ ] Example agents loaded
   - [ ] Analysis completing

✅ Flask Server
   - [ ] Server starts without errors
   - [ ] /health endpoint responding
   - [ ] /stats endpoint responding
   - [ ] /analyze/post endpoint working
   - [ ] /analyze/page endpoint working
   - [ ] Error handling proper

✅ Tests
   - [ ] All unit tests passing
   - [ ] Integration tests passing
   - [ ] 85%+ coverage achieved
   - [ ] No warnings or errors
   - [ ] Performance acceptable
```

---

## Summary

Everything is working properly when:

1. ✅ All tests pass (`pytest tests/ -v`)
2. ✅ Database operations work (CRUD, embeddings, search)
3. ✅ APIs are responsive (health checks pass)
4. ✅ Flask server starts and responds to requests
5. ✅ End-to-end analysis completes successfully
6. ✅ Performance is within expected ranges
7. ✅ No errors or warnings in logs

---

**Status**: Ready for production deployment 🚀

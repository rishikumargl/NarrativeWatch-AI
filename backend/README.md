# NarrativeWatch AI Backend

Multi-Agent Social Media Intelligence Platform - Backend Service

## Structure

```
backend/
├── src/                      # Main Python package
│   ├── agents/               # 9 Specialized AI Agents
│   ├── apis/                 # External API integrations
│   ├── database/             # Database layer (PostgreSQL + pgvector)
│   ├── models/               # Pydantic request/response models
│   ├── utils/                # Utility functions
│   ├── workflow/             # Orchestration and state management
│   ├── app.py                # FastAPI application
│   ├── config.py             # Configuration
│   ├── logger.py             # Logging setup
│   └── __init__.py           # Package initialization
│
├── tests/                    # Test suite
├── scripts/                  # Utility scripts
├── requirements.txt          # Python dependencies
├── setup.py                  # Setup configuration
├── pyproject.toml            # Modern Python project config
└── README.md                 # This file
```

## Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL with pgvector extension
- API Keys: Vertex AI, Tavily, Instagram Graph API

### Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup environment
cp ../.env.example ../.env
# Edit ../.env with your API keys

# 3. Initialize database
python scripts/init_db.py

# 4. Run development server
python -m uvicorn src.app:app --reload --port 8000
```

### Environment Variables

```
VERTEX_AI_PROJECT=narrativewatch-ai
VERTEX_AI_LOCATION=us-central1
LLM_MODEL=gemini-2.5-pro
EMBEDDING_MODEL=text-embedding-005

TAVILY_API_KEY=***
INSTAGRAM_API_TOKEN=***
TWITTER_API_KEY=***

DATABASE_URL=postgresql://postgres:postgres@localhost:5432/narrativewatch
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=narrativewatch
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
API_RELOAD=False

APP_NAME=NarrativeWatch AI
APP_VERSION=1.0.0
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

## API Endpoints

### Health & Status
- `GET /health` - Health check
- `GET /stats` - System statistics
- `GET /workflow/{id}` - Workflow status

### Analysis
- `POST /analyze/post` - Analyze Instagram post
- `POST /analyze/page` - Analyze Instagram page
- `GET /results/{id}` - Get analysis results

### Search
- `POST /search/similar` - Search similar content

### Documentation
- `GET /docs` - Interactive API docs (Swagger UI)
- `GET /redoc` - ReDoc documentation

## Architecture

### Agents (9 Total)
1. **Orchestrator** - Workflow coordination
2. **Content Analyzer** - Content extraction and classification
3. **RAG Agent** - Retrieval-augmented generation
4. **Research Agent** - Web search and fact-checking
5. **Bias Detector** - Bias pattern identification
6. **Bot Detector** - Bot activity analysis
7. **Campaign Detector** - Coordinated campaign detection
8. **Synthesis Agent** - Result synthesis and reporting
9. **Reviewer Agent** - Quality assurance with reflection loop

### Database Models (5 SQLAlchemy ORM)
- **InstagramPost** - Social media posts with embeddings
- **InstagramPage** - User pages and profiles
- **Campaign** - Coordinated campaigns
- **BiasPattern** - Detected bias patterns
- **AnalysisResult** - Historical analysis results

### Technology Stack
- **Framework**: FastAPI
- **ORM**: SQLAlchemy 2.0+
- **Database**: PostgreSQL + pgvector
- **LLM**: Vertex AI / Gemini 2.5
- **Agents**: LangChain
- **Embeddings**: Vertex AI text-embedding-005 (1536-dim)
- **Web Search**: Tavily API

## Development

### Code Quality

```bash
# Format code
black src/ tests/

# Lint
flake8 src/ tests/ --max-line-length=120

# Type checking
mypy src/ --ignore-missing-imports

# Run tests
pytest tests/ -v --cov=src
```

### Running Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_agents.py -v

# With coverage
pytest tests/ -v --cov=src --cov-report=html
```

## Deployment

### Docker

```bash
docker-compose up -d
```

### Local Deployment

```bash
python -m uvicorn src.app:app --host 0.0.0.0 --port 8000 --workers 4
```

### Production Deployment

See [../docs/DEPLOYMENT_GUIDE.md](../docs/DEPLOYMENT_GUIDE.md)

## Import Structure

### Within Backend Package
Files in `backend/src/` use package-relative imports:

```python
# In backend/src/agents/orchestrator.py
from src.config import settings  # This works because src is part of package
from src.agents.base_agent import BaseAgent
```

### Running from Root Directory
When executing from project root:

```bash
python -m uvicorn src.app:app --reload
# This works because Python adds the current directory to sys.path
```

## Troubleshooting

### Import Errors
If you get `ModuleNotFoundError: No module named 'src'`:
1. Make sure you're running from the backend/ directory
2. Or install the package: `pip install -e .`
3. Or set `PYTHONPATH=.`

### Database Connection
If PostgreSQL connection fails:
1. Ensure PostgreSQL is running
2. Check DATABASE_URL in .env
3. Verify pgvector extension: `CREATE EXTENSION IF NOT EXISTS vector;`
4. Run: `python scripts/init_db.py`

### Agent Initialization
If agents fail to initialize:
1. Check all required API keys are set
2. Verify VERTEX_AI_PROJECT and VERTEX_AI_LOCATION
3. Run health check: `curl http://localhost:8000/health`

## Contributing

1. Create a feature branch
2. Make changes
3. Run tests and linting
4. Submit pull request

## License

Copyright 2026 NarrativeWatch Team

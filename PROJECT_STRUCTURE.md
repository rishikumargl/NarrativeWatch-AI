# NarrativeWatch AI - Complete Project Structure

## Overview
NarrativeWatch AI is a multi-agent social media intelligence platform that separates frontend and backend into distinct directory structures for clarity and maintainability.

---

## Directory Structure

```
NarrativeWatch-AI/
│
├── BACKEND/
│   ├── src/
│   │   ├── agents/                 # 9 Specialized AI Agents
│   │   │   ├── base_agent.py       # BaseAgent + AgentConfig classes
│   │   │   ├── orchestrator.py     # Orchestrator Agent
│   │   │   ├── content_analyzer.py # Content Analysis
│   │   │   ├── bias_detector.py    # Bias Detection
│   │   │   ├── bot_detector.py     # Bot Activity Detection
│   │   │   ├── campaign_detector.py# Campaign Detection
│   │   │   ├── research_agent.py   # Web Research via Tavily
│   │   │   ├── rag_agent.py        # RAG Analysis
│   │   │   ├── synthesis_agent.py  # Result Synthesis
│   │   │   └── reviewer_agent.py   # Quality Review + Reflection Loop
│   │   │
│   │   ├── apis/                   # External API Integrations
│   │   │   ├── llm_client.py       # Vertex AI / Gemini 2.5
│   │   │   ├── tavily_api.py       # Tavily Search Integration
│   │   │   ├── instagram_api.py    # Instagram Graph API
│   │   │   └── twitter_api.py      # Twitter API (Optional)
│   │   │
│   │   ├── database/               # Data Persistence Layer
│   │   │   ├── postgres_client.py  # PostgreSQL Connection + Pooling
│   │   │   ├── models.py           # SQLAlchemy ORM Models (5 models)
│   │   │   │   ├── InstagramPost   # Social media posts
│   │   │   │   ├── InstagramPage   # User pages
│   │   │   │   ├── Campaign        # Coordinated campaigns
│   │   │   │   ├── BiasPattern     # Detected bias patterns
│   │   │   │   └── AnalysisResult  # Historical results
│   │   │   └── rag_pipeline.py     # RAG with pgvector
│   │   │
│   │   ├── models/                 # API Data Models
│   │   │   ├── request.py          # Pydantic request models
│   │   │   └── response.py         # Pydantic response models
│   │   │
│   │   ├── utils/                  # Utility Functions
│   │   │   ├── embedding_utils.py  # Vertex AI Embeddings (1536-dim)
│   │   │   ├── text_processor.py   # NLP Preprocessing
│   │   │   ├── scoring.py          # Trust Score Calculation
│   │   │   └── validators.py       # Input Validation
│   │   │
│   │   ├── workflow/               # Orchestration & Workflow
│   │   │   ├── orchestration.py    # Workflow Engine
│   │   │   ├── state_manager.py    # State Management
│   │   │   └── reflection_loop.py  # Quality Assurance Loop
│   │   │
│   │   ├── app.py                  # FastAPI Application
│   │   ├── config.py               # Configuration Management
│   │   ├── logger.py               # Logging Setup
│   │   └── __init__.py             # Package initialization
│   │
│   ├── tests/                      # Backend Test Suite
│   │   ├── test_agents.py          # Agent unit tests
│   │   ├── test_apis.py            # API integration tests
│   │   ├── test_rag.py             # RAG pipeline tests
│   │   ├── test_integration.py     # E2E workflow tests
│   │   └── conftest.py             # Pytest configuration
│   │
│   ├── scripts/                    # Utility Scripts
│   │   ├── init_db.py              # Database initialization
│   │   └── setup.sh                # Environment setup
│   │
│   ├── requirements.txt            # Python Dependencies (47 packages)
│   ├── .env.example                # Environment Variables Template
│   └── docker-compose.yml          # Docker Composition
│
├── FRONTEND/
│   ├── public/                     # Static Assets
│   │   ├── index.html              # HTML entry point
│   │   └── favicon.ico             # Favicon
│   │
│   ├── src/
│   │   ├── components/             # Reusable React Components
│   │   │   ├── AnalysisForm.jsx    # Post/Page Analysis Form
│   │   │   ├── AnalysisForm.css    # Form Styling
│   │   │   ├── ResultsDisplay.jsx  # Analysis Results Display
│   │   │   ├── ResultsDisplay.css  # Results Styling
│   │   │   ├── LoadingSpinner.jsx  # Loading Indicator
│   │   │   ├── LoadingSpinner.css  # Spinner Styling
│   │   │   └── Dashboard.jsx       # Home Dashboard
│   │   │
│   │   ├── pages/                  # Page Components (for routing)
│   │   │   ├── Home.jsx            # Home page
│   │   │   ├── Analysis.jsx        # Analysis page
│   │   │   └── Settings.jsx        # Settings page
│   │   │
│   │   ├── styles/                 # Global Stylesheets
│   │   │   ├── App.css             # Application styles
│   │   │   ├── index.css           # Global styles
│   │   │   └── responsive.css      # Responsive design
│   │   │
│   │   ├── utils/                  # Frontend Utilities
│   │   │   ├── api.js              # API client utilities
│   │   │   └── helpers.js          # Helper functions
│   │   │
│   │   ├── App.jsx                 # Root Application Component
│   │   └── main.jsx                # React Entry Point
│   │
│   ├── package.json                # Node Dependencies
│   ├── package-lock.json           # Dependency Lock File
│   ├── vite.config.js              # Vite Configuration
│   ├── .eslintrc.json              # ESLint Configuration
│   ├── .gitignore                  # Git Ignore Rules
│   └── .vite/                      # Vite Cache/Build
│
├── notebooks/                      # Jupyter Notebooks
│   └── demo.ipynb                  # Demo & Testing Notebook
│
├── docs/                           # Documentation
│   ├── API_REFERENCE.md            # API Documentation
│   ├── SETUP_GUIDE.md              # Setup Instructions
│   ├── DEPLOYMENT_GUIDE.md         # Deployment Procedures
│   ├── ARCHITECTURE.md             # System Architecture
│   ├── AGENTS.md                   # Agent Specifications
│   └── FRONTEND_GUIDE.md           # Frontend Development
│
├── .gitignore                      # Git Ignore (root)
├── .env.example                    # Root Environment Template
├── README.md                       # Project Overview
├── docker-compose.yml              # Docker Composition
├── requirements.txt                # Root Python Requirements
└── PROJECT_STRUCTURE.md            # This File
```

---

## Backend Architecture Details

### Agents (9 Total)

1. **Orchestrator Agent** - Coordinates workflow and manages state
2. **Content Analyzer Agent** - Extracts and classifies content
3. **RAG Agent** - Retrieval-augmented generation analysis
4. **Research Agent** - Web search via Tavily API
5. **Bias Detector Agent** - Identifies bias patterns
6. **Bot Detector Agent** - Detects bot activity
7. **Campaign Detector Agent** - Identifies coordinated campaigns
8. **Synthesis Agent** - Combines findings into reports
9. **Reviewer Agent** - Quality assurance with reflection loop

### Database Models (5 SQLAlchemy ORM Models)

- **InstagramPost** - Social media posts with embeddings
- **InstagramPage** - User profiles and metadata
- **Campaign** - Coordinated campaigns
- **BiasPattern** - Detected bias patterns
- **AnalysisResult** - Historical analysis results

### Technology Stack

**Backend:**
- Python 3.10+
- FastAPI (REST API)
- SQLAlchemy 2.0+ (ORM)
- PostgreSQL + pgvector (Vector DB)
- LangChain (Agent Framework)
- Vertex AI / Gemini 2.5 (LLM)
- Tavily (Web Search)

**Frontend:**
- React 18.2+
- Vite (Build Tool)
- React Router (Routing)
- Axios (HTTP Client)

---

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

---

## Environment Configuration

Required environment variables (see `.env.example`):

```
# LLM Configuration
VERTEX_AI_PROJECT=narrativewatch-ai
VERTEX_AI_LOCATION=us-central1
LLM_MODEL=gemini-2.5-pro
EMBEDDING_MODEL=text-embedding-005

# API Keys
TAVILY_API_KEY=***
INSTAGRAM_API_TOKEN=***
TWITTER_API_KEY=***

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/narrativewatch
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=narrativewatch

# API Server
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
API_RELOAD=False

# Application
APP_NAME=NarrativeWatch AI
APP_VERSION=1.0.0
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

---

## Development Workflow

### Backend Development
```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your API keys

# Run database initialization
python scripts/init_db.py

# Start development server
python -m uvicorn src.app:app --reload

# Run tests
pytest tests/ -v

# Code quality checks
mypy src/ --ignore-missing-imports
flake8 src/ --max-line-length=120
black src/ --check
```

### Frontend Development
```bash
# Install dependencies
cd frontend
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Run linter
npm run lint

# Format code
npm run format
```

---

## Build & Deployment

### Docker Deployment
```bash
docker-compose up -d
```

### Local Deployment
```bash
# Terminal 1: Backend
python -m uvicorn src.app:app --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend && npm run dev
```

Access at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Key Files & Their Purposes

| File | Purpose | Status |
|------|---------|--------|
| `src/app.py` | FastAPI application | ✅ Production |
| `src/config.py` | Configuration management | ✅ Production |
| `src/agents/orchestrator.py` | Main orchestration | ✅ Production |
| `src/database/models.py` | ORM models | ✅ Production |
| `src/database/rag_pipeline.py` | RAG implementation | ✅ Production |
| `src/utils/embedding_utils.py` | Embedding service | ✅ Production |
| `frontend/src/App.jsx` | React root component | ✅ Production |
| `frontend/src/components/` | React components | ✅ Production |

---

## Merge History

All code from team members (Member 1-4) has been merged successfully:
- ✅ Devlop2 branch (base integration)
- ✅ feature/ml-nlp-agents (Member 3)
- ✅ feature/data-eng-agents (Member 4)  
- ✅ feature/frontend-api-deployment (Member 5)

**Result:** Clean merge with NO CONFLICTS

---

## Ready for Deployment ✅

- Backend: Production-ready with all critical issues fixed
- Frontend: Complete React application structure
- Database: PostgreSQL + pgvector configured
- API: FastAPI with proper routing and error handling
- Tests: Comprehensive test suite ready
- Documentation: Complete setup and deployment guides


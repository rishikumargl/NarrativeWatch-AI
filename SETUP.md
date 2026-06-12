# NarrativeWatch AI - Setup Guide

**Project Structure:** Backend (Python/FastAPI) + Frontend (React/Vite)  
**LLM:** Claude API  
**Database:** PostgreSQL + pgvector  
**News Source:** NewsAPI

---

## Quick Start (5 minutes)

### 1. Install PostgreSQL

```bash
# Windows: Download from https://www.postgresql.org/download/windows/
# macOS: brew install postgresql
# Linux: sudo apt-get install postgresql postgresql-contrib
```

### 2. Enable pgvector Extension

```bash
# Connect to PostgreSQL
psql -U postgres

# In psql shell:
CREATE EXTENSION IF NOT EXISTS vector;
\q
```

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Update .env with your API keys (already has NewsAPI & Tavily)
# Add your CLAUDE_API_KEY to .env

# Initialize database
python scripts/init_db.py

# Start backend
python start_backend.py
# Or: uvicorn src.app:app --reload
```

Backend runs on: **http://localhost:8000**  
API Docs: **http://localhost:8000/docs**

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs on: **http://localhost:5173**

---

## Project Structure

```
NarrativeWatch AI/
├── backend/                      # Python FastAPI backend
│   ├── src/
│   │   ├── agents/              # All 9 agents
│   │   ├── apis/                # NewsAPI, Tavily, Claude clients
│   │   ├── database/            # PostgreSQL + pgvector models
│   │   ├── workflow/            # Orchestration logic
│   │   ├── app.py               # FastAPI application
│   │   └── config.py            # Configuration
│   ├── requirements.txt
│   ├── .env.example
│   └── start_backend.py
│
├── frontend/                     # React + Vite frontend
│   ├── src/
│   │   ├── components/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── LLD_AND_TEAM_PLAN.md         # Full technical design
├── README.md                     # Project overview
└── .env                         # Environment variables
```

---

## Key Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **LLM** | Claude API | Intelligence & analysis |
| **Framework** | FastAPI | Backend API |
| **Database** | PostgreSQL + pgvector | Storage + Vector search |
| **APIs** | NewsAPI, Tavily | News & fact-checking |
| **Frontend** | React + Vite | User interface |

---

## API Endpoints

### News Analysis
- `POST /api/v1/analyze/article` - Analyze single article
- `POST /api/v1/analyze/topic` - Analyze topic across articles
- `POST /api/v1/articles/search` - Search articles by query

### Data
- `GET /api/v1/articles/recent` - Get recent articles
- `GET /api/v1/narratives` - Get narrative clusters
- `GET /api/v1/health` - System status

### System
- `GET /docs` - API documentation (Swagger UI)
- `GET /redoc` - ReDoc documentation

---

## Database Schema

### NewsArticle
- article_id, title, source, author, url
- content, summary, published_at
- **content_embedding** (Vector 1536) - for semantic search
- bias_score, trust_score, sentiment_score, credibility_score
- key_claims, entities, topics, narrative_tags

### NarrativeCluster
- cluster_id, narrative_theme, description
- articles_count, article_ids
- **cluster_embedding** (Vector 1536)
- evidence_strength, confidence_score

### BiasPattern
- pattern_id, bias_type, description, indicators
- **pattern_embedding** (Vector 1536)
- confidence_score

### FactCheckResult
- check_id, article_id, claim
- fact_check_result (True/False/Disputed/Unknown)
- evidence, confidence_score

---

## Environment Variables

Essential:
```
CLAUDE_API_KEY=your_key_here
NEWSAPI_KEY=your_key_here
TAVILY_API_KEY=your_key_here
DATABASE_URL=postgresql://postgres:password@localhost:5432/narrativewatch
```

---

## Development Workflow

### 1. Backend Development
```bash
cd backend
source venv/bin/activate
# Make changes to src/
# Changes auto-reload with --reload flag
```

### 2. Frontend Development
```bash
cd frontend
# Changes auto-reload with Vite dev server
```

### 3. Running Both
```bash
# Terminal 1: Backend
cd backend && python start_backend.py

# Terminal 2: Frontend
cd frontend && npm run dev

# Open http://localhost:5173
```

---

## Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
pytest tests/ --cov=src/  # With coverage
```

### Frontend Tests
```bash
cd frontend
npm test
```

---

## Troubleshooting

### PostgreSQL Connection Error
```bash
# Check if PostgreSQL is running
pg_isrunning  # or check Services on Windows

# Verify database exists
psql -U postgres -c "SELECT datname FROM pg_database WHERE datname='narrativewatch';"

# Create database if missing
createdb -U postgres narrativewatch
```

### pgvector Extension Error
```bash
# Install pgvector extension
psql -U postgres -d narrativewatch -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### API Key Errors
- Verify keys are in `.env` file
- Check no spaces around `=` sign
- Reload Python process after changing `.env`

### Port Already in Use
```bash
# Change API_PORT in .env or run on different port:
API_PORT=8001 python start_backend.py
```

---

## Next Steps

1. **Add your API keys** to `.env`
2. **Start PostgreSQL** and create database
3. **Run backend** - verify API docs work
4. **Run frontend** - verify it loads
5. **Try analysis** - search for articles and analyze them
6. **Build agents** - implement missing agent logic

---

## Resources

- **LLD**: See [LLD_AND_TEAM_PLAN.md](LLD_AND_TEAM_PLAN.md) for full design
- **Claude API**: https://claude.ai/
- **NewsAPI**: https://newsapi.org/
- **Tavily**: https://tavily.com/
- **FastAPI**: https://fastapi.tiangolo.com/
- **PostgreSQL**: https://www.postgresql.org/

---

## Questions?

Refer to:
- `backend/README.md` - Backend details
- `frontend/README.md` - Frontend details (if exists)
- `LLD_AND_TEAM_PLAN.md` - Architecture & design
- API Docs: http://localhost:8000/docs

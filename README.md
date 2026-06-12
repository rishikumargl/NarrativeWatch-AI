# NarrativeWatch AI

**Multi-Agent Social Media Intelligence Platform**  
*Detecting Misleading Content, Emotional Manipulation, Bias, and Coordinated Influence Campaigns on Instagram*

---

## 🎯 Project Overview

NarrativeWatch AI is a sophisticated agentic application that analyzes Instagram pages and posts to detect:

- 🔴 **Misleading Content** - False claims, misinformation
- 😡 **Emotional Manipulation** - Sensationalism, fear-mongering
- ⚖️ **Bias** - Political, gender, ideological, religious bias
- 🤖 **Bot Activity** - Inauthentic engagement, coordinated accounts
- 🕸️ **Influence Campaigns** - Coordinated narrative manipulation across pages
- 📊 **Trust Score** - Evidence-based trust rating (0-100)

Built with **LangChain**, **Vertex AI (Gemini 2.5)**, **PostgreSQL + pgvector**, and **Tavily Search** for comprehensive analysis.

---

## ✨ Features

### 9-Agent Orchestrated System
- **Orchestrator Agent** - Coordinates workflow and task routing
- **Content Analyzer Agent** - Extracts post features and narrative themes
- **RAG Agent** - Retrieves similar historical content from vector DB
- **Research Agent** - Gathers external information via web search
- **Bias Detector Agent** - Identifies multiple types of bias
- **Bot Detector Agent** - Analyzes engagement authenticity
- **Campaign Detector Agent** - Finds coordinated influence campaigns
- **Synthesis Agent** - Combines findings into coherent reports
- **Reviewer Agent** - Quality assurance with reflection loop

### Advanced Capabilities
- 🔄 **Reflection Loop** - Auto-improves analysis via feedback (max 3 iterations)
- 🎯 **Vector RAG** - PostgreSQL pgvector-powered historical pattern matching
- 🔍 **Multi-API Integration** - Instagram, Twitter, Tavily Search, fact-checking APIs
- 📈 **Trust Score Algorithm** - Evidence-based scoring system
- 💾 **Persistent Memory** - Stores analyses for improvement over time
- 🚀 **Fast Inference** - Gemini 2.5 (20x cheaper than alternatives)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Google Cloud Project (for Vertex AI)
- Instagram Graph API credentials
- Tavily API key

### Setup (5 minutes)

```bash
# 1. Clone repository
git clone <repo-url>
cd NarrativeWatch-AI

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your API keys (see below)

# 5. Initialize database
python scripts/init_db.py

# 6. Run tests
pytest tests/ -v

# 7. Start the API
python -m uvicorn src.app:app --reload
```

### API Configuration

Get these API keys and add to `.env`:

```bash
# Google Cloud (for Vertex AI & Gemini 2.5)
VERTEX_AI_PROJECT_ID=your-gcp-project-id
VERTEX_AI_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# Instagram Data Access
INSTAGRAM_ACCESS_TOKEN=your-instagram-token

# External Search
TAVILY_API_KEY=your-tavily-key

# Backup LLM (optional)
CLAUDE_API_KEY=your-claude-key

# Embedding Model
EMBEDDING_MODEL=text-embedding-005  # Vertex AI
```

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────┐
│          User Request (Instagram Page/Post)             │
└────────────────────┬────────────────────────────────────┘
                     ↓
            ┌────────────────────┐
            │  ORCHESTRATOR      │ (Routes & Coordinates)
            └────────┬───────────┘
                     ↓
     ┌───────────────┼────────────────────┬──────────────┐
     │               │                    │              │
  ┌──▼──┐  ┌────────▼──────┐  ┌─────────▼──┐  ┌───────▼──┐
  │CON  │  │RAG (Weaviate)│  │ RESEARCH   │  │  BIAS    │
  │TENT │──│              │──│ (Tavily)   │──│ DETECTOR │
  │ANAL │  │              │  │            │  │          │
  └──┬──┘  └────────┬──────┘  └─────────┬──┘  └───────┬──┘
     │               │                   │            │
     └───┬───────────┴───────┬──────────┘            │
         │                   │                       │
   ┌─────▼──────┐  ┌────────▼───┐      ┌────────────▼───┐
   │ BOT        │  │ CAMPAIGN   │      │               │
   │ DETECTOR   │  │ DETECTOR   │      │  SYNTHESIS    │
   │            │  │            │      │               │
   └─────┬──────┘  └────────┬───┘      └────────┬───────┘
         │                  │                   │
         └──────────┬───────┴───────────┬───────┘
                    │                   │
             ┌──────▼───────────────────▼──┐
             │   REVIEWER AGENT            │
             │   + REFLECTION LOOP         │
             │   (Max 3 retries)           │
             └──────┬──────────────────────┘
                    │
        ┌───────────▼──────────┐
        │  TRUST SCORE + REPORT│
        │  (0-100 score)       │
        │  Evidence + Insights │
        └──────────────────────┘
```

### Technology Stack

| Component | Technology | Notes |
|-----------|-----------|-------|
| **Agent Framework** | LangChain 0.1+ | Industry standard orchestration |
| **LLM** | Vertex AI / Gemini 2.5 | Primary (fast & cheap); Claude backup |
| **Embeddings** | Vertex AI text-embedding-005 | For RAG & similarity search |
| **Vector DB** | PostgreSQL + pgvector | RAG storage, retrieval, pattern matching |
| **Relational DB** | PostgreSQL | Structured data, metadata, analytics |
| **Web Search** | Tavily API | External fact-finding & research |
| **Data APIs** | Instagram Graph, Twitter, etc. | Content ingestion |
| **API Service** | FastAPI | REST endpoints with Swagger docs |
| **Container** | Docker | Production deployment |

---

## 📁 Project Structure

```
NarrativeWatch-AI/
├── README.md                          ← You are here
├── LLD_AND_TEAM_PLAN.md              ← Complete design document (150+ pages)
├── IMPLEMENTATION_CHECKLIST.md        ← Weekly task breakdown
├── VECTOR_DB_SCHEMA.md               ← Database schema design
├── VERTEX_AI_INTEGRATION.md          ← Vertex AI setup & usage
├── QUICK_START_GUIDE.md              ← 5-min team onboarding
├── PROJECT_OVERVIEW.md               ← Project governance & status
│
├── .env.example                       ← Copy to .env and configure
├── requirements.txt                   ← All Python dependencies
├── setup.sh                           ← One-command local setup
├── docker-compose.yml                 ← Docker stack for testing
├── Dockerfile                         ← Container image definition
│
├── src/
│   ├── agents/
│   │   ├── base_agent.py             ← Base class for all agents
│   │   ├── orchestrator.py           ← Orchestrator Agent (#1)
│   │   ├── content_analyzer.py       ← Content Analyzer Agent (#2)
│   │   ├── rag_agent.py              ← RAG Agent (#3)
│   │   ├── research_agent.py         ← Research Agent (#4)
│   │   ├── bias_detector.py          ← Bias Detector Agent (#5)
│   │   ├── bot_detector.py           ← Bot Detector Agent (#6)
│   │   ├── campaign_detector.py      ← Campaign Detector Agent (#7)
│   │   ├── synthesis_agent.py        ← Synthesis Agent (#8)
│   │   └── reviewer_agent.py         ← Reviewer Agent (#9)
│   │
│   ├── apis/
│   │   ├── llm_client.py             ← Multi-provider LLM (Vertex/Claude/OpenAI)
│   │   ├── tavily_api.py             ← Tavily search wrapper
│   │   ├── instagram_api.py          ← Instagram Graph API client
│   │   ├── twitter_api.py            ← Twitter API client
│   │   └── fact_check_api.py         ← Fact-checking APIs
│   │
│   ├── database/
│   │   ├── postgres_client.py        ← PostgreSQL connection
│   │   ├── models.py                 ← SQLAlchemy ORM models
│   │   └── rag_pipeline.py           ← Embeddings & pgvector retrieval
│   │
│   ├── models/
│   │   ├── request.py                ← Input models (Pydantic)
│   │   ├── response.py               ← Output models
│   │   └── enums.py                  ← Enumerations
│   │
│   ├── utils/
│   │   ├── text_processor.py         ← NLP preprocessing
│   │   ├── embedding_utils.py        ← Embedding generation
│   │   ├── scoring.py                ← Trust score calculation
│   │   └── validators.py             ← Input validation
│   │
│   ├── workflow/
│   │   ├── orchestration.py          ← Main workflow logic
│   │   ├── reflection_loop.py        ← Reviewer feedback loop
│   │   └── state_manager.py          ← State management
│   │
│   ├── config.py                     ← Configuration management
│   ├── logger.py                     ← Logging setup
│   └── app.py                        ← FastAPI application
│
├── tests/
│   ├── test_agents.py                ← Agent unit tests
│   ├── test_apis.py                  ← API integration tests
│   ├── test_rag.py                   ← RAG pipeline tests
│   └── test_integration.py           ← End-to-end tests
│
├── notebooks/
│   ├── exploration.ipynb             ← Data exploration
│   └── testing.ipynb                 ← Component testing
│
├── docs/
│   ├── API_REFERENCE.md              ← API documentation
│   ├── SETUP_GUIDE.md                ← Detailed setup
│   └── DEPLOYMENT.md                 ← Production deployment
│
└── scripts/
    └── init_db.py                    ← Database initialization
```

---

## 🔌 API Endpoints

```bash
# Health Check
GET /health
# Response: {"status": "ok", "timestamp": "2026-06-12T10:30:00Z"}

# Analyze Instagram Page
POST /analyze/page
# Request:
{
  "username": "instagram_page_name",
  "include_posts": true,
  "num_posts": 20
}
# Response:
{
  "pageId": "123456",
  "username": "instagram_page_name",
  "trustScore": 35,
  "riskLevel": "high",
  "detectedIssues": ["misleading_content", "bot_activity"],
  "report": "...",
  "evidence": [...]
}

# Analyze Single Post
POST /analyze/post
# Request:
{
  "postUrl": "https://instagram.com/p/ABC123DEF456/",
  "includeContext": true
}
# Response:
{
  "postId": "ABC123DEF456",
  "trustScore": 42,
  "findings": {...}
}

# Get Analysis Results
GET /results/{resultId}
# Returns cached analysis

# Search Similar Content
POST /search/similar
# Find similar posts/campaigns in vector DB
```

See [docs/API_REFERENCE.md](docs/API_REFERENCE.md) for complete API documentation.

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_agents.py -v

# Run with debug output
pytest tests/ -vv -s
```

**Coverage Goal:** 80%+ across all modules

---

## 🐳 Docker Deployment

```bash
# Build image
docker build -t narrativewatch-ai:latest .

# Run locally
docker run -p 8000:8000 \
  -e VERTEX_AI_PROJECT_ID=your-project \
  -e VERTEX_AI_LOCATION=us-central1 \
  narrativewatch-ai:latest

# Or use docker-compose (includes PostgreSQL + pgvector)
docker-compose up -d
# Access API at http://localhost:8000
# PostgreSQL at localhost:5432
```

---

## 📚 Documentation

- **[LLD_AND_TEAM_PLAN.md](LLD_AND_TEAM_PLAN.md)** - Complete design & architecture (150+ pages)
- **[VECTOR_DB_SCHEMA.md](VECTOR_DB_SCHEMA.md)** - Weaviate schema & RAG design
- **[VERTEX_AI_INTEGRATION.md](VERTEX_AI_INTEGRATION.md)** - Gemini 2.5 setup
- **[QUICK_START_GUIDE.md](QUICK_START_GUIDE.md)** - Team onboarding (5 min)
- **[IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md)** - Weekly tasks
- **[docs/API_REFERENCE.md](docs/API_REFERENCE.md)** - REST API docs
- **[docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md)** - Detailed setup instructions
- **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** - Production deployment

---

## 🎓 Learning Resources

- **LangChain:** https://python.langchain.com/docs/
- **Vertex AI:** https://cloud.google.com/vertex-ai/docs
- **Weaviate:** https://weaviate.io/developers/weaviate/
- **Tavily:** https://tavily.com/
- **FastAPI:** https://fastapi.tiangolo.com/

---

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes and write tests
3. Commit with clear messages: `git commit -m "Clear description"`
4. Push to remote: `git push origin feature/your-feature`
5. Create Pull Request for review
6. Address feedback and merge

**Code Quality Standards:**
- Python PEP 8 (use `black` formatter)
- Type hints on all functions
- Unit tests (80%+ coverage)
- Docstrings for all modules/functions
- No hardcoded values (use `.env`)

---

## 📊 Performance

**Typical Analysis Time:**
- Single post analysis: 5-10 seconds
- Full page analysis (20 posts): 30-60 seconds
- Campaign detection (10 pages): 60-120 seconds

**Cost per Analysis (Vertex AI):**
- Single post: ~$0.00004
- Full page: ~$0.0004
- Campaign: ~$0.0005

**Comparison:**
- Claude: 20-50x more expensive
- GPT-4o: 25-50x more expensive

---

## 🔒 Security

- API keys stored in `.env` (never committed)
- Input validation on all endpoints
- SQL injection protection (using Pydantic models)
- Rate limiting on external APIs
- Secure communication (HTTPS in production)
- No sensitive data logged

---

## 📈 Roadmap

**V1.1 (2 weeks post-launch)**
- Multi-language support
- Real-time alert notifications
- Advanced filtering & search

**V1.2 (1 month post-launch)**
- Mobile app (iOS/Android)
- Advanced dashboard & visualizations
- API authentication & rate limiting

**V2.0 (3 months post-launch)**
- Multi-platform support (TikTok, YouTube, Twitter)
- ML model fine-tuning
- Enterprise analytics dashboard
- Licensing model for organizations

---

## 📝 License

This project is developed for educational and research purposes as part of the FDE Team Activity requirement.

---

## 👥 Team

- **Project Lead:** Rohan Urmude
- **Backend Specialist:** [Team Member]
- **ML/NLP Specialist:** [Team Member]
- **Senior Data Engineer:** [Team Member]
- **Frontend/DevOps:** [Team Member] (Optional)
- **QA Lead:** [Team Member] (Optional)

---

## ❓ FAQ

**Q: Why Vertex AI over Claude/GPT-4?**  
A: 20-50x cost savings while maintaining high quality. Gemini 2.5 has 1M token context and excellent tool support.

**Q: Can I switch to Claude later?**  
A: Yes! The LLMClient supports both. Just change `LLM_PROVIDER` in `.env`.

**Q: How does the reflection loop work?**  
A: Reviewer agent checks synthesis quality. If issues found, synthesis agent regenerates with feedback (max 3 tries).

**Q: What's in the vector DB?**  
A: Historical posts, pages, campaigns, bias patterns, analysis results. Used for RAG retrieval.

**Q: How long does a full page analysis take?**  
A: 30-60 seconds including RAG retrieval, API calls, and multi-agent analysis.

**Q: Can I run this locally?**  
A: Yes! Use `docker-compose up` to start Weaviate locally. Just needs Google Cloud credentials.

---

## 📞 Support

- **Questions?** See [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md#questions)
- **Bug reports?** Create GitHub Issue
- **Setup issues?** Check [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md)
- **Architecture questions?** See [LLD_AND_TEAM_PLAN.md](LLD_AND_TEAM_PLAN.md)

---

## 🚀 Getting Started Now

1. **Read:** [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md) (5 minutes)
2. **Setup:** Follow "Quick Start" section above (5 minutes)
3. **Test:** Run `pytest tests/ -v` (2 minutes)
4. **Learn:** Read [LLD_AND_TEAM_PLAN.md](LLD_AND_TEAM_PLAN.md) (45 minutes)
5. **Code:** Check [IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md)

---

**Created:** 2026-06-12  
**Status:** Ready for Development  
**Next Step:** Distribute to team and begin Phase 1 (Infrastructure Setup)

🚀 **Let's build something amazing!**


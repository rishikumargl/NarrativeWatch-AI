# 🚀 START HERE - NarrativeWatch AI

## Welcome! Here's how to run the application end-to-end.

---

## 📋 Choose Your Path

### **Option A: I want to start running the app RIGHT NOW** ⚡
👉 Open: [RUN_INSTRUCTIONS.txt](RUN_INSTRUCTIONS.txt)
- Quick 5-step guide
- No fluff, just commands
- Takes ~10 minutes to get running

### **Option B: I want detailed setup instructions** 📖
👉 Open: [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md)
- 500+ lines of comprehensive setup
- Screenshots and examples
- Troubleshooting for each step
- Database management section

### **Option C: I want to know if everything is ready** ✅
👉 Open: [DEPLOYMENT_READY.md](DEPLOYMENT_READY.md)
- Complete status checklist
- Architecture overview
- API endpoints reference
- Feature completeness chart

---

## ⚡ Ultra-Quick Summary

**What you need:**
1. PostgreSQL 15+ with pgvector extension
2. Python 3.10+
3. Node.js 18+
4. 4 API keys (get from: Google Cloud, Tavily, Meta, Twitter)

**5 Steps to running:**
```bash
# 1. Setup PostgreSQL
createdb narrativewatch
psql narrativewatch -c "CREATE EXTENSION IF NOT EXISTS vector;"

# 2. Create .env file
cp .env.example .env
# Edit with your API keys

# 3. Start backend
cd backend
pip install -r requirements.txt
python -m uvicorn src.app:app --reload --port 8000

# 4. Start frontend (new terminal)
cd frontend
npm install
npm run dev

# 5. Access application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

---

## 📚 Documentation Index

| Document | Purpose | When to Read |
|----------|---------|--------------|
| **START_HERE.md** | This file - navigation guide | First |
| **RUN_INSTRUCTIONS.txt** | Quick reference guide (220 lines) | For quick start |
| **QUICK_START_GUIDE.md** | Comprehensive setup guide (529 lines) | For detailed instructions |
| **DEPLOYMENT_READY.md** | Status checklist & architecture | For understanding readiness |
| **README.md** | Project overview | For context |
| **PROJECT_STRUCTURE.md** | File organization | For finding code |

---

## 🎯 What's Ready

### Backend ✅
- FastAPI with 6 API endpoints
- 9 specialized agents (all integrated)
- PostgreSQL with pgvector support
- Authentication & error handling
- Logging & monitoring
- Background task processing

### Frontend ✅
- React 18.2 with Vite
- Dashboard with statistics
- Analysis forms (post & page)
- Results display
- API proxy to backend

### Database ✅
- PostgreSQL 15+
- pgvector extension
- Auto-schema creation
- Connection pooling (10+20)
- Vector embeddings (1536-dim)

### Documentation ✅
- Setup guides (2 files)
- Quick reference (1 file)
- API documentation (auto-generated at /docs)
- Troubleshooting guides

---

## 🔑 Required API Keys

Before starting, get these 4 keys:

| Key | Service | Where to Get |
|-----|---------|-------------|
| `VERTEX_AI_PROJECT` | Google Cloud | https://console.cloud.google.com/ |
| `TAVILY_API_KEY` | Tavily | https://www.tavily.com/ |
| `INSTAGRAM_API_TOKEN` | Meta/Facebook | https://developers.facebook.com/ |
| `TWITTER_API_KEY` | Twitter Dev | https://developer.twitter.com/ (optional) |

Details in: [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md#required-api-keys--credentials)

---

## 🐳 What We Removed (Per Your Request)

- Docker & Docker Compose
- Alembic migrations
- Unnecessary dependencies

Everything is now simplified for direct deployment.

---

## ✅ Verification Steps

After starting both servers:

```bash
# 1. Check backend health
curl http://localhost:8000/health

# Expected:
# {"status": "ok", "version": "1.0.0", ...}

# 2. Check API docs
# Open: http://localhost:8000/docs

# 3. Check frontend
# Open: http://localhost:3000

# 4. Test analysis
# 1. Go to http://localhost:3000
# 2. Click "Analyze Post"
# 3. Enter Instagram URL
# 4. Click "Analyze"
# 5. Wait for results
```

---

## 🚨 Common Issues & Fixes

### PostgreSQL not running
```bash
# Windows: Start from Services app
# macOS: brew services start postgresql@15
# Linux: sudo service postgresql start
```

### Database not found
```bash
createdb narrativewatch
psql narrativewatch -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### Module not found (Python)
```bash
cd backend
pip install -r requirements.txt
```

### Port 3000 or 8000 in use
```bash
# Backend port 8000
python -m uvicorn src.app:app --port 8001

# Frontend port 3000
npm run dev -- --port 3001
```

More help: [QUICK_START_GUIDE.md - Troubleshooting](QUICK_START_GUIDE.md#troubleshooting)

---

## 📊 Architecture at a Glance

```
Frontend (React + Vite)
    ↓ API proxy (http://localhost:8000)
Backend (FastAPI)
    ↓
Database (PostgreSQL + pgvector)
    ↓
Vector Embeddings (1536-dim)

9 Agents:
├── OrchestratorAgent (Coordinates)
├── ContentAnalyzerAgent
├── RAGAgent (Vector search)
├── ResearchAgent (Web search)
├── BiasDetectorAgent
├── BotDetectorAgent
├── CampaignDetectorAgent
├── SynthesisAgent
└── ReviewerAgent
```

---

## 📈 What This Application Does

1. **Analyzes Instagram Content** - Posts and pages
2. **Detects Patterns** - Bias, bots, campaigns
3. **Searches Context** - Web search + vector similarity
4. **Synthesizes Findings** - Creates comprehensive report
5. **Calculates Risk Score** - Trust score and risk level

**Output**: Comprehensive analysis with risk assessment and recommendations

---

## 🔧 Configuration Files

- **[.env.example](backend/.env.example)** - Environment variables template
- **[requirements.txt](backend/requirements.txt)** - Python dependencies (47 packages)
- **[package.json](frontend/package.json)** - Node.js dependencies
- **[vite.config.js](frontend/vite.config.js)** - Frontend configuration
- **[src/config.py](backend/src/config.py)** - Backend configuration

---

## 📞 Need Help?

1. **Quick Start Issues** → [RUN_INSTRUCTIONS.txt](RUN_INSTRUCTIONS.txt)
2. **Detailed Setup** → [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md)
3. **Understanding Status** → [DEPLOYMENT_READY.md](DEPLOYMENT_READY.md)
4. **API Documentation** → http://localhost:8000/docs (when running)
5. **Project Structure** → [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

---

## ✨ Quick Checklist

Before starting:
- [ ] PostgreSQL 15+ installed
- [ ] Python 3.10+ installed
- [ ] Node.js 18+ installed
- [ ] .env file created with API keys

To run:
- [ ] Backend server started (`python -m uvicorn src.app:app --reload`)
- [ ] Frontend server started (`npm run dev`)
- [ ] Both accessible (http://localhost:3000 and http://localhost:8000)

---

## 🎓 Learning Resources

- **Backend Code**: `backend/src/` folder
- **Frontend Code**: `frontend/src/` folder
- **Agents**: `backend/src/agents/` folder
- **Database**: `backend/src/database/` folder
- **Workflow**: `backend/src/workflow/` folder

---

## 🚀 Next Steps

1. **Choose a path above** (Option A, B, or C)
2. **Get your API keys** (4 services)
3. **Follow the steps** in your chosen guide
4. **Access the app** at http://localhost:3000
5. **Test an analysis**

---

## 📝 Git Status

**Latest commits:**
- ✅ Comprehensive quick start guide
- ✅ Quick reference instructions
- ✅ Deployment ready status
- ✅ All code pushed to Devlop2 branch

**Ready to:** Start end-to-end testing

---

## Questions?

Check these files in order:
1. This file (START_HERE.md) - Overview
2. RUN_INSTRUCTIONS.txt - Quick start
3. QUICK_START_GUIDE.md - Detailed help
4. DEPLOYMENT_READY.md - Understanding status

All guides are self-contained with examples and troubleshooting.

---

**Status: 🟢 READY TO RUN**

Last updated: June 12, 2026

Choose your path above and let's get started! 🚀

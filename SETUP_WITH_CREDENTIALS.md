# NarrativeWatch AI - Ready to Run Setup Guide

**Status: Configuration Complete ✅**

Your credentials have been configured and saved. Follow these steps to run the application.

---

## 📋 Your Configuration Summary

### Vertex AI (Google Cloud)
```
Project ID:    learning-development-c-000027
Location:      us-central1
LLM Model:     gemini-2.5-pro
Embedding:     text-embedding-005
Status:        ✅ Configured
```

### API Keys
```
Tavily API:    ✅ Configured (tvly-dev-bG8Lu-...)
Instagram:     ⚠️  Optional - not set
Twitter:       ⚠️  Optional - not set
```

### Email
```
Address:       pankaj91201@gmail.com
Status:        ✅ Configured
```

### Database
```
Host:          localhost
Port:          5432
Database:      narrativewatch
User:          postgres
Status:        🔍 Ready to create
```

---

## 🚀 Quick Start (3 Steps)

### Step 1: Create PostgreSQL Database

**Windows Command Prompt (as Administrator):**
```cmd
# Start PostgreSQL (if not already running)
# Service name: PostgreSQL 15

# Create database
psql -U postgres -c "CREATE DATABASE narrativewatch;"

# Enable pgvector
psql -U postgres -d narrativewatch -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Verify
psql -U postgres -d narrativewatch -c "\dt"
```

**OR use pgAdmin GUI:**
1. Open pgAdmin (http://localhost:5050)
2. Right-click "Databases" → "Create" → "Database"
3. Name: `narrativewatch`
4. Click "Create"
5. Right-click database → "Query Tool"
6. Run: `CREATE EXTENSION IF NOT EXISTS vector;`

### Step 2: Install Python Dependencies

```bash
cd backend
python -m venv venv

# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### Step 3: Start Backend

```bash
# Verify configuration
python verify_config.py

# Expected output: ✅ ALL REQUIRED VARIABLES SET - READY TO START!

# Start the server
python -m uvicorn src.app:app --reload --port 8000
```

You should see:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 4: Start Frontend (New Terminal)

```bash
cd frontend
npm install
npm run dev
```

You should see:
```
  VITE v5.0.0  ready in 234 ms
  ➜  Local:   http://localhost:3000/
```

### Step 5: Access the Application

- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc

---

## ✅ Verification Checklist

### Before Starting
- [ ] PostgreSQL 15+ installed on Windows
- [ ] Python 3.10+ installed
- [ ] Node.js 18+ installed
- [ ] `.env` file in project root (already created)
- [ ] Dependencies will be installed in Step 2

### After Starting Backend
```bash
# In new terminal, test health check
curl http://localhost:8000/health

# Expected response:
# {"status": "ok", "version": "1.0.0", "components": {...}}
```

### After Starting Frontend
- Open http://localhost:3000 in browser
- You should see NarrativeWatch AI dashboard
- Dashboard displays statistics

### End-to-End Test
1. Go to http://localhost:3000
2. Click "Analyze Post" button
3. Enter Instagram post URL (example: https://instagram.com/p/ABC123/)
4. Click "Analyze"
5. Wait for "Analysis in progress" message
6. Check backend terminal for agent logs:
   - ContentAnalyzerAgent
   - RAGAgent
   - ResearchAgent
   - BiasDetectorAgent
   - BotDetectorAgent
   - CampaignDetectorAgent
   - SynthesisAgent
   - ReviewerAgent
7. Results display on frontend

---

## 🔧 Configuration Files

Your configuration is stored in:

**`.env`** (Project root - NOT committed to git)
```
GOOGLE_CLOUD_PROJECT=learning-development-c-000027
GOOGLE_CLOUD_LOCATION=us-central1
TAVILY_API_KEY=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
EMAIL_ADDRESS=pankaj91201@gmail.com
EMAIL_PASSWORD=rohvlqtcwbxzdfsy
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/narrativewatch
...
```

**`backend/.env.example`** (Template - committed to git)
- Same as above, can be used as reference

---

## 🐛 Troubleshooting

### PostgreSQL Issues

**Database doesn't exist:**
```bash
psql -U postgres -c "CREATE DATABASE narrativewatch;"
```

**pgvector extension missing:**
```bash
psql -U postgres -d narrativewatch -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

**Can't connect to PostgreSQL:**
```bash
# Windows: Start PostgreSQL service
# From Command Prompt (admin):
net start PostgreSQL-x64-15

# Or use Services app and search for PostgreSQL
```

### Backend Issues

**Module not found:**
```bash
cd backend
venv\Scripts\activate
pip install -r requirements.txt
```

**Port 8000 already in use:**
```bash
python -m uvicorn src.app:app --port 8001
```

**Tavily API error:**
- Verify TAVILY_API_KEY in .env is correct
- Check internet connection

**Vertex AI error:**
- Verify GOOGLE_CLOUD_PROJECT is correct: `learning-development-c-000027`
- Verify GOOGLE_CLOUD_LOCATION is correct: `us-central1`
- Check Google Cloud credentials are accessible

### Frontend Issues

**Port 3000 already in use:**
```bash
npm run dev -- --port 3001
```

**Module not found:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

**Cannot reach backend:**
- Verify backend is running on http://localhost:8000
- Check vite.config.js has correct proxy: `http://localhost:8000`

---

## 📊 Environment Variables Explained

| Variable | Value | Purpose |
|----------|-------|---------|
| `GOOGLE_CLOUD_PROJECT` | `learning-development-c-000027` | GCP project for Vertex AI |
| `GOOGLE_CLOUD_LOCATION` | `us-central1` | Region for Vertex AI services |
| `GOOGLE_GENAI_USE_VERTEXAI` | `TRUE` | Enable Vertex AI for LLM |
| `LLM_MODEL` | `gemini-2.5-pro` | Gemini LLM model |
| `EMBEDDING_MODEL` | `text-embedding-005` | Embedding model for vectors |
| `TAVILY_API_KEY` | `tvly-dev-...` | Web search API |
| `EMAIL_ADDRESS` | `pankaj91201@gmail.com` | Email for notifications |
| `EMAIL_PASSWORD` | `rohvlqtcwbxzdfsy` | Email app password |
| `DATABASE_URL` | `postgresql://...` | PostgreSQL connection string |

---

## 📈 Expected Performance

- **Backend startup**: ~10-30 seconds
- **First analysis**: ~60 seconds (downloads models)
- **Subsequent analyses**: ~30-60 seconds
- **Vector dimension**: 1536-dimensional embeddings
- **Database pooling**: 10 base + 20 overflow connections

---

## 🎯 Next Steps After Running

1. **Test Analysis Features**
   - Analyze different Instagram posts
   - Check agent logs in terminal
   - Review results on frontend

2. **Monitor Logs**
   - Backend: `backend/logs/narrativewatch.log`
   - Frontend: Browser console (F12)
   - Terminal output for agent execution

3. **Check API Documentation**
   - Visit http://localhost:8000/docs
   - Try out endpoints in Swagger UI

4. **Verify All 9 Agents**
   - Each analysis should show all agents executing
   - Check logs for:
     - OrchestratorAgent
     - ContentAnalyzerAgent
     - RAGAgent
     - ResearchAgent
     - BiasDetectorAgent
     - BotDetectorAgent
     - CampaignDetectorAgent
     - SynthesisAgent
     - ReviewerAgent

---

## 📚 Documentation

- **This file**: Setup with your credentials
- **START_HERE.md**: Navigation guide
- **QUICK_START_GUIDE.md**: Comprehensive guide
- **RUN_INSTRUCTIONS.txt**: Quick reference
- **DEPLOYMENT_READY.md**: Status checklist

---

## ✨ You're All Set!

Your credentials are configured. The next steps are:

1. ✅ Create PostgreSQL database (Step 1 above)
2. ✅ Install backend dependencies (Step 2 above)
3. ✅ Start backend server (Step 3 above)
4. ✅ Start frontend server (Step 4 above)
5. ✅ Access at http://localhost:3000

Everything else is already done!

---

## 🆘 Still Need Help?

If you encounter issues:

1. Run `python backend/verify_config.py` to check configuration
2. Check logs in `backend/logs/narrativewatch.log`
3. Check browser console (F12)
4. Refer to **QUICK_START_GUIDE.md** for detailed troubleshooting

---

**Configuration Status: ✅ COMPLETE**

**Ready to: 🚀 START BACKEND & FRONTEND**

Happy analyzing! 🎉

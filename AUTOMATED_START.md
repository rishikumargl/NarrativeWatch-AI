# 🚀 Automated Startup - NarrativeWatch AI

## One-Command Startup!

Your project is now fully automated. Choose your method below:

---

## **Option 1: PowerShell (Recommended) ⭐**

### **ONE COMMAND:**
```powershell
powershell -ExecutionPolicy Bypass -File START_ALL.ps1
```

**What it does:**
- ✅ Checks PostgreSQL
- ✅ Creates database and enables pgvector
- ✅ Verifies all configuration
- ✅ Creates Python virtual environment
- ✅ Installs all Python dependencies
- ✅ Installs all frontend dependencies
- ✅ Starts backend server (port 8000)
- ✅ Starts frontend server (port 3000)
- ✅ Opens browser to http://localhost:3000

---

## **Option 2: Batch File (Windows CMD)**

### **ONE CLICK:**
1. Double-click `START_ALL.bat` in your project folder
2. New terminal windows will open for backend and frontend
3. Application starts automatically

---

## **Option 3: Manual Step-by-Step**

If you prefer to run commands manually:

```bash
# Terminal 1 - Backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn src.app:app --reload --port 8000
```

```bash
# Terminal 2 - Frontend (NEW TERMINAL)
cd frontend
npm install
npm run dev
```

---

## **Configuration Status**

✅ **All Credentials Already Set:**
- Google Cloud: `learning-development-c-000027`
- Tavily API: `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`
- **NewsAPI Key: `a5e572fa74f441059d7b1bc2395bb19f`** ✅
- Email: `pankaj91201@gmail.com`
- Database: PostgreSQL (auto-creates if doesn't exist)

**No additional configuration needed!**

---

## **Requirements Before Running**

✅ PostgreSQL 15+ must be installed and running
✅ Python 3.10+ installed
✅ Node.js 18+ installed
✅ All configuration in `.env` file (already done ✓)

### **Check Prerequisites:**

```bash
# Check Python
python --version

# Check Node.js
node --version

# Check PostgreSQL (must be running)
psql --version
```

---

## **First Run?**

1. Open PowerShell or Command Prompt
2. Navigate to project folder: `cd "c:\Users\rohan.urmude\Desktop\NarrativeWatch AI"`
3. Run: `powershell -ExecutionPolicy Bypass -File START_ALL.ps1`
4. Wait for browser to open automatically
5. Start analyzing news articles!

---

## **What Happens When You Run**

### **Backend (Port 8000)**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### **Frontend (Port 3000)**
```
  VITE v5.0.0  ready in 234 ms
  ➜  Local:   http://localhost:3000/
```

---

## **Access Points**

Once running, you can access:

| Component | URL | Purpose |
|-----------|-----|---------|
| **Frontend** | http://localhost:3000 | Web interface |
| **Backend API** | http://localhost:8000 | API server |
| **API Docs** | http://localhost:8000/docs | Swagger UI |
| **ReDoc** | http://localhost:8000/redoc | Alternative docs |

---

## **Analyzing News Articles**

### **Method 1: Web Interface**
1. Go to http://localhost:3000
2. Click "Analyze Article"
3. Enter article details
4. Click "Analyze"
5. View results

### **Method 2: Search News (Auto-fetch)**
1. Go to http://localhost:3000
2. Click "Search News"
3. Enter search query (e.g., "artificial intelligence")
4. Click "Search"
5. Analyzes top 10 articles automatically

### **Method 3: API (Advanced)**
```bash
curl -X POST "http://localhost:8000/search/news" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "climate change",
    "num_articles": 10
  }'
```

---

## **Stop the Application**

Press `Ctrl+C` in the terminal windows or close them.

---

## **Troubleshooting**

### **PostgreSQL not running?**
```bash
# Windows Services:
# 1. Press Win+R
# 2. Type: services.msc
# 3. Find "PostgreSQL" service
# 4. Right-click → Start
```

### **Port already in use?**
The script will try to use default ports. If they're taken, you'll see an error. Either:
- Close other applications using those ports
- Manually specify different ports in app.py and vite.config.js

### **Dependencies not installing?**
```bash
cd backend
pip install --upgrade pip
pip install -r requirements.txt
```

### **Still having issues?**
Check logs in `backend/logs/narrativewatch.log`

---

## **What Gets Analyzed**

Each news article is analyzed for:

✅ **Misinformation Signals**
- Sensationalism score
- Missing author flags
- Excessive punctuation
- All-caps titles

✅ **Bias Indicators**
- Emotional language
- One-sided reporting
- Opinion vs news
- Loaded language

✅ **Content Analysis**
- Narrative themes
- Emotional language
- Writing patterns
- Factual claims

✅ **Source Credibility**
- Author presence
- Source reputation
- Suspicious indicators

---

## **9 AI Agents Working Together**

1. **OrchestratorAgent** - Coordinates analysis
2. **ContentAnalyzerAgent** - Analyzes article content
3. **RAGAgent** - Retrieves similar articles
4. **ResearchAgent** - Web research on topics
5. **BiasDetectorAgent** - Detects bias patterns
6. **BotDetectorAgent** - Identifies coordinated posts
7. **CampaignDetectorAgent** - Finds campaigns
8. **SynthesisAgent** - Synthesizes findings
9. **ReviewerAgent** - Reviews and validates

---

## **Performance**

- **First article analysis:** ~30-60 seconds (downloads models)
- **Subsequent analyses:** ~20-40 seconds
- **Search & analyze 10 articles:** ~60-90 seconds

---

## **Next Steps**

1. ✅ Run startup script (PowerShell or batch)
2. ✅ Wait for servers to start
3. ✅ Browser opens automatically
4. ✅ Start analyzing news articles!

---

## **You're All Set!** 🎉

Everything is automated and configured. Just run:

```powershell
powershell -ExecutionPolicy Bypass -File START_ALL.ps1
```

And your NarrativeWatch AI application will be running!

**Happy analyzing!** 📰🤖

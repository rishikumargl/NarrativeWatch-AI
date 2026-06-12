# NarrativeWatch AI - Quick Start Guide

## Prerequisites

Before running the application, ensure you have:

- **Python 3.10+** - `python --version`
- **PostgreSQL 15+** - [Download](https://www.postgresql.org/download/)
- **Node.js 18+** - `node --version`
- **npm or yarn** - `npm --version`
- **pgvector extension** - Required for PostgreSQL

---

## Required API Keys & Credentials

You'll need to obtain these keys before running the application:

### 1. **Vertex AI (Google Cloud)**
   - **What**: LLM and embeddings service
   - **How to get**:
     1. Go to [Google Cloud Console](https://console.cloud.google.com/)
     2. Create a new project or select existing
     3. Enable "Vertex AI API"
     4. Create a service account
     5. Download JSON key file
     6. Set `GOOGLE_APPLICATION_CREDENTIALS` environment variable
   - **Env Variable**: `VERTEX_AI_PROJECT`, `VERTEX_AI_LOCATION`
   - **Cost**: ~$0.00015 per 1000 embeddings

### 2. **Tavily Search API**
   - **What**: Web search and fact-checking
   - **How to get**:
     1. Go to [Tavily AI](https://www.tavily.com/)
     2. Sign up for free account
     3. Get API key from dashboard
   - **Env Variable**: `TAVILY_API_KEY`
   - **Cost**: Free tier available

### 3. **Instagram Graph API**
   - **What**: Instagram data collection
   - **How to get**:
     1. Go to [Meta Developers](https://developers.facebook.com/)
     2. Create app and get credentials
     3. Request Instagram Graph API access
     4. Generate access token
   - **Env Variable**: `INSTAGRAM_API_TOKEN`
   - **Cost**: Free tier available

### 4. **Twitter API (Optional)**
   - **What**: Cross-platform data collection
   - **How to get**:
     1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
     2. Apply for developer access
     3. Get Bearer token
   - **Env Variable**: `TWITTER_API_KEY`
   - **Cost**: Varies by plan

---

## Environment Setup

### Step 1: Setup PostgreSQL

**On Windows:**
```bash
# After installing PostgreSQL, start the service
# Or use pgAdmin GUI (default: localhost:5050)

# Create database (using psql command line)
psql -U postgres -c "CREATE DATABASE narrativewatch;"

# Verify extension installation
psql -U postgres -d narrativewatch -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

**On macOS:**
```bash
# Using Homebrew
brew install postgresql@15

# Start PostgreSQL
brew services start postgresql@15

# Create database
createdb narrativewatch

# Add pgvector extension
psql narrativewatch -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

**On Linux (Ubuntu/Debian):**
```bash
# Install PostgreSQL
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# Install pgvector
sudo apt-get install postgresql-15-pgvector

# Start PostgreSQL
sudo service postgresql start

# Create database
sudo -u postgres createdb narrativewatch
sudo -u postgres psql -d narrativewatch -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### Step 2: Create Environment File

Create `.env` in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# ============================================
# LLM & VERTEX AI CONFIGURATION
# ============================================
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
VERTEX_AI_PROJECT=your-gcp-project-id
VERTEX_AI_LOCATION=us-central1
LLM_MODEL=gemini-2.5-pro
EMBEDDING_MODEL=text-embedding-005

# ============================================
# EXTERNAL API KEYS
# ============================================
TAVILY_API_KEY=your-tavily-api-key
INSTAGRAM_API_TOKEN=your-instagram-token
TWITTER_API_KEY=your-twitter-token (optional)

# ============================================
# DATABASE CONFIGURATION
# ============================================
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/narrativewatch
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=narrativewatch

# ============================================
# API SERVER CONFIGURATION
# ============================================
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
API_RELOAD=True

# ============================================
# APPLICATION SETTINGS
# ============================================
ENV=development
DEBUG=True
APP_NAME=NarrativeWatch AI
APP_VERSION=1.0.0
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# ============================================
# LOGGING
# ============================================
LOG_LEVEL=INFO
LOG_FILE=logs/narrativewatch.log
```

---

## Running the Application

### Option 1: Run Backend & Frontend Separately (Recommended for Development)

#### Terminal 1: Start Backend

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python scripts/init_db.py

# Start FastAPI server
python -m uvicorn src.app:app --reload --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

#### Terminal 2: Start Frontend

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

**Expected output:**
```
  VITE v5.0.0  ready in 234 ms

  ➜  Local:   http://localhost:3000/
  ➜  Press q to quit
```

---

### Option 2: Run Both Together (Using Scripts)

**On macOS/Linux:**

```bash
# Make scripts executable
chmod +x start.sh

# Run both servers
./start.sh
```

**On Windows (PowerShell):**

```bash
# Create start.ps1
$backendProcess = Start-Process python -ArgumentList "-m uvicorn src.app:app --reload --port 8000" -WorkingDirectory "backend" -NoNewWindow
$frontendProcess = Start-Process npm -ArgumentList "run dev" -WorkingDirectory "frontend" -NoNewWindow

Write-Host "Backend running on http://localhost:8000"
Write-Host "Frontend running on http://localhost:3000"
```

---

## Verification Steps

### 1. Check Backend Health

```bash
# In a new terminal, test API health
curl http://localhost:8000/health

# Expected response:
{
  "status": "ok",
  "version": "1.0.0"
}
```

### 2. Check Database Connection

```bash
# In Python shell
python
>>> from backend.src.database.postgres_client import PostgresClient
>>> client = PostgresClient()
>>> print("Database connected successfully!")
```

### 3. Check API Endpoints

```bash
# Get system statistics
curl http://localhost:8000/stats

# Expected response:
{
  "total_posts_analyzed": 0,
  "total_pages_analyzed": 0,
  "agents_running": 9,
  "average_trust_score": 0.0
}
```

### 4. Test Frontend

Open browser and navigate to: **http://localhost:3000**

Expected to see:
- NarrativeWatch AI header
- Dashboard with platform statistics
- Analyze button for post/page analysis
- Links to analysis form

---

## Full End-to-End Test

### Test Analysis Workflow

```bash
# 1. Open frontend at http://localhost:3000

# 2. Navigate to "Analyze Post"

# 3. Enter test data:
#    - Analysis Type: Post Analysis
#    - Post URL: https://instagram.com/p/example
#    - Include Context: Yes
#    - Check for Campaigns: Yes

# 4. Click "Analyze"

# 5. Wait for "Analysis in progress" message

# 6. Check backend logs for agent execution:
#    - Content Analyzer
#    - RAG Agent
#    - Research Agent
#    - Bias Detector
#    - Bot Detector
#    - Campaign Detector
#    - Synthesis Agent
#    - Reviewer Agent

# 7. View results when completed
```

---

## Troubleshooting

### Backend Issues

**Error: "No module named 'src'"**
```bash
# Solution: Make sure you're in the backend directory
cd backend
python -m uvicorn src.app:app --reload
```

**Error: "PostgreSQL connection refused"**
```bash
# Solution: Check PostgreSQL is running
# Windows: Start PostgreSQL service from Services
# macOS: brew services start postgresql@15
# Linux: sudo service postgresql start

# Verify connection:
psql -U postgres -d narrativewatch
```

**Error: "pgvector extension not found"**
```bash
# Solution: Install pgvector extension
psql -U postgres -d narrativewatch
postgres=# CREATE EXTENSION vector;
postgres=# \q
```

**Error: "API key validation failed"**
```bash
# Solution: Check .env file has correct keys
# Verify GOOGLE_APPLICATION_CREDENTIALS file exists
# Test Vertex AI: python -c "from google.cloud import aiplatform; aiplatform.init()"
```

### Frontend Issues

**Error: "Cannot find module 'react'"**
```bash
# Solution: Install dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

**Error: "Port 3000 already in use"**
```bash
# Solution: Use different port
npm run dev -- --port 3001
# Or kill process using port 3000
# Windows: netstat -ano | findstr :3000
# macOS/Linux: lsof -i :3000
```

---

## Database Management

### Backup Database

```bash
# Windows Command Prompt
pg_dump -U postgres -d narrativewatch > backup.sql

# macOS/Linux
pg_dump -U postgres narrativewatch > backup.sql
```

### Restore Database

```bash
# Create fresh database
psql -U postgres -c "DROP DATABASE narrativewatch;"
psql -U postgres -c "CREATE DATABASE narrativewatch;"

# Restore from backup
psql -U postgres narrativewatch < backup.sql
```

### View Database Contents

```bash
# Connect to database
psql -U postgres -d narrativewatch

# List tables
\dt

# View instagram_posts table
SELECT * FROM instagram_posts LIMIT 5;

# Exit
\q
```

---

## Performance Tips

1. **Backend Optimization**
   - Use `API_WORKERS=4` for production
   - Set `DEBUG=False` for production
   - Use connection pooling (auto-configured)

2. **Frontend Optimization**
   - Build for production: `npm run build`
   - Use `serve` to run production build: `npx serve -s dist`

3. **Database Optimization**
   - pgvector indices created automatically
   - Connection pooling: 10 base + 20 overflow

---

## Next Steps

Once running successfully:

1. **Test Analysis Features**
   - Analyze Instagram posts
   - Check agent outputs
   - Review trust scores

2. **Monitor Logs**
   - Backend: `backend/logs/narrativewatch.log`
   - Frontend: Browser console (F12)

3. **Scale Up**
   - Add more workers: `API_WORKERS=8`
   - Use production WSGI: `gunicorn src.app:app`
   - Deploy to cloud (AWS, GCP, Azure)

---

## Support & Debugging

### Enable Verbose Logging

```env
LOG_LEVEL=DEBUG
```

### View Agent Execution

Check backend terminal for detailed agent logs:
```
INFO: ContentAnalyzerAgent started
INFO: RAGAgent retrieved 3 similar posts
INFO: ResearchAgent found 5 sources
...
```

### Check API Documentation

Visit: **http://localhost:8000/docs**

This opens interactive Swagger UI for testing endpoints.

---

## Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://...` | PostgreSQL connection string |
| `VERTEX_AI_PROJECT` | `narrativewatch-ai` | GCP project ID |
| `VERTEX_AI_LOCATION` | `us-central1` | GCP region |
| `LLM_MODEL` | `gemini-2.5-pro` | LLM model name |
| `EMBEDDING_MODEL` | `text-embedding-005` | Embedding model |
| `API_PORT` | `8000` | Backend API port |
| `LOG_LEVEL` | `INFO` | Logging level |
| `CORS_ORIGINS` | `http://localhost:3000` | Allowed origins |

---

## Success Indicators

✅ Backend starts without errors  
✅ Database connection successful  
✅ Frontend loads at http://localhost:3000  
✅ Health check returns 200 OK  
✅ Can submit analysis request  
✅ Agents execute and return results  
✅ Results display in frontend  

You're ready to use NarrativeWatch AI! 🚀

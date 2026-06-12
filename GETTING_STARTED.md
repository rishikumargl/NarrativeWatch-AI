# NarrativeWatch AI - Getting Started

## Quick Start (Easiest)

### Windows
1. Open terminal/PowerShell in the project root
2. Run:
```bash
.\start.bat
```

This will open 2 new windows - one for backend, one for frontend.

### Mac/Linux
1. Open terminal in the project root
2. Run:
```bash
bash start.sh
```

---

## Manual Start (If Scripts Don't Work)

### Terminal 1 - Backend
```bash
cd backend
python run.py
```

Expected output:
```
[OK] Starting NarrativeWatch AI Backend
[OK] URL: http://localhost:8000
[OK] Docs: http://localhost:8000/docs
```

### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```

Expected output:
```
VITE v5.4.21 ready in XXX ms
➜  Local:   http://localhost:3000/
```

---

## Access the Application

- **Home Page**: http://localhost:3000
- **Analyze**: http://localhost:3000/analyze
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## What You Can Do

### 1. **Analyze Single Article**
- Go to `/analyze` tab "Single Article"
- Enter article title and content
- Click "Analyze Article"
- View trust score and analysis results

### 2. **Search & Analyze News**
- Go to `/analyze` tab "News Search"
- Enter search query (e.g., "election", "climate")
- Select number of articles to analyze
- Click "Search & Analyze"
- Get results for multiple articles

### 3. **View Results**
- See trust score (0-100%)
- Review risk indicators
- Check detected patterns
- Read recommendations

---

## System Overview

```
Frontend (React)          Backend (FastAPI)         APIs
- HomePage              - 11 AI Agents            - Groq LLM
- AnalyzePage           - Article Analysis        - NewsAPI
- ResultsPage           - News Search             - Tavily
                        - Bias Detection
                        - Fact Checking
                        - Risk Assessment
```

---

## Technology Stack

### Frontend
- React 18
- Vite (build tool)
- Tailwind CSS v4
- Lucide React (icons)

### Backend
- FastAPI
- LangChain
- Groq API
- PostgreSQL + pgvector (RAG)

---

## Troubleshooting

### Port Already in Use
- Frontend automatically tries ports 3000, 3001, 3002
- Check the output to see which port it's using

### Backend Won't Start
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000
```

### Frontend Won't Start
```bash
cd frontend
npm install
npm run dev
```

### Clear Everything & Start Fresh
```bash
# Backend
cd backend
# (no cleanup needed)

# Frontend
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

---

## Project Structure

```
NarrativeWatch AI/
├── backend/
│   ├── src/
│   │   ├── app.py              # FastAPI app
│   │   ├── agents/             # 11 AI agents
│   │   ├── models/             # Data models
│   │   ├── database/           # Database & RAG
│   │   └── workflow/           # Agent orchestration
│   ├── run.py                  # Startup script
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── pages/
│   │   │   ├── HomePage.jsx
│   │   │   ├── AnalyzePage.jsx
│   │   │   └── ResultsPage.jsx
│   │   ├── components/
│   │   │   └── Nav.jsx
│   │   └── index.css
│   ├── package.json
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── vite.config.js
│   └── index.html
├── start.bat                   # Windows startup
├── start.sh                    # Mac/Linux startup
├── README.md
├── QUICK_START.md
└── .env                        # Configuration
```

---

## Environment Variables

Create `.env` in the backend directory:

```
APP_NAME=NarrativeWatch
APP_VERSION=1.0.0
GROQ_API_KEY=your_groq_key
NEWSAPI_KEY=your_newsapi_key
TAVILY_API_KEY=your_tavily_key
DATABASE_URL=postgresql://user:password@localhost/narrativewatch
CORS_ORIGINS=["http://localhost:3000","http://localhost:3001","http://localhost:3002"]
```

---

## Development Tips

### Hot Reload
- Frontend: Automatically reloads on file changes
- Backend: Runs with `reload=True` for hot reload

### API Testing
- Visit http://localhost:8000/docs for interactive API docs
- Try endpoints directly in Swagger UI

### VS Code Extensions (Recommended)
- ES7+ React/Redux/React-Native snippets
- Tailwind CSS IntelliSense
- Python
- FastAPI

---

## Next Steps

1. Start the servers: `.\start.bat` (Windows) or `bash start.sh` (Mac/Linux)
2. Open http://localhost:3000 in your browser
3. Try analyzing an article or searching for news
4. Check the results and trust scores

---

**Ready to go!** 🚀

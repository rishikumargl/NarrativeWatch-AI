# NarrativeWatch AI - Quick Start Guide

Get up and running with NarrativeWatch AI in 5 minutes.

## ⚡ Quick Start (Development)

### Prerequisites
- Python 3.10+
- Node.js 18+
- Git

### Setup (3 commands)

```bash
# 1. Clone and enter directory
git clone https://github.com/rishikumargl/NarrativeWatch-AI.git
cd NarrativeWatch-AI

# 2. Setup Python backend
python -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate (Windows)
pip install -r requirements.txt

# 3. Setup Node.js frontend
cd frontend
npm install
cd ..
```

### Run (2 terminals)

**Terminal 1 - Backend API (port 8000)**
```bash
source venv/bin/activate
python -m uvicorn src.app:app --reload
```

**Terminal 2 - Frontend (port 5173)**
```bash
cd frontend
npm run dev
```

### Access
- Frontend: `http://localhost:5173`
- API: `http://localhost:8000`
- API Docs: `http://localhost:8000/api/docs`

---

## 🐳 Quick Start (Docker)

### One Command
```bash
docker-compose up --build
```

### Access
- Entire app: `http://localhost:8000`
- API Docs: `http://localhost:8000/api/docs`

### Cleanup
```bash
docker-compose down
docker-compose down -v  # Also remove data
```

---

## 📝 Quick Test

### Test API (without orchestrator)
```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "instagram_url": "https://www.instagram.com/bbcnews/",
    "analysis_type": "page"
  }'
```

### Test in React
1. Open `http://localhost:5173`
2. Enter: `https://www.instagram.com/bbcnews/`
3. Click "Analyze"
4. See mock results

---

## 📁 Project Structure

```
NarrativeWatch-AI/
├── src/                    # Python backend
│   ├── app.py             # Main API server
│   ├── models/            # Data validation
│   └── utils/             # Helpers
│
├── frontend/              # React frontend
│   ├── src/
│   │   ├── App.jsx        # Main component
│   │   ├── components/    # Reusable components
│   │   ├── services/      # API client
│   │   └── styles/        # CSS
│   ├── package.json
│   └── vite.config.js
│
├── docs/                  # Documentation
│   ├── SETUP_GUIDE.md    # Full setup
│   ├── DEPLOYMENT.md     # Production
│   └── API_REFERENCE.md  # API docs
│
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## 🔧 Key Commands

### Backend
```bash
# Start API
python -m uvicorn src.app:app --reload

# Type check
mypy src/

# Format code
black src/

# Run tests (when available)
pytest tests/
```

### Frontend
```bash
# Dev server
npm run dev

# Build for production
npm run build

# Preview build
npm run preview

# Lint
npm run lint
```

### Docker
```bash
# Start all services
docker-compose up --build

# View logs
docker-compose logs -f api

# Access container
docker-compose exec api bash

# Stop all
docker-compose down
```

---

## 🔗 Integration with Orchestrator

When Team 1 finishes orchestrator:

1. **Edit `src/app.py` line 82**
   ```python
   # Replace this:
   response = await _mock_analysis(request, request_id)
   
   # With this:
   from src.workflow.orchestration import WorkflowOrchestrator
   orchestrator = WorkflowOrchestrator()
   response = await orchestrator.execute(request)
   ```

2. **Test the pipeline**
   ```bash
   # With all services running
   curl -X POST http://localhost:8000/api/v1/analyze \
     -H "Content-Type: application/json" \
     -d '{"instagram_url": "https://instagram.com/bbcnews/"}'
   ```

---

## 📚 Detailed Docs

- **Setup:** See [SETUP_GUIDE.md](./docs/SETUP_GUIDE.md)
- **API:** See [API_REFERENCE.md](./docs/API_REFERENCE.md)
- **Deploy:** See [DEPLOYMENT.md](./docs/DEPLOYMENT.md)
- **Full Details:** See [TEAM_MEMBER_5_SUMMARY.md](./TEAM_MEMBER_5_SUMMARY.md)

---

## 🆘 Troubleshooting

### Port in use?
```bash
# Find what's using port 8000
lsof -i :8000        # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill it
kill -9 <PID>        # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

### Database connection error?
```bash
# Check if PostgreSQL is running (Docker)
docker-compose ps postgres

# Restart PostgreSQL
docker-compose down
docker-compose up postgres -d
```

### Frontend won't load?
```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Docker image too large?
Already optimized with multi-stage build. If issues:
```bash
docker image prune  # Remove unused images
docker system prune  # Deep clean
```

---

## ✅ Next Steps

1. **Get familiar with the code** - Review [src/app.py](./src/app.py)
2. **Test the mock API** - Use the quick test above
3. **Explore the frontend** - Run locally and test UI
4. **Read full docs** - Check [SETUP_GUIDE.md](./docs/SETUP_GUIDE.md)
5. **Wait for other teams** - They'll integrate their agents
6. **Integrate orchestrator** - When Team 1 is ready
7. **Deploy to production** - See [DEPLOYMENT.md](./docs/DEPLOYMENT.md)

---

## 📞 Questions?

- Check [API_REFERENCE.md](./docs/API_REFERENCE.md) for API details
- Read inline code comments
- Check [TEAM_MEMBER_5_SUMMARY.md](./TEAM_MEMBER_5_SUMMARY.md) for architecture
- Open an issue on GitHub

---

**You're all set!** Start with one of the quick start options above. 🚀

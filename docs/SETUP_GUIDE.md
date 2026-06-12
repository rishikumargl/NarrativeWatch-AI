# NarrativeWatch AI - Setup Guide

Complete setup instructions for the NarrativeWatch AI development environment.

## Prerequisites

### System Requirements
- **Python 3.10+** - Backend runtime
- **Node.js 18+** - Frontend build
- **Docker & Docker Compose** - For containerized deployment
- **Git** - Version control
- **4GB RAM minimum** - For development
- **2GB free disk space** - For dependencies

### API Keys Required
1. **Tavily Search API** - External research capability
2. **Instagram Graph API** - Instagram data access
3. **Vertex AI / Google Cloud** - LLM and embeddings
4. **PostgreSQL / pgvector** - Vector database

## Installation Steps

### 1. Clone Repository

```bash
git clone https://github.com/rishikumargl/NarrativeWatch-AI.git
cd NarrativeWatch-AI
```

### 2. Create Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### 3. Setup Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or use your preferred editor
```

**Required variables:**
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/narrativewatch

# APIs
TAVILY_API_KEY=your_tavily_key
INSTAGRAM_API_TOKEN=your_instagram_token
TWITTER_API_KEY=your_twitter_key  # Optional

# Vector AI
VERTEX_AI_PROJECT=your-gcp-project
VERTEX_AI_LOCATION=us-central1

# Logging
LOG_LEVEL=INFO
```

### 4. Install Backend Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python -c "import fastapi; print('FastAPI installed successfully')"
```

### 5. Setup Database (PostgreSQL + pgvector)

**Option A: Using Docker (Recommended)**
```bash
docker run -p 5432:5432 \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=narrativewatch \
  -v postgres_data:/var/lib/postgresql/data \
  pgvector/pgvector:latest
```

**Option B: Local PostgreSQL Installation**
```bash
# macOS with Homebrew
brew install postgresql pgvector

# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# Enable pgvector extension
sudo -u postgres psql -c "CREATE EXTENSION vector;"
```

**Option C: Docker Compose (Full Stack)**
```bash
docker-compose up -d postgres
```

### 6. Initialize Database Schema

```bash
# Run migration scripts (once agents are ready)
python scripts/init_db.py
```

### 7. Setup Frontend

```bash
cd frontend

# Install Node dependencies
npm install

# Start development server (runs on localhost:5173)
npm run dev

# Or build for production
npm run build
```

### 8. Run Backend API

```bash
# From project root
uvicorn src.app:app --reload --host 0.0.0.0 --port 8000
```

API will be available at: `http://localhost:8000`

API Docs: `http://localhost:8000/api/docs`

### 9. Verify Setup

```bash
# Health check
curl http://localhost:8000/health

# API documentation
# Open in browser: http://localhost:8000/api/docs
```

## Development Workflow

### Running Both Frontend and Backend

**Terminal 1 - Backend:**
```bash
# Activate venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Start API
uvicorn src.app:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Terminal 3 - Database (if using Docker):**
```bash
docker-compose up postgres
```

Access the app at: `http://localhost:5173`

### Testing the API

**Using cURL:**
```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "instagram_url": "https://www.instagram.com/bbcnews/",
    "analysis_type": "page"
  }'
```

**Using Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/analyze",
    json={
        "instagram_url": "https://www.instagram.com/bbcnews/",
        "analysis_type": "page"
    }
)
print(response.json())
```

**Using JavaScript/Fetch:**
```javascript
const response = await fetch('http://localhost:8000/api/v1/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    instagram_url: 'https://www.instagram.com/bbcnews/',
    analysis_type: 'page'
  })
});
const data = await response.json();
console.log(data);
```

## Docker Setup (Production-like)

### Build and Run

```bash
# Build image
docker build -t narrativewatch-ai:latest .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:password@localhost:5432/narrativewatch \
  -e TAVILY_API_KEY=your_key \
  narrativewatch-ai:latest
```

### Using Docker Compose (Full Stack)

```bash
# Start all services
docker-compose up --build

# Verify services
docker-compose ps

# View logs
docker-compose logs -f api

# Stop services
docker-compose down

# Clean up volumes
docker-compose down -v
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

### Database Connection Error

```bash
# Check PostgreSQL is running
psql -U postgres -h localhost

# Check pgvector extension
psql -U postgres -d narrativewatch -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Verify connection string in .env
DATABASE_URL=postgresql://username:password@localhost:5432/narrativewatch
```

### Frontend Build Issues

```bash
# Clear npm cache
npm cache clean --force

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Rebuild
npm run build
```

### Python Dependency Conflicts

```bash
# Upgrade pip
pip install --upgrade pip

# Reinstall all dependencies
pip install --force-reinstall -r requirements.txt

# Check for conflicts
pip check
```

## Next Steps

1. **Configure Team Integrations** - Connect with other team members' modules
2. **Test API Endpoints** - Verify all endpoints work with sample data
3. **Frontend Integration** - Ensure frontend calls backend correctly
4. **Load Testing** - Test with concurrent requests
5. **Security Hardening** - Add authentication, rate limiting

## Getting Help

- Check [API_REFERENCE.md](./API_REFERENCE.md) for API documentation
- See [DEPLOYMENT.md](./DEPLOYMENT.md) for production deployment
- Review [LLD_AND_TEAM_PLAN.md](../LLD_AND_TEAM_PLAN.md) for architecture details
- Open an issue on GitHub for bugs

## Useful Commands

```bash
# Backend
pytest tests/                      # Run tests
black src/                        # Format code
mypy src/                         # Type checking
flake8 src/                       # Linting

# Frontend
npm run lint                      # Lint React code
npm run build                     # Build for production
npm run preview                   # Preview production build

# Docker
docker-compose logs api           # View logs
docker-compose exec api bash      # Access container shell
docker-compose down -v            # Remove everything including volumes
```

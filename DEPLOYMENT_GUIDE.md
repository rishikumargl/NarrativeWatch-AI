# NarrativeWatch AI - Deployment Guide

## Overview

This guide covers deploying the NarrativeWatch AI backend to production. The system is containerized with Docker and can be deployed to any platform supporting Docker containers.

---

## Prerequisites

### Local Development
- Python 3.10+
- PostgreSQL 14+ with pgvector extension
- pip (Python package manager)

### Docker Deployment
- Docker 20.10+
- docker-compose 1.29+
- 2GB RAM minimum
- 5GB storage minimum

### Production Requirements
- Google Cloud Project with Vertex AI API enabled
- Instagram Graph API credentials
- Tavily Search API key
- PostgreSQL database (or managed service)

---

## Local Development Setup

### 1. Clone Repository
```bash
git clone https://github.com/rishikumargl/NarrativeWatch-AI.git
cd NarrativeWatch-AI
```

### 2. Create Virtual Environment
```bash
python3.10 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env with your credentials
```

### 5. Initialize Database
```bash
python scripts/init_db.py
```

### 6. Run Development Server
```bash
python src/server.py
```

Server runs on http://localhost:5000

---

## Docker Deployment

### Single Container (Development)

```bash
# Build image
docker build -t narrativewatch-api:latest .

# Run container
docker run -d \
  --name narrativewatch-api \
  -p 5000:5000 \
  -e VERTEX_AI_PROJECT_ID=your-project-id \
  -e INSTAGRAM_ACCESS_TOKEN=your-token \
  -e TAVILY_API_KEY=your-key \
  -e DATABASE_URL=postgresql://user:pass@db:5432/narrativewatch \
  narrativewatch-api:latest
```

### Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

Services:
- **postgres**: PostgreSQL database (port 5432)
- **api**: Flask server (port 5000)

### Health Checks

```bash
# API health
curl http://localhost:5000/health

# Database health
docker-compose ps

# Check logs
docker-compose logs api
```

---

## Environment Configuration

### Required Variables

```env
# Google Cloud
VERTEX_AI_PROJECT_ID=your-gcp-project-id
VERTEX_AI_LOCATION=us-central1

# Database
DATABASE_URL=postgresql://user:password@host:5432/narrativewatch
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

# Instagram API
INSTAGRAM_ACCESS_TOKEN=your-instagram-token
INSTAGRAM_BUSINESS_ACCOUNT_ID=your-account-id

# Tavily Search
TAVILY_API_KEY=your-tavily-api-key

# Server
PORT=5000
DEBUG=False
ENV=production
```

### Optional Variables

```env
# Logging
LOG_LEVEL=INFO

# Database Connection
DB_ECHO=False
DB_POOL_PRE_PING=True
```

---

## API Endpoints

### Health Check
```
GET /health
Response: {"status": "healthy", "components": {...}}
```

### Get Statistics
```
GET /stats
Response: {"status": "success", "data": {"posts": 100, ...}}
```

### Analyze Post
```
POST /analyze/post
Content-Type: application/json

{
  "post_id": "123",
  "page_username": "user",
  "caption": "Post text",
  "hashtags": ["#tag1"],
  "likes": 100,
  "comments": 10
}

Response: {"status": "success", "data": {...}}
```

### Analyze Page
```
POST /analyze/page
Content-Type: application/json

{
  "page_id": "page_123",
  "username": "user",
  "biography": "Page bio",
  "followers": 10000
}

Response: {"status": "success", "data": {...}}
```

---

## Production Deployment

### AWS EC2

```bash
# 1. Launch EC2 (Ubuntu 22.04, t3.medium)
# 2. Install Docker
sudo apt update && sudo apt install -y docker.io docker-compose

# 3. Clone repo
git clone https://github.com/rishikumargl/NarrativeWatch-AI.git
cd NarrativeWatch-AI

# 4. Create .env
nano .env

# 5. Start services
sudo docker-compose up -d
```

### Google Cloud Run

```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/narrativewatch-api
gcloud run deploy narrativewatch-api \
  --image gcr.io/PROJECT_ID/narrativewatch-api \
  --platform managed \
  --region us-central1 \
  --memory 2Gi
```

### Kubernetes

```bash
# Create secrets
kubectl create secret generic narrativewatch-secrets \
  --from-literal=db-url=postgresql://... \
  --from-literal=gcp-project=...

# Deploy
kubectl apply -f deployment.yaml

# Scale
kubectl scale deployment narrativewatch-api --replicas=3
```

---

## Monitoring & Logging

### Docker Logs
```bash
docker-compose logs -f api
docker logs narrativewatch-api
```

### Database Maintenance
```bash
# Check size
docker exec narrativewatch-db psql -U narrativewatch -c \
  "SELECT pg_size_pretty(pg_database_size('narrativewatch'));"

# Vacuum
docker exec narrativewatch-db psql -U narrativewatch -c "VACUUM ANALYZE;"
```

---

## Backup & Recovery

### Database Backup
```bash
docker exec narrativewatch-db pg_dump \
  -U narrativewatch narrativewatch > backup_$(date +%Y%m%d).sql
```

### Database Restore
```bash
docker exec -i narrativewatch-db psql -U narrativewatch narrativewatch < backup.sql
```

---

## Performance Tuning

### Connection Pool
```python
# In postgres_client.py
pool_config = {
    "pool_size": 20,        # Increase for more concurrent requests
    "max_overflow": 40,
    "pool_pre_ping": True,
}
```

### Gunicorn Workers
```bash
# Workers = (2 * CPU_CORES) + 1
gunicorn --workers 5 --bind 0.0.0.0:5000 src.server:app
```

---

## Security Checklist

- [ ] HTTPS/TLS enabled
- [ ] Secrets in environment variables (not in code)
- [ ] Database encrypted at rest
- [ ] Regular backups verified
- [ ] Firewall restricts access
- [ ] Rate limiting configured
- [ ] SQL injection prevention (SQLAlchemy ORM)
- [ ] CORS configured properly
- [ ] Input validation (Pydantic)
- [ ] API authentication/authorization
- [ ] Monitoring and alerting active

---

## Troubleshooting

### Connection Refused
```bash
docker ps | grep narrativewatch
docker-compose restart api
docker-compose logs api
```

### Database Error
```bash
docker-compose ps postgres
docker exec narrativewatch-db psql -U narrativewatch -d narrativewatch -c "SELECT 1;"
```

### Health Check Failing
```bash
curl http://localhost:5000/health
docker logs narrativewatch-api
```

### High Memory
```bash
docker stats narrativewatch-api
docker-compose up -d --scale api=1
```

---

## Rollback

```bash
# Tag previous version
docker tag narrativewatch-api:latest narrativewatch-api:v1.0.0

# Deploy previous
docker pull narrativewatch-api:v1.0.0
docker-compose down
export DOCKER_IMAGE=narrativewatch-api:v1.0.0
docker-compose up -d

# Verify
curl http://localhost:5000/health
```

---

## Next Steps

1. Set up CI/CD (GitHub Actions)
2. Add monitoring (Prometheus, Grafana)
3. Configure alerting (PagerDuty)
4. Add authentication (JWT)
5. Implement rate limiting (Redis)
6. Setup logging (ELK Stack)
7. Add tracing (Jaeger)

---

**For support**, refer to BACKEND_DOCUMENTATION.md or create a GitHub issue.

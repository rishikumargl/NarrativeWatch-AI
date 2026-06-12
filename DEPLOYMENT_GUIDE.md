# NarrativeWatch AI - Deployment Guide

## Overview

This guide covers deploying the NarrativeWatch AI backend to production. The system runs as a standard Flask application with a PostgreSQL database.

---

## Prerequisites

### Local Development & Production
- Python 3.10+
- PostgreSQL 14+ with pgvector extension
- pip (Python package manager)
- 2GB RAM minimum
- 5GB storage minimum

### External Services Required
- Google Cloud Project with Vertex AI API enabled
- Instagram Graph API credentials
- Tavily Search API key

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
# Edit .env with your credentials:
# - VERTEX_AI_PROJECT_ID
# - DATABASE_URL (PostgreSQL connection string)
# - INSTAGRAM_ACCESS_TOKEN
# - TAVILY_API_KEY
```

### 5. Setup PostgreSQL Database

```bash
# Install PostgreSQL 14+ with pgvector extension
# https://github.com/pgvector/pgvector

# Create database
createdb -U postgres narrativewatch

# Install pgvector extension
psql -U postgres -d narrativewatch -c "CREATE EXTENSION vector;"

# Initialize schema
python scripts/init_db.py
```

### 6. Run Development Server
```bash
python src/server.py
```

Server runs on http://localhost:5000

### 7. Verify Installation

```bash
# Health check
curl http://localhost:5000/health

# Get stats
curl http://localhost:5000/stats

# Example analysis
curl -X POST http://localhost:5000/analyze/post \
  -H "Content-Type: application/json" \
  -d '{
    "post_id": "test_123",
    "page_username": "testuser",
    "caption": "Test content",
    "hashtags": ["#test"],
    "likes": 100,
    "comments": 10
  }'
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
# 1. Launch EC2 instance (Ubuntu 22.04, t2.medium+)
ssh -i key.pem ubuntu@your-instance-ip

# 2. Install dependencies
sudo apt update
sudo apt install -y python3.10 python3-pip postgresql postgresql-contrib
sudo apt install -y postgresql-14-pgvector

# 3. Clone repository
git clone https://github.com/rishikumargl/NarrativeWatch-AI.git
cd NarrativeWatch-AI

# 4. Setup Python virtual environment
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Configure PostgreSQL
sudo su - postgres
createdb narrativewatch
psql -d narrativewatch -c "CREATE EXTENSION vector;"
exit

# 6. Create .env file
cp .env.example .env
nano .env  # Add your credentials

# 7. Initialize database
python scripts/init_db.py

# 8. Run with systemd (production)
# Create /etc/systemd/system/narrativewatch.service:
sudo nano /etc/systemd/system/narrativewatch.service
```

### Systemd Service Setup

Create `/etc/systemd/system/narrativewatch.service`:

```ini
[Unit]
Description=NarrativeWatch AI Backend
After=network.target postgresql.service

[Service]
Type=notify
User=ubuntu
WorkingDirectory=/home/ubuntu/NarrativeWatch-AI
Environment="PATH=/home/ubuntu/NarrativeWatch-AI/venv/bin"
EnvironmentFile=/home/ubuntu/NarrativeWatch-AI/.env
ExecStart=/home/ubuntu/NarrativeWatch-AI/venv/bin/python src/server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable narrativewatch
sudo systemctl start narrativewatch
sudo systemctl status narrativewatch
```

### Google Cloud Compute Engine

```bash
# 1. Create VM instance
gcloud compute instances create narrativewatch-api \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --machine-type=e2-medium \
  --zone=us-central1-a

# 2. SSH into instance
gcloud compute ssh narrativewatch-api --zone=us-central1-a

# 3. Install dependencies (same as AWS EC2 above)
```

### Heroku Deployment

```bash
# 1. Create Heroku app
heroku create narrativewatch-api

# 2. Add PostgreSQL addon
heroku addons:create heroku-postgresql:standard-0

# 3. Set environment variables
heroku config:set VERTEX_AI_PROJECT_ID=your-project-id
heroku config:set INSTAGRAM_ACCESS_TOKEN=your-token
heroku config:set TAVILY_API_KEY=your-key

# 4. Create Procfile
echo "web: python src/server.py" > Procfile

# 5. Deploy
git push heroku main
```

---

## Monitoring & Logging

### Application Logs

```bash
# With systemd
sudo journalctl -u narrativewatch -f

# Direct output (development)
tail -f ~/.narrativewatch/app.log
```

### Database Monitoring

```bash
# Connect to PostgreSQL
psql -U postgres -d narrativewatch

# Check database size
SELECT pg_size_pretty(pg_database_size('narrativewatch'));

# Check connections
SELECT count(*) FROM pg_stat_activity;

# Check table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) 
FROM pg_tables ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

# Vacuum and analyze
VACUUM ANALYZE;
```

---

## Backup & Recovery

### Database Backup

```bash
# Daily backup
pg_dump -U postgres narrativewatch > backup_$(date +%Y%m%d).sql

# Compressed backup
pg_dump -U postgres narrativewatch | gzip > backup_$(date +%Y%m%d).sql.gz

# Automated backup (cron)
# Add to crontab: 0 2 * * * pg_dump -U postgres narrativewatch | gzip > /backups/db_$(date +\%Y\%m\%d).sql.gz
```

### Database Restore

```bash
# From backup
psql -U postgres narrativewatch < backup_20260612.sql

# From compressed backup
gunzip -c backup_20260612.sql.gz | psql -U postgres narrativewatch
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

### API Not Starting
```bash
# Check systemd logs
sudo journalctl -u narrativewatch -n 50

# Check if port is in use
sudo netstat -tulpn | grep 5000

# Check Python errors
python src/server.py  # Run directly to see errors
```

### Database Connection Error
```bash
# Verify PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -U postgres -d narrativewatch -c "SELECT 1;"

# Check .env DATABASE_URL
grep DATABASE_URL .env

# Verify pgvector extension
psql -U postgres -d narrativewatch -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
```

### API Health Check Failing
```bash
# Test endpoint
curl http://localhost:5000/health

# Check if service is running
sudo systemctl status narrativewatch

# View recent logs
sudo journalctl -u narrativewatch -n 20 -e
```

### Environment Variables Not Loaded
```bash
# Check .env file
cat .env

# Verify variables are set in systemd
sudo systemctl cat narrativewatch

# Manually set in session
source .env
python src/server.py
```

---

## Rollback to Previous Version

```bash
# 1. Stop current version
sudo systemctl stop narrativewatch

# 2. Checkout previous commit
git log --oneline  # Find commit hash
git checkout <commit-hash>

# 3. Restart
sudo systemctl start narrativewatch

# 4. Verify
curl http://localhost:5000/health
```

---

## Performance Tuning

### Application Configuration

```python
# src/server.py - Adjust for your server:

# Worker configuration
workers = (2 * cpu_count()) + 1  # For multi-process

# Connection pool (in src/database/postgres_client.py)
pool_size = 20        # Increase for more concurrency
max_overflow = 40     # Overflow connections
pool_pre_ping = True  # Health checks
```

### PostgreSQL Tuning

```sql
-- For 2GB RAM server, run as postgres:
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET work_mem = '4MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';

-- Apply changes
SELECT pg_reload_conf();
```

---

## Next Steps

1. Set up CI/CD (GitHub Actions)
2. Add monitoring (ELK, Datadog, New Relic)
3. Configure alerting (PagerDuty, Opsgenie)
4. Add authentication (JWT)
5. Implement rate limiting (custom middleware)
6. Setup centralized logging
7. Add APM tracing

---

**For support**, refer to BACKEND_DOCUMENTATION.md or create a GitHub issue.

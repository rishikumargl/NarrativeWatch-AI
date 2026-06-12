# NarrativeWatch AI - Deployment Guide

Production deployment and operational guide for NarrativeWatch AI.

## Table of Contents
1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Docker Deployment](#docker-deployment)
3. [Cloud Deployment](#cloud-deployment)
4. [Environment Configuration](#environment-configuration)
5. [Monitoring & Logging](#monitoring--logging)
6. [Scaling](#scaling)
7. [Backup & Recovery](#backup--recovery)

---

## Pre-Deployment Checklist

Before deploying to production:

- [ ] All tests passing (`pytest tests/ -v`)
- [ ] Code linting passed (`flake8 src/`)
- [ ] Type checking passed (`mypy src/`)
- [ ] Security scan completed
- [ ] Docker image builds successfully
- [ ] Environment variables configured
- [ ] Database migrations tested
- [ ] API endpoints verified
- [ ] Frontend build completed
- [ ] Documentation updated

---

## Docker Deployment

### Building the Docker Image

```bash
# Build for production
docker build -t narrativewatch-ai:latest .
docker tag narrativewatch-ai:latest narrativewatch-ai:v1.0.0

# Push to registry (optional)
docker push your-registry/narrativewatch-ai:latest
```

### Running Single Container

```bash
docker run -d \
  --name narrativewatch-api \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:pass@db:5432/narrativewatch" \
  -e TAVILY_API_KEY="your-key" \
  -e VERTEX_AI_PROJECT="your-project" \
  --health-cmd='curl -f http://localhost:8000/health || exit 1' \
  --health-interval=30s \
  --health-timeout=10s \
  --health-retries=3 \
  narrativewatch-ai:latest
```

### Docker Compose Deployment

```bash
# Start all services
docker-compose -f docker-compose.yml up -d

# Start with environment override
docker-compose --env-file .env.production up -d

# Monitor
docker-compose logs -f api
docker-compose ps

# Graceful shutdown
docker-compose stop
docker-compose down
```

---

## Cloud Deployment

### Google Cloud Run

```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/narrativewatch-ai

# Deploy to Cloud Run
gcloud run deploy narrativewatch-ai \
  --image gcr.io/PROJECT_ID/narrativewatch-ai \
  --platform managed \
  --region us-central1 \
  --memory 1Gi \
  --cpu 1 \
  --timeout 300 \
  --set-env-vars DATABASE_URL="postgresql://..." \
  --allow-unauthenticated
```

### AWS ECS/Fargate

```bash
# Create ECR repository
aws ecr create-repository --repository-name narrativewatch-ai

# Build and push
docker build -t narrativewatch-ai:latest .
docker tag narrativewatch-ai:latest ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/narrativewatch-ai:latest
aws ecr get-login-password --region REGION | docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com
docker push ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/narrativewatch-ai:latest

# Create ECS task definition and service
# (Use AWS Console or CloudFormation)
```

### Kubernetes Deployment

```bash
# Create ConfigMap for environment
kubectl create configmap narrativewatch-config \
  --from-env-file=.env.production

# Apply deployment manifest
kubectl apply -f k8s/deployment.yaml

# Check deployment
kubectl get pods -l app=narrativewatch-ai
kubectl logs -f deployment/narrativewatch-api
```

**k8s/deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: narrativewatch-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: narrativewatch-ai
  template:
    metadata:
      labels:
        app: narrativewatch-ai
    spec:
      containers:
      - name: api
        image: narrativewatch-ai:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: narrativewatch-config
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
```

---

## Environment Configuration

### Production Environment Variables

Create `.env.production`:

```env
# Application
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://user:password@db.example.com:5432/narrativewatch
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40

# APIs
TAVILY_API_KEY=sk_...
INSTAGRAM_API_TOKEN=EAAX...
TWITTER_API_KEY=xxx
VERTEX_AI_PROJECT=my-project
VERTEX_AI_LOCATION=us-central1

# Security
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=https://example.com,https://www.example.com
CORS_CREDENTIALS=true
CORS_METHODS=POST,GET,OPTIONS
CORS_HEADERS=Content-Type,Authorization

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_PER_HOUR=1000

# Caching
REDIS_URL=redis://cache.example.com:6379/0
CACHE_TTL=3600

# Monitoring
SENTRY_DSN=https://...@sentry.io/...
NEW_RELIC_LICENSE_KEY=...

# Frontend
FRONTEND_BUILD_PATH=/app/frontend/dist
SERVE_FRONTEND=true
```

### Secrets Management

Use a secrets manager instead of .env files in production:

```bash
# AWS Secrets Manager
aws secretsmanager create-secret --name narrativewatch/db-url \
  --secret-string "postgresql://..."

# Google Cloud Secret Manager
gcloud secrets create narrativewatch-db-url \
  --replication-policy="automatic" \
  --data-file=-

# HashiCorp Vault
vault kv put secret/narrativewatch/db database_url=...
```

---

## Monitoring & Logging

### Application Logging

```bash
# View logs
docker-compose logs -f api

# Log rotation
docker-compose exec api tail -f /var/log/narrativewatch.log

# Structured logging (JSON)
export LOG_FORMAT=json
docker-compose up
```

### Health Monitoring

```bash
# Health check endpoint
curl http://localhost:8000/health

# Metrics endpoint (future)
curl http://localhost:8000/metrics
```

### Sentry Error Tracking

```python
import sentry_sdk

sentry_sdk.init(
    dsn="https://xxx@sentry.io/yyy",
    traces_sample_rate=0.1,
    environment="production"
)
```

### Database Monitoring

```bash
# Check database connections
psql -h localhost -U narrativewatch_user -d narrativewatch
SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;

# Check vector index performance
SELECT * FROM pg_stat_user_indexes WHERE relname LIKE '%embedding%';
```

---

## Scaling

### Horizontal Scaling (Multiple Instances)

```bash
# Load balancer configuration (nginx)
upstream narrativewatch {
  server api1:8000;
  server api2:8000;
  server api3:8000;
}

server {
  listen 80;
  server_name api.example.com;
  
  location / {
    proxy_pass http://narrativewatch;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
  }
}
```

### Database Scaling

```bash
# Connection pooling with PgBouncer
# pgbouncer.ini
[databases]
narrativewatch = host=db.example.com port=5432 dbname=narrativewatch

[pgbouncer]
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 25
```

### Caching Layer (Redis)

```bash
# Add Redis for response caching
docker run -d --name redis -p 6379:6379 redis:7-alpine

# Configure in .env
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=3600
```

---

## Backup & Recovery

### Database Backups

```bash
# Full backup
pg_dump -U narrativewatch_user -h localhost narrativewatch > backup.sql

# Restore from backup
psql -U narrativewatch_user -h localhost narrativewatch < backup.sql

# Automated backups (cron)
0 2 * * * pg_dump -U narrativewatch_user narrativewatch | gzip > /backups/narrativewatch-$(date +\%Y\%m\%d).sql.gz
```

### Docker Volume Backups

```bash
# Backup volume
docker run --rm -v narrativewatch_postgres_data:/data -v $(pwd):/backup \
  busybox tar czf /backup/postgres-backup.tar.gz /data

# Restore volume
docker run --rm -v narrativewatch_postgres_data:/data -v $(pwd):/backup \
  busybox tar xzf /backup/postgres-backup.tar.gz -C /
```

### Disaster Recovery Plan

1. **RTO (Recovery Time Objective):** 15 minutes
2. **RPO (Recovery Point Objective):** 1 hour
3. **Backup Location:** Separate cloud storage (S3, GCS)
4. **Test Recovery:** Monthly

---

## Performance Optimization

### API Response Caching

```python
# Cache expensive analysis results
from fastapi_cache2 import FastAPICache2
from fastapi_cache2.backends.redis import RedisBackend

@cached(namespace="analysis", expire=3600)
@app.post("/api/v1/analyze")
async def analyze_instagram(request: AnalysisRequest):
    # ...
```

### Database Query Optimization

```bash
# Analyze slow queries
SELECT query, calls, mean_time FROM pg_stat_statements 
ORDER BY mean_time DESC LIMIT 10;

# Optimize vector search indexes
CREATE INDEX ON instagram_posts USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);
```

### Frontend Optimization

```bash
# Gzip compression
gzip on;
gzip_types text/plain text/css text/javascript application/json;
gzip_min_length 1024;

# Browser caching
add_header Cache-Control "public, max-age=3600";
```

---

## Troubleshooting Deployment

### Container won't start

```bash
# Check logs
docker logs narrativewatch-api

# Debug container
docker run -it narrativewatch-ai:latest /bin/bash

# Check health
docker inspect --format='{{.State.Health.Status}}' narrativewatch-api
```

### Database connection failed

```bash
# Verify connectivity
nc -zv db.example.com 5432

# Check credentials
psql "postgresql://user:password@db.example.com/narrativewatch"

# Test from container
docker-compose exec api psql $DATABASE_URL
```

### Performance degradation

```bash
# Check CPU/Memory
docker stats narrativewatch-api

# Profile application
python -m cProfile -s cumulative src/app.py

# Monitor database
psql -x << EOF
SELECT * FROM pg_stat_database WHERE datname = 'narrativewatch';
SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;
EOF
```

---

## Security Hardening

### SSL/TLS

```bash
# Generate certificate (Let's Encrypt)
certbot certonly --standalone -d api.example.com

# Update Docker to use HTTPS
docker run -d \
  -p 443:8000 \
  -v /etc/letsencrypt/live/api.example.com/fullchain.pem:/app/cert.pem \
  -v /etc/letsencrypt/live/api.example.com/privkey.pem:/app/key.pem \
  narrativewatch-ai:latest
```

### Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/v1/analyze")
@limiter.limit("10/minute")
async def analyze_instagram(request: AnalysisRequest):
    pass
```

### Input Validation

Already implemented in `src/models/request.py` with Pydantic.

---

## Rollback Procedure

```bash
# Identify current version
docker inspect narrativewatch-api:latest | grep RepoTags

# Switch to previous version
docker pull narrativewatch-ai:v1.0.0
docker-compose -f docker-compose.yml down
docker tag narrativewatch-ai:v1.0.0 narrativewatch-ai:latest
docker-compose up -d

# Verify rollback
curl http://localhost:8000/health
```

---

## Support

For deployment issues:
1. Check logs: `docker-compose logs -f api`
2. Review [SETUP_GUIDE.md](./SETUP_GUIDE.md)
3. Check [API_REFERENCE.md](./API_REFERENCE.md)
4. Open issue on GitHub

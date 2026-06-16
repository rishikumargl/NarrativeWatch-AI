# Database Information - NarrativeWatch AI

## Database Details

### **Database Type**
**PostgreSQL** (Open-source relational database)

### **Database Name**
```
narrativewatch_ai
```

### **Connection Details**

```
Host: localhost
Port: 5432
Username: narrativewatch
Password: password
Database: narrativewatch_ai
```

### **Full Connection String**
```
postgresql://narrativewatch:password@localhost:5432/narrativewatch_ai
```

---

## How to Connect

### **Using psql (Command Line)**
```bash
psql -U narrativewatch -d narrativewatch_ai -h localhost
# When prompted for password, enter: password
```

### **Using Python**
```python
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://narrativewatch:password@localhost:5432/narrativewatch_ai"
)
connection = engine.connect()
```

### **Using PostgreSQL GUI (pgAdmin)**
```
Server: localhost
Port: 5432
Username: narrativewatch
Password: password
Database: narrativewatch_ai
```

---

## Database Tables

### **1. news_article_analyses**
Stores analysis results for articles

**Columns:**
```
id (INT, PRIMARY KEY)
url (VARCHAR 1000, UNIQUE)
title (VARCHAR 500)
content (TEXT)
analysis_result (TEXT)
summary (TEXT)
trust_score (FLOAT)
risk_level (VARCHAR 50)
sentiment_score (FLOAT)
entities (TEXT[])
source_domain (VARCHAR 255)
author (VARCHAR 255)
publish_date (DATE)
content_bias_score (FLOAT)
bot_probability (FLOAT)
misinformation_risk (FLOAT)
verification_status (VARCHAR 50)
corroboration_score (FLOAT)
similar_articles_count (INT)
synthesis_report (TEXT)
synthesis_model (VARCHAR 100)
synthesis_timestamp (TIMESTAMP)
review_status (VARCHAR 50)
review_feedback (TEXT)
review_model (VARCHAR 100)
review_timestamp (TIMESTAMP)
reflection_iterations (INT)
content_embedding (vector(1536))
analysis_timestamp (TIMESTAMP)
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
```

**Indexes:**
```
idx_news_analyses_url
idx_news_analyses_trust_score
idx_news_analyses_risk_level
idx_news_analyses_analysis_timestamp
pgvector index on content_embedding (ivfflat)
```

---

### **2. documents**
Stores uploaded documents for RAG system

**Columns:**
```
id (INT, PRIMARY KEY)
title (VARCHAR 500)
content (TEXT)
source_url (VARCHAR 1000, UNIQUE)
source_domain (VARCHAR 255)
author (VARCHAR 255)
publish_date (DATE)
category (VARCHAR 100)
tags (JSON)
document_hash (VARCHAR 64, UNIQUE)
content_embedding (vector(1536))
ingestion_timestamp (TIMESTAMP)
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
```

**Indexes:**
```
idx_documents_source_domain
idx_documents_category
idx_documents_ingestion_timestamp
pgvector index on content_embedding (ivfflat)
```

---

## Vector Extension (pgvector)

### **What is pgvector?**
PostgreSQL extension for storing and searching vector embeddings (1,536 dimensions)

### **Used For:**
- Semantic similarity search for RAG retrieval
- Finding similar articles based on content meaning
- Entity relationship queries
- Context enrichment

### **Query Example:**
```sql
-- Find similar articles (similarity > 0.5)
SELECT title, content, 
       1 - (content_embedding <-> '[0.234, -0.156, ...]'::vector) as similarity
FROM documents
WHERE 1 - (content_embedding <-> '[0.234, -0.156, ...]'::vector) > 0.5
ORDER BY similarity DESC
LIMIT 5;
```

---

## Configuration

### **In config.py**
```python
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://narrativewatch:password@localhost:5432/narrativewatch_ai"
)
```

### **Environment Variables**
```
DATABASE_URL=postgresql://narrativewatch:password@localhost:5432/narrativewatch_ai
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
```

### **Connection Pool Settings**
```
Pool Size: 20 (default connections)
Max Overflow: 10 (additional connections if needed)
Total: Up to 30 concurrent connections
```

---

## Database Management

### **Check Connection**
```bash
# Test connection
psql -U narrativewatch -d narrativewatch_ai -h localhost -c "SELECT version();"
```

### **View All Tables**
```sql
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public';
```

### **Check Row Counts**
```sql
SELECT 
    'news_article_analyses' as table_name,
    COUNT(*) as row_count
FROM news_article_analyses
UNION ALL
SELECT 
    'documents' as table_name,
    COUNT(*) as row_count
FROM documents;
```

### **View Indexes**
```sql
SELECT indexname FROM pg_indexes 
WHERE schemaname = 'public';
```

### **Check Vector Extension**
```sql
-- Verify pgvector is installed
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Check vector columns
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE data_type LIKE '%vector%';
```

---

## Data Flow in Database

### **When Article is Analyzed**
```
1. Extract URL data (title, entities, content)
2. Query documents table for similar articles (RAG)
3. Retrieve entity reputation from news_article_analyses
4. Retrieve source baseline from news_article_analyses
5. Combine all context
6. Pass to agents for analysis
7. Save results to news_article_analyses
   ├─ trust_score
   ├─ risk_level
   ├─ synthesis_report
   ├─ review_status
   ├─ content_embedding
   └─ analysis_timestamp
```

### **When Documents are Uploaded**
```
1. Receive document from frontend
2. Generate MD5 hash for deduplication
3. Check if already exists (document_hash)
4. Generate embedding (1,536 dimensions)
5. Save to documents table
   ├─ title
   ├─ content
   ├─ content_embedding
   ├─ document_hash
   └─ ingestion_timestamp
6. Create pgvector index for search
```

### **When RAG Context is Retrieved**
```
1. Query news_article_analyses for entity reputation
   └─ 90-day lookback
2. Query news_article_analyses for source baseline
   └─ 180-day lookback
3. Generate embedding for new article
4. Query documents table for similar articles
   └─ pgvector similarity search > 0.5
5. Return combined context
```

---

## Backup & Maintenance

### **Backup Database**
```bash
pg_dump -U narrativewatch -d narrativewatch_ai > backup.sql
```

### **Restore Database**
```bash
psql -U narrativewatch -d narrativewatch_ai < backup.sql
```

### **Check Database Size**
```sql
SELECT 
    pg_database.datname,
    pg_size_pretty(pg_database_size(pg_database.datname)) as size
FROM pg_database
WHERE datname = 'narrativewatch_ai';
```

### **Vacuum & Analyze** (Maintenance)
```sql
VACUUM ANALYZE;
```

---

## Performance Optimization

### **pgvector Index Type: ivfflat**
```
Inverted File Flat Index
- Fast approximate similarity search
- Good for 1,536-dimensional vectors
- Trade-off: Speed vs. accuracy
- Suitable for RAG retrieval
```

### **Query Optimization**
```sql
-- Before: Full table scan
SELECT * FROM documents WHERE content_embedding <-> embedding > 0.5;

-- After: Uses ivfflat index
SELECT * FROM documents 
WHERE content_embedding <-> embedding > 0.5
LIMIT 5;
```

---

## Summary

| Property | Value |
|----------|-------|
| **Database Type** | PostgreSQL |
| **Database Name** | narrativewatch_ai |
| **Host** | localhost |
| **Port** | 5432 |
| **Username** | narrativewatch |
| **Password** | password |
| **Tables** | 2 (news_article_analyses, documents) |
| **Vector Extension** | pgvector (1,536 dimensions) |
| **Indexes** | Multiple (including ivfflat for vectors) |
| **Connection Pool Size** | 20 |
| **Max Connections** | 30 |

---

## Connection String Formats

### **SQLAlchemy (Python)**
```
postgresql://narrativewatch:password@localhost:5432/narrativewatch_ai
```

### **psycopg2 (Python)**
```
host=localhost port=5432 database=narrativewatch_ai user=narrativewatch password=password
```

### **JDBC (Java)**
```
jdbc:postgresql://localhost:5432/narrativewatch_ai?user=narrativewatch&password=password
```

### **Node.js (pg)**
```javascript
{
  user: 'narrativewatch',
  password: 'password',
  host: 'localhost',
  port: 5432,
  database: 'narrativewatch_ai'
}
```

---

## Common Database Queries

### **Get Recent Analyses**
```sql
SELECT title, trust_score, risk_level, analysis_timestamp
FROM news_article_analyses
ORDER BY analysis_timestamp DESC
LIMIT 10;
```

### **Find High Trust Articles**
```sql
SELECT title, trust_score, author, source_domain
FROM news_article_analyses
WHERE trust_score > 0.8
ORDER BY trust_score DESC;
```

### **Count Documents by Domain**
```sql
SELECT source_domain, COUNT(*) as count
FROM documents
GROUP BY source_domain
ORDER BY count DESC;
```

### **Get Entity Reputation**
```sql
SELECT 
    jsonb_array_elements(entities) as entity,
    AVG(trust_score) as avg_trust,
    COUNT(*) as mentions
FROM news_article_analyses
WHERE entities IS NOT NULL
GROUP BY entity
ORDER BY avg_trust DESC;
```

---

**Status:** PostgreSQL database fully configured and operational ✅

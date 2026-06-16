# Auto Database Initialization - How It Works

## YES! Database Creation IS Automatic ✅

The backend **automatically handles database creation** when you run it!

---

## How It Works

### **Step 1: Backend Startup** (in app.py)
```python
@app.on_event("startup")
async def startup_event():
    try:
        init_db()  # ← Called on startup
        logger.info("✅ Database connected")
    except Exception as e:
        logger.warning(f"Database optional: {e}")
```

### **Step 2: Database Creation** (in postgres_client.py)
```python
def _create_database_if_not_exists(self):
    """Create database if it doesn't exist."""
    # 1. Connect to default 'postgres' database
    # 2. Check if 'narrativewatch_ai' exists
    # 3. If NOT exists:
    #    - CREATE DATABASE narrativewatch_ai
    #    - Log: "Created database: narrativewatch_ai"
    # 4. If exists: Skip creation
```

### **Step 3: Table Creation** (in connection.py)
```python
def init_db():
    """Initialize database tables."""
    # 1. Enable pgvector extension
    #    - CREATE EXTENSION IF NOT EXISTS vector
    
    # 2. Create all tables from models
    #    - Base.metadata.create_all(bind=engine)
    #    
    #    Tables created:
    #    ✓ news_article_analyses
    #    ✓ documents
    #    
    #    Indexes created:
    #    ✓ Entity indexes
    #    ✓ pgvector ivfflat indexes
```

---

## What You Need Before Running Backend

### **IMPORTANT: You MUST Have:**

1. **PostgreSQL Server Running**
   - Should be running on localhost:5432
   - With admin user 'postgres' and password 'password'
   
2. **That's It!** Everything else is automatic

---

## Complete Auto-Initialization Flow

```
Backend Startup
    ↓
postgres_client.py initialized
    ↓
_create_database_if_not_exists()
    ├─ Parse database URL
    │  └─ Extract: narrativewatch_ai
    ├─ Connect to default 'postgres' DB
    │  └─ Use: postgres / password
    ├─ Check if 'narrativewatch_ai' exists
    │  └─ Query: SELECT 1 FROM pg_database WHERE datname = 'narrativewatch_ai'
    ├─ If NOT exists:
    │  └─ CREATE DATABASE narrativewatch_ai
    │     └─ Owner: postgres (initially)
    └─ Close connection
    ↓
connection.py init_db() called
    ├─ CREATE EXTENSION IF NOT EXISTS vector
    │  └─ Enables pgvector for embeddings
    ├─ Base.metadata.create_all()
    │  ├─ CREATE TABLE news_article_analyses
    │  ├─ CREATE TABLE documents
    │  ├─ CREATE INDEXES
    │  └─ CREATE pgvector indexes (ivfflat)
    └─ Log: "Database tables created"
    ↓
✅ Database ready for use
    ├─ All tables exist
    ├─ All indexes created
    ├─ pgvector extension enabled
    └─ Ready to upload documents and analyze
```

---

## What Gets Created Automatically

### **Database**
```
Name: narrativewatch_ai
Owner: postgres (can be changed)
Extensions: pgvector
```

### **Tables**

#### **1. news_article_analyses**
```sql
CREATE TABLE news_article_analyses (
    id SERIAL PRIMARY KEY,
    url VARCHAR(1000) UNIQUE,
    title VARCHAR(500),
    content TEXT,
    trust_score FLOAT,
    risk_level VARCHAR(50),
    ... (30+ columns)
    content_embedding vector(1536),
    analysis_timestamp TIMESTAMP,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Indexes created:
CREATE INDEX idx_news_analyses_url ON news_article_analyses(url);
CREATE INDEX idx_news_analyses_trust_score ON news_article_analyses(trust_score);
CREATE INDEX idx_news_analyses_risk_level ON news_article_analyses(risk_level);
CREATE INDEX idx_news_analyses_analysis_timestamp ON news_article_analyses(analysis_timestamp);
CREATE INDEX idx_news_analyses_embedding ON news_article_analyses USING ivfflat (content_embedding);
```

#### **2. documents**
```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500),
    content TEXT,
    source_url VARCHAR(1000) UNIQUE,
    source_domain VARCHAR(255),
    author VARCHAR(255),
    publish_date DATE,
    category VARCHAR(100),
    tags JSON,
    document_hash VARCHAR(64) UNIQUE,
    content_embedding vector(1536),
    ingestion_timestamp TIMESTAMP,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Indexes created:
CREATE INDEX idx_documents_source_domain ON documents(source_domain);
CREATE INDEX idx_documents_category ON documents(category);
CREATE INDEX idx_documents_ingestion_timestamp ON documents(ingestion_timestamp);
CREATE INDEX idx_documents_embedding ON documents USING ivfflat (content_embedding);
```

---

## Expected Backend Startup Output

### **SUCCESS (Database auto-created):**
```
[INFO] Connecting to PostgreSQL: localhost:5432/narrativewatch_ai
[INFO] [OK] Created database: narrativewatch_ai
[INFO] Database tables created
[INFO] ✅ Database connected
[INFO] ✅ HuggingFace Inference API initialized
[INFO] ✅ Groq AI initialized
[INFO] ✅ 4 specialized agents ready
[INFO] ✅ WebSocket real-time updates enabled
[INFO] 🎉 NARRATIVEWATCH AI READY FOR ANALYSIS!
[INFO] Uvicorn running on http://0.0.0.0:8000
```

### **If PostgreSQL Not Running:**
```
[ERROR] Could not connect to PostgreSQL
[WARNING] ⚠️  Database optional (can still analyze): connection refused
[INFO] Backend started (database optional)
```

---

## How to Run (Simple!)

### **Step 1: Make Sure PostgreSQL is Running**
```bash
# Check if PostgreSQL is running
# On Windows: Services app or PostgreSQL installer
# On Mac: brew services start postgresql
# On Linux: systemctl start postgresql
```

### **Step 2: Start Backend**
```bash
cd backend
python -m uvicorn src.app:app --reload
```

### **Step 3: Watch the Logs**
```
You should see:
✅ Created database: narrativewatch_ai  (if first run)
✅ Database tables created
✅ Database connected
✅ NARRATIVEWATCH AI READY FOR ANALYSIS!
```

### **Step 4: Database is Ready!**
```bash
# Verify in pgAdmin:
# 1. Refresh Servers
# 2. Expand your PostgreSQL server
# 3. Look under "Databases"
# 4. You should see: narrativewatch_ai ✓
```

---

## Configuration

### **Database URL** (in config.py)
```python
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://narrativewatch:password@localhost:5432/narrativewatch_ai"
)
```

### **Connection Pool Settings**
```python
pool_size=20          # Default connections
max_overflow=10       # Extra connections if needed
pool_pre_ping=True    # Verify connections before use
```

---

## What Gets Created AFTER First Upload

### **When Documents Are Uploaded:**
```
1. Database already exists ✓
2. Tables already exist ✓
3. When you upload documents:
   ├─ Generate embeddings
   ├─ INSERT into documents table
   ├─ Create vector index
   └─ Ready for RAG retrieval ✓

4. When you analyze articles:
   ├─ RAG retrieves similar documents
   ├─ Query entity reputation
   ├─ INSERT into news_article_analyses
   ├─ Generate content embedding
   └─ Store in database ✓
```

---

## Troubleshooting Auto-Initialization

### **Issue: "Connection refused"**
```
Cause: PostgreSQL not running
Fix: Start PostgreSQL service
```

### **Issue: "FATAL: password authentication failed"**
```
Cause: Wrong postgres password
Fix: Use correct PostgreSQL admin password in .env:
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/narrativewatch_ai
```

### **Issue: "ERROR: permission denied to create database"**
```
Cause: postgres user doesn't have permissions
Fix: Use admin/superuser account, or grant permissions
```

### **Issue: "Extension 'vector' not found"**
```
Cause: pgvector extension not installed
Fix: Install pgvector extension first:
CREATE EXTENSION pgvector;
```

---

## Summary

✅ **You DO NOT need to manually create database!**

✅ **Backend automatically:**
- Creates database (narrativewatch_ai)
- Creates tables (news_article_analyses, documents)
- Enables pgvector extension
- Creates all indexes
- Tests connection

✅ **All you need:**
- PostgreSQL running (localhost:5432)
- Admin credentials (postgres / password)
- Run: `python -m uvicorn src.app:app --reload`

✅ **Result:**
- Database ready ✓
- Tables created ✓
- Ready to upload documents ✓
- Ready to analyze articles ✓

---

## Timeline

```
Before: Database doesn't exist
    ↓
Run backend: python -m uvicorn src.app:app --reload
    ↓
Backend checks: Does narrativewatch_ai exist?
    ↓
No? Create it! (2-3 seconds)
    ↓
Create tables (1-2 seconds)
    ↓
Enable pgvector extension (1 second)
    ↓
Ready! (5-10 seconds total)
    ↓
After: Database fully functional
```

---

**Status:** Auto-initialization is working ✅

Just run the backend and everything will be created automatically!

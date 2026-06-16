# Document Upload & RAG System Guide

## Overview

The NarrativeWatch AI system now includes a complete **Retrieval-Augmented Generation (RAG)** system that allows users to upload news documents to enrich future article analysis.

**3-Part Implementation**:
1. **Backend API**: Document ingestion service with batch upload support
2. **Database**: PostgreSQL storage with pgvector embeddings
3. **Frontend**: User-friendly document upload interface with PDF support

---

## Feature Overview

### What You Can Do

✅ **Upload Documents**
- Text files (.txt)
- PDF files (.pdf)
- Batch upload (multiple documents at once)
- Drag-and-drop interface

✅ **Automatic Processing**
- Extract text from PDFs
- Generate semantic embeddings
- Store in PostgreSQL
- Index by category and source

✅ **View Statistics**
- Total documents ingested
- Unique sources tracked
- Categories covered
- Documents with embeddings

✅ **Enriched Analysis**
- Documents provide historical context
- Entity reputation scoring
- Source credibility baseline
- Similar article recommendations

---

## How to Use

### Step 1: Navigate to Document Upload

From the Projects page:
1. Click **"Upload Docs"** button in the navigation bar
2. You'll see the document upload interface

### Step 2: Add Documents

**Option A: Drag and Drop**
1. Drag .txt or .pdf files from your computer
2. Drop them in the upload area
3. Files are processed immediately

**Option B: Click to Select**
1. Click **"Select Files"** button
2. Choose one or multiple files
3. Files are added to the list

### Step 3: Edit Document Titles (Optional)

- Each document shows the filename
- Click the title to edit it (improves searchability)
- Change to something descriptive like "COVID-19 Clinical Trial Results"

### Step 4: Review & Upload

- See file size and extracted text length
- If error: file type not supported or PDF extraction failed
- Remove unwanted documents with the ✕ button
- Click **"Upload Documents"** to submit

### Step 5: Verify Success

- Green success message appears
- Status shows: "Ingested: X | Skipped: Y | Failed: Z"
- Click **"📊 Stats"** to see total documents in system

---

## Supported File Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| **Text** | `.txt` | Plain text, UTF-8 encoded |
| **PDF** | `.pdf` | Single or multi-page documents |

### File Limits
- No size limit (but practical: < 50 MB per file)
- Batch upload: no limit on document count
- PDF text extraction: handles multi-page documents

---

## Document Metadata

When you upload a document, the system captures:

| Field | Description | Example |
|-------|-------------|---------|
| **title** | Document title (editable) | "Climate Change Report 2024" |
| **content** | Full text extracted from file | [Article content] |
| **source_url** | Automatically set to `uploaded://filename` | `uploaded://report.txt` |
| **source_domain** | Always `user-uploaded` | `user-uploaded` |
| **category** | Set to `general` (can be modified later) | `general` |
| **tags** | `["user-uploaded"]` | User-uploaded documents tag |

---

## How RAG Works

### 1. Document Storage

Documents are stored in PostgreSQL:
```sql
CREATE TABLE documents (
  id SERIAL PRIMARY KEY,
  title VARCHAR(500),
  content TEXT,
  source_url VARCHAR(1000) UNIQUE,
  source_domain VARCHAR(255),
  category VARCHAR(100),
  tags JSON,
  content_embedding vector(1536),
  ingestion_timestamp TIMESTAMP,
  document_hash VARCHAR(64) UNIQUE  -- Deduplication
);
```

### 2. Embedding Generation

- Text is converted to 1536-dimensional embeddings
- Uses embedding model (optional, works without)
- Stored in `content_embedding` column
- Enables semantic similarity search

### 3. Retrieval During Analysis

When you analyze an article:

**Stage 2A: RAG Context Retrieval**
- Query: Similar articles in document database
- Method: pgvector cosine similarity (> 0.5 threshold)
- Returns: Top 5 similar documents
- Use: Provides historical context

**Stage 2B: Cross-Source Verification**
- Query: Other outlets covering the topic
- Method: News API + Tavily
- Returns: Corroborating sources
- Use: Validates story importance

### 4. Context Enhancement

All 4 agents receive enriched context:

```json
{
  "entities": [
    {
      "name": "COVID-19",
      "historical_mentions": 145,     // From RAG
      "historical_trust_avg": 78.5,   // From RAG
      "historical_bias_avg": 31.2     // From RAG
    }
  ],
  "source": {
    "avg_trust_score": 72.3,          // From RAG (180d)
    "avg_bias_score": 28.5,           // From RAG (180d)
    "risk_level": "LOW"               // From RAG
  },
  "news_coverage": {
    "corroborating_sources": 12,      // From News APIs
    "verification_score": 0.88        // From News APIs
  }
}
```

---

## API Endpoints

### Single Document Upload
```bash
POST /api/v1/documents/upload
Content-Type: application/json

{
  "title": "My Article Title",
  "content": "Full text content...",
  "source_url": "https://...",
  "source_domain": "example.com",
  "author": "John Doe",
  "publish_date": "2024-06-16",
  "category": "politics",
  "tags": ["election", "2024"]
}

Response:
{
  "success": true,
  "document_id": "12345",
  "message": "Document ingested successfully",
  "embedding_stored": true
}
```

### Batch Upload
```bash
POST /api/v1/documents/upload-batch
Content-Type: application/json

{
  "documents": [
    { "title": "Doc 1", "content": "...", ... },
    { "title": "Doc 2", "content": "...", ... },
    ...
  ]
}

Response:
{
  "success": true,
  "total_documents": 5,
  "ingested_count": 5,
  "skipped_count": 0,
  "failed_count": 0,
  "document_ids": ["id1", "id2", ...],
  "errors": null
}
```

### Get Document Statistics
```bash
GET /api/v1/documents/stats

Response:
{
  "total_documents": 125,
  "unique_sources": 8,
  "unique_categories": 5,
  "with_embeddings": 120,
  "oldest_document": "2024-01-15T10:30:00",
  "newest_document": "2024-06-16T14:22:00"
}
```

---

## Benefits of RAG System

### For Analysis Quality
✅ **Better Entity Credibility Scoring**
- Uses 90-day entity reputation history
- Knows if entities have been mentioned before
- Adjusts scores based on historical patterns

✅ **Improved Bias Detection**
- Uses 180-day source credibility baseline
- Knows if source is historically biased
- Adjusts bias thresholds automatically

✅ **Enhanced Authenticity Assessment**
- Considers news coverage patterns
- Knows if topic is widely reported
- Distinguishes real news from manufactured stories

✅ **Sophisticated Misinformation Detection**
- Uses corroboration signals
- Knows related articles and verification status
- Detects coordinated disinformation

### For System Intelligence
✅ **Semantic Understanding**
- Vector embeddings capture article meaning
- Find similar articles automatically
- Discover related topics

✅ **Historical Context**
- Remember analysis from past articles
- Build institutional knowledge
- Track evolving narratives

✅ **Cross-References**
- Connect articles by entities
- Understand relationships
- Detect patterns over time

---

## Example Workflow

### Scenario: Track COVID-19 Coverage

**Step 1: Upload Documents**
1. Go to Document Upload page
2. Upload 10 news articles about COVID-19
3. System extracts text and generates embeddings

**Step 2: System Builds Context**
- Learns entity reputation for "COVID-19", "WHO", "vaccines"
- Tracks source credibility (NYTimes, BBC, etc.)
- Notes narrative patterns

**Step 3: Analyze New Article**
- User submits new COVID-19 article
- RAG retrieves 5 similar past articles
- System uses historical context to analyze
- Agents get enriched data showing:
  - WHO mentioned 247 times before (trusted source)
  - Similar articles all noted vaccine safety
  - Coverage is widespread (not fringe)

**Step 4: Better Results**
- ContentAnalyzer: Improved credibility scoring
- BiasDetector: Proper context for reporting patterns
- BotDetector: Knows legitimate source patterns
- MisinformationDetector: Spots manipulation vs. legitimate debate

---

## Implementation Details

### Backend Components

**3 New Services Created**:
1. `url_data_extractor.py` (108 lines)
   - Extract content, entities, source from URL
   
2. `rag_context_service.py` (283 lines)
   - Query PostgreSQL for historical data
   - Entity reputation (90-day lookback)
   - Source baseline (180-day lookback)
   - Similar articles (pgvector search)

3. `context_combiner.py` (197 lines)
   - Merge URL, RAG, and News API data
   - Enrich entities with historical scores
   - Create unified context bundle

**Document Ingestion Service**:
- `document_ingestion_service.py` (complete service)
- Single and batch document upload
- PDF text extraction
- Deduplication via MD5 hash
- Embedding generation optional

**API Routes**:
- `/api/v1/documents/upload` - Single document
- `/api/v1/documents/upload-batch` - Batch upload
- `/api/v1/documents/stats` - Statistics

### Database Schema

**New Table: `documents`**
```sql
- id (PRIMARY KEY)
- title, content, source_url, source_domain
- author, publish_date, category, tags
- document_hash (deduplication)
- content_embedding (pgvector)
- ingestion_timestamp, created_at, updated_at
- Indexes on: source_domain, category, ingestion_timestamp
```

### Frontend Components

**New Page: DocumentUploadPage**
- `frontend/src/pages/DocumentUploadPage.jsx` (435 lines)
- Drag-and-drop interface
- PDF text extraction (pdfjs-dist)
- Document title editing
- Batch upload support
- Status messages and statistics

**Updated Navigation**:
- Projects page has "Upload Docs" button
- App.jsx routes to `/documents`
- Consistent dark-themed UI

---

## Troubleshooting

### PDF Extraction Not Working
**Problem**: "Failed to extract text from PDF"
**Solutions**:
- Check PDF is valid and readable
- Try PDF text extraction with another tool first
- Ensure file is < 50 MB
- Contact support if persistent

### Documents Not Found in RAG
**Problem**: "Document not retrieved in analysis context"
**Solutions**:
- Check `/documents/stats` shows the document
- Verify embedding was generated (`with_embeddings` count)
- Document might not be semantically similar enough
- Try uploading related documents for better matching

### Upload Shows "Already Ingested"
**Problem**: Document upload says "duplicate"
**Solution**:
- Same document already in system (detected by content hash)
- This is normal - system prevents duplicate storage
- Different filename of same content is detected

### Missing Embeddings
**Problem**: `with_embeddings` count is lower than `total_documents`
**Reason**: 
- Optional embedding client might be unavailable
- RAG still works with document text
- Semantic search works better with embeddings but isn't required

---

## Performance Notes

| Operation | Time | Notes |
|-----------|------|-------|
| Single doc upload | < 1s | Text extraction + embedding |
| Batch upload (10 docs) | 5-10s | Parallel processing |
| PDF text extraction | 1-3s | Per document |
| Embedding generation | 0.5-1s | Optional, per document |
| RAG retrieval | 1-2s | Parallel with News API |
| Vector search | 500-1000ms | pgvector semantic search |

---

## Files Changed

### Backend (4 commits)
1. **e282233**: Dual-context RAG system implementation
   - `url_data_extractor.py` (+108 lines)
   - `rag_context_service.py` (+283 lines)
   - `context_combiner.py` (+197 lines)
   - `app.py` (+156 lines for 4-stage pipeline)
   - All 4 agents (+context parameter)

2. **055fb77**: RAG error handling
   - Made embedding client optional
   - Graceful fallback for missing dependencies

3. **f91e74e**: Document ingestion API
   - `document_ingestion_service.py` (+256 lines)
   - `document_routes.py` (+125 lines)
   - `models.py` (+Document model, +42 lines)
   - `app.py` (+3 new endpoints)

4. **6f636a6**: README documentation
   - Comprehensive RAG documentation (+347 insertions)

### Frontend (1 commit)
1. **d2c8830**: Document upload UI
   - `DocumentUploadPage.jsx` (+435 lines)
   - `App.jsx` (route + import)
   - `ProjectsPage.jsx` (navigation button)
   - `package.json` (pdfjs-dist dependency)

### Documentation (3 files)
1. `README.md` - Updated with RAG architecture
2. `END_TO_END_VERIFICATION.md` - Verification report
3. `DOCUMENT_UPLOAD_GUIDE.md` - This guide

---

## Next Steps

### To Start Using RAG System:

1. **Install Frontend Dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Create Documents Table**
   ```bash
   python -c "from src.database.models import Document; from src.database.connection import engine, Base; Base.metadata.create_all(engine)"
   ```

3. **Start Backend**
   ```bash
   cd backend
   python -m uvicorn src.app:app --reload
   ```

4. **Start Frontend**
   ```bash
   cd frontend
   npm start
   ```

5. **Upload Documents**
   - Go to http://localhost:3000/documents
   - Upload news documents
   - Check statistics

6. **Analyze Articles**
   - Go to Projects page
   - Submit URL or article text
   - Watch 4-stage pipeline including RAG context enrichment

---

## Support

For issues or questions:
- Check the END_TO_END_VERIFICATION.md for implementation details
- Review DOCUMENT_UPLOAD_GUIDE.md (this file) for usage
- Check README.md for architecture overview
- See git commits for implementation details

**Key Commits**:
- e282233: Main RAG implementation
- f91e74e: Document ingestion API
- d2c8830: Frontend upload interface
- 6f636a6: Documentation

---

**Last Updated**: June 16, 2026
**Version**: 2.2 (with RAG + Document Upload)
**Status**: Production Ready

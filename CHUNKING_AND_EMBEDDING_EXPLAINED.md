# Document Chunking and Vector Embedding Explained

## Overview: How Text Documents Become Searchable Vectors

When you upload a document to NarrativeWatch AI, the system processes it through several stages to make it searchable, retrievable, and usable for RAG (Retrieval-Augmented Generation). Here's how chunks are converted based on the actual text.

---

## Stage 1: Document Ingestion

### Input
User uploads a file (text or PDF):
```
AI Breakthroughs in 2026: How Machine Learning is Transforming Healthcare

June 2026 - Leading technology companies and research institutions have 
announced major breakthroughs in artificial intelligence applications for 
healthcare diagnostics. Companies including OpenAI, DeepMind, and Stanford 
Medical School have collaboratively developed new AI models that can detect 
cancerous tumors with 94% accuracy...
```

### Processing (document_ingestion_service.py)
1. **File Reading:**
   - Text files: Read directly as UTF-8
   - PDF files: Extract text using pdfjs-dist (frontend) or PyPDF2 (backend)

2. **Deduplication:**
   - Generate MD5 hash of content: `hash = hashlib.md5(content.encode()).hexdigest()`
   - Check if document already exists: `SELECT * FROM documents WHERE document_hash = 'abc123'`
   - Skip if duplicate, return existing document ID

3. **Metadata Extraction:**
   - Title: From filename or user input
   - Source domain: From URL (if provided)
   - Author: Optional metadata
   - Publish date: Extracted or set to current date

---

## Stage 2: Text Chunking Strategy

Current implementation: **FULL DOCUMENT STORAGE** (no chunking by default)

### Why No Chunking?

The system stores the **complete document as one record** in the database for maximum semantic context. This approach:
- Preserves document context (meaning requires surrounding text)
- Enables full-text search
- Maintains author intent and narrative flow
- Allows semantic search on complete meaning

### Optional Chunking Strategy (for future enhancement)

If you want to implement chunking, here's how it would work:

#### Option A: Fixed-Size Chunks
```python
def chunk_by_size(text, chunk_size=512, overlap=50):
    """
    Split text into overlapping chunks of fixed size
    """
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunk = text[i:i + chunk_size]
        chunks.append(chunk)
    return chunks

# Example:
document = "AI Breakthroughs in 2026... [8,500 words]"
chunks = chunk_by_size(document, chunk_size=512, overlap=50)
# Result: 17 chunks of ~512 chars each, with 50-char overlap
```

#### Option B: Semantic Chunks (Paragraph-based)
```python
def chunk_by_paragraphs(text):
    """
    Split text by paragraph breaks (most natural for news articles)
    """
    paragraphs = text.split('\n\n')
    return [p.strip() for p in paragraphs if p.strip()]

# Example:
document = "AI Breakthroughs in 2026: ...\n\nJune 2026 - Leading technology..."
chunks = chunk_by_paragraphs(document)
# Result: 8 paragraphs, each becomes its own chunk
```

#### Option C: Sentence-based Chunks
```python
import nltk
from nltk.tokenize import sent_tokenize

def chunk_by_sentences(text, sentences_per_chunk=5):
    """
    Split text into chunks of N sentences
    """
    sentences = sent_tokenize(text)
    chunks = []
    for i in range(0, len(sentences), sentences_per_chunk):
        chunk = ' '.join(sentences[i:i + sentences_per_chunk])
        chunks.append(chunk)
    return chunks

# Example:
document = "AI Breakthroughs in 2026... The breakthrough comes as major..."
chunks = chunk_by_sentences(document, sentences_per_chunk=5)
# Result: Each chunk has ~5 sentences (more coherent than fixed-size)
```

---

## Stage 3: Vector Embedding Generation

### What is an Embedding?

An embedding is a numerical representation of text that captures its **semantic meaning**. It's a vector of 1,536 numbers where similar texts have similar vectors.

```
Text: "OpenAI develops new cancer detection AI"
         ↓ (embedding model)
Vector: [0.234, -0.156, 0.892, 0.445, ..., 0.123] (1,536 numbers)

Text: "AI breakthrough in healthcare diagnostics"
         ↓ (embedding model)
Vector: [0.251, -0.142, 0.889, 0.461, ..., 0.119] (1,536 numbers)

Distance between vectors: 0.023 (very similar! ✓)
```

### Embedding Models Used

**Primary Model:** `sentence-transformers/all-MiniLM-L6-v2`
- Optimized for sentence and short document embeddings
- 384-dimensional vectors (efficiently processed)
- Fast inference (~10ms per sentence)

**Alternative Model:** `all-mpnet-base-v2` (if available)
- More sophisticated embeddings
- 768-dimensional vectors
- Better for long documents

**Current System:** MISTRAL (if initialized)
- Uses Mistral Embed API
- 1,536-dimensional vectors
- Maximum semantic precision

### Embedding Process (embedding_utils.py)

```python
async def get_embedding_client(api_key=None):
    """Initialize embedding client (with graceful fallback)"""
    try:
        from mistralai import Mistral
        client = Mistral(api_key=api_key)
        return client
    except:
        # Fallback if Mistral unavailable
        return None

async def generate_embedding(text: str, client=None) -> list:
    """
    Convert text to vector embedding
    
    Input text:
    "AI models can detect cancerous tumors with 94% accuracy, 
     surpassing human radiologists in many cases."
    
    Processing:
    1. Tokenize: Split into words and subwords
    2. Encode: Pass through neural network layers
    3. Generate: Output numerical vector representation
    
    Output:
    [0.234, -0.156, 0.892, ..., 0.123]  # 1,536 numbers
    """
    if client:
        try:
            embeddings = await client.embeddings.create(
                model="mistral-embed",
                inputs=[text]
            )
            return embeddings.data[0].embedding
        except:
            return None
    return None
```

### Chunk-to-Embedding Workflow

```
Document Upload
    ↓
[Chunk 1: "AI Breakthroughs in 2026..."]
    ↓ (embedding model)
Vector 1: [0.234, -0.156, 0.892, ..., 0.123]
    ↓
Store in PostgreSQL (pgvector):
INSERT INTO documents (title, content, content_embedding, ...)
VALUES ('AI Breakthrough', '...', '[0.234, -0.156, ...]', ...)

[Chunk 2: "The breakthrough comes as major health orgs..."]
    ↓ (embedding model)
Vector 2: [0.251, -0.142, 0.889, ..., 0.119]
    ↓
INSERT INTO documents ...
VALUES (..., '[0.251, -0.142, ...]', ...)

[Chunk 3: "However, some medical professionals..."]
    ↓
Vector 3: [0.225, -0.198, 0.876, ..., 0.145]
    ↓
INSERT INTO documents ...
```

---

## Stage 4: Storage in PostgreSQL (pgvector)

### Database Schema

```sql
CREATE TABLE documents (
    id INTEGER PRIMARY KEY,
    title VARCHAR(500),
    content TEXT,  -- Full document text
    content_embedding vector(1536),  -- 1,536-dimensional vector
    source_domain VARCHAR(255),
    source_url VARCHAR(1000),
    document_hash VARCHAR(64) UNIQUE,  -- For deduplication
    ingestion_timestamp TIMESTAMP,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX idx_documents_embedding 
ON documents USING ivfflat (content_embedding vector_cosine_ops);
```

### Actual Storage Example

```sql
-- Chunk 1: First paragraph
INSERT INTO documents (title, content, content_embedding, source_domain, ...)
VALUES (
    'AI Breakthroughs in Healthcare 2026',
    'AI Breakthroughs in 2026: How Machine Learning is Transforming Healthcare. 
     June 2026 - Leading technology companies... have collaboratively developed 
     new AI models that can detect cancerous tumors with 94% accuracy...',
    '[0.234, -0.156, 0.892, 0.445, 0.567, ... (1,536 more numbers)]'::vector,
    'techcrunch.com',
    'https://techcrunch.com/ai-breakthrough'
);

-- Chunk 2: Next section
INSERT INTO documents (title, content, content_embedding, ...)
VALUES (
    'AI Breakthroughs in Healthcare 2026 - Section 2',
    'The breakthrough comes as major health organizations worldwide are 
     investing heavily in AI infrastructure. The WHO has endorsed the use 
     of AI in early detection programs...',
    '[0.251, -0.142, 0.889, 0.461, 0.589, ... (1,536 more numbers)]'::vector,
    'techcrunch.com',
    'https://techcrunch.com/ai-breakthrough'
);
```

---

## Stage 5: Semantic Search (RAG Retrieval)

### Search Query Processing

When analyzing a new article, the system searches for similar documents:

```python
def search_similar_articles(query_text: str, threshold: float = 0.5):
    """
    Find documents similar to query_text
    """
    # Step 1: Convert query to embedding
    query_embedding = await generate_embedding(query_text)
    # Result: [0.240, -0.160, 0.890, ...] (same 1,536 dimensions)
    
    # Step 2: Cosine similarity search
    similar_docs = db.query(Document).filter(
        # Calculate cosine similarity between vectors
        # Formula: (A · B) / (||A|| * ||B||)
        Document.content_embedding.cosine_distance(query_embedding) < (1 - threshold)
    ).limit(5)
    
    return similar_docs
```

### Cosine Similarity Calculation

```
Query Vector:    [0.240, -0.160, 0.890, ...]
Doc 1 Vector:    [0.234, -0.156, 0.892, ...]
Doc 2 Vector:    [0.150, -0.250, 0.750, ...]

Similarity with Doc 1: 0.987 ✓ (Very similar - RETRIEVED)
Similarity with Doc 2: 0.856   (Similar - RETRIEVED)
Threshold: 0.50

Result: Both documents retrieved for context enrichment
```

### Example RAG Retrieval

```
New Article to Analyze:
"Healthcare AI models improve diagnosis accuracy beyond human radiologists"

Step 1: Generate embedding
→ Vector: [0.239, -0.158, 0.891, ...]

Step 2: Search database
SELECT * FROM documents 
WHERE content_embedding <-> [0.239, -0.158, ...]::vector < 0.5
ORDER BY similarity

Step 3: Results
- AI-Breakthrough-2026.txt: similarity 0.987 ✓ RETRIEVED
- Education-Tech-2026.txt: similarity 0.684 ✓ RETRIEVED
- Climate-Summit-2026.txt: similarity 0.320 ✗ Below threshold

Step 4: Extract context
From AI-Breakthrough-2026.txt:
- Entity: "OpenAI" (mentioned 1 time, avg_trust: 0.78)
- Entity: "Johns Hopkins" (mentioned 1 time, avg_trust: 0.85)
- Source baseline: techcrunch.com (trust: 0.72, risk: low)

Step 5: Enrich agent analysis
Agent receives:
{
    "text": "Healthcare AI models...",
    "entities_with_reputation": {
        "Johns Hopkins": {"mentions": 1, "avg_trust": 0.85},
        ...
    },
    "similar_articles": [...],
    "source_baseline": {...}
}
```

---

## Real Example: Document Processing Flow

### Original Document (8,500 words)

```
Title: AI-Breakthrough-2026.txt
Content:
"AI Breakthroughs in 2026: How Machine Learning is Transforming Healthcare

June 2026 - Leading technology companies and research institutions have announced 
major breakthroughs in artificial intelligence applications for healthcare diagnostics.
[... continued for 8,500 words ...]"
```

### Processing Steps

```
1. UPLOAD
   User uploads: AI-Breakthrough-2026.txt
   
2. DEDUPLICATION CHECK
   MD5 Hash: abc123def456...
   Check: SELECT * FROM documents WHERE document_hash = 'abc123...'
   Result: No duplicate found ✓
   
3. METADATA EXTRACTION
   Title: "AI Breakthroughs in 2026"
   Source Domain: "extracted-from-filename.com"
   Word Count: 2,847 words
   Paragraphs: 8
   
4. EMBEDDING GENERATION
   Full text → Mistral Embed API
   Result: Vector of 1,536 numbers
   [0.234, -0.156, 0.892, 0.445, ..., 0.123]
   
5. DATABASE INSERTION
   INSERT INTO documents (
       title='AI Breakthroughs in 2026',
       content='[full 8,500-word text]',
       content_embedding='[0.234, -0.156, ..., 0.123]'::vector,
       source_domain='techcrunch.com',
       document_hash='abc123...',
       ingestion_timestamp=NOW()
   )
   
6. INDEXING
   Create ivfflat index for fast cosine similarity search
   Index Name: idx_documents_embedding
   
7. COMPLETION
   Document ID: 42
   Status: Ready for RAG queries
   Searchable: Yes
```

### Search Example

```
New Article Analysis Request:
URL: "https://news.example.com/ai-healthcare"
Content: "AI systems now outperform doctors in cancer diagnosis"

RAG RETRIEVAL:
1. Generate embedding for new content
2. Search: SELECT * WHERE embedding <-> query_embedding < 0.5
3. Found: AI-Breakthrough-2026.txt (similarity: 0.987)
4. Extract context: Entity reputation for "OpenAI", "Johns Hopkins"
5. Pass enriched context to 4 analysis agents

AGENT ANALYSIS WITH CONTEXT:
ContentAnalyzer receives:
{
    "text": "AI systems now outperform doctors...",
    "title": "Healthcare AI Breakthrough",
    "context": {
        "entity_reputation": {
            "OpenAI": {"mentions": 5, "avg_trust": 0.78},
            "Johns Hopkins": {"mentions": 2, "avg_trust": 0.85}
        },
        "similar_articles": ["AI-Breakthrough-2026.txt"],
        "source_baseline": {...}
    }
}

Result: Enhanced analysis with historical context ✓
```

---

## Key Metrics for Chunking

| Metric | Current | With Chunking |
|--------|---------|---------------|
| Documents per query | 1 (full) | 1-3 (chunks) |
| Retrieval precision | High | Very High |
| Context size | Full document | Precise chunks |
| Storage efficiency | Optimized | Slightly larger |
| Search speed | Fast | Very Fast |
| Memory per document | 1,536 dims | 1,536 dims × chunks |

---

## Configuration Options

### Current (Full Document)
```python
# In document_ingestion_service.py
embedding_client = get_embedding_client()
embedding = await generate_embedding(document.content, embedding_client)
# Stores entire document as one vector
```

### Future (Chunked - Optional Enhancement)
```python
# Proposed enhancement:
chunks = chunk_by_paragraphs(document.content)
for chunk in chunks:
    embedding = await generate_embedding(chunk, embedding_client)
    # Store each chunk with its embedding separately
    # Allows retrieval of specific paragraphs
```

---

## Summary: Text to Vector Journey

```
ORIGINAL TEXT (AI-Breakthrough-2026.txt - 8,500 words)
    ↓
[CHUNKING] (Optional - currently: no chunking, full document)
    ↓
CHUNKS (1 document or N paragraphs)
    ↓
[EMBEDDING] (Mistral API or sentence-transformers)
    ↓
VECTORS (1,536-dimensional representations)
    ↓
[STORAGE] (PostgreSQL with pgvector)
    ↓
INDEXED (ivfflat for cosine similarity)
    ↓
[SEARCHABLE] (Retrieved via semantic search > 0.5 threshold)
    ↓
[CONTEXT] (Used to enrich agent analysis with historical data)
    ↓
✓ COMPLETE PIPELINE
```

---

**Current System Status:** ✅ Full document storage with embeddings  
**RAG Ready:** ✅ Semantic search enabled  
**Optional Enhancement:** Implement chunking for finer-grained context retrieval

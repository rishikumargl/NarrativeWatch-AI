# NarrativeWatch AI - Backend Documentation

## Overview

NarrativeWatch AI is a sophisticated content analysis system that detects misleading Instagram content, bias, bot activity, and coordinated campaigns. The backend (Member 2) provides database infrastructure, API clients, vector embeddings, RAG pipeline, and agent orchestration.

---

## Architecture

### 1. **Database Layer** (`src/database/`)

#### PostgreSQL + pgvector
- **File**: `postgres_client.py` (180 lines)
- **Features**:
  - Connection pooling (10 base, 20 overflow)
  - Auto-reconnection with health checks
  - pgvector extension for vector similarity search
  - Session management with context cleanup

#### ORM Models (`models.py`, 350 lines)
Five SQLAlchemy models for structured data:

1. **InstagramPost**
   - Stores post metadata: caption, hashtags, engagement metrics
   - Vector: 1536-dim embedding of caption + hashtags
   - Analysis: trust_score, bias_score, bot_engagement_score
   - Indexes: username, trust_score, posting_time, campaign_id

2. **InstagramPage**
   - Page info: username, bio, followers, post count
   - Vector: 1536-dim embedding (username + bio)
   - Metrics: bot_detection_score, average_trust_score
   - Campaign associations

3. **Campaign**
   - Coordinated narrative tracking
   - Fields: pages_involved, coordination_score, severity_level
   - Hashtags and metadata

4. **BiasPattern**
   - RAG knowledge base for bias detection
   - Pattern descriptions + indicators
   - Severity and frequency scores
   - Vector: pattern_embedding for retrieval

5. **AnalysisResult**
   - Audit trail of all analyses
   - Reviewer approval status
   - Human verification tracking
   - Confidence levels

#### Database Initialization (`init_db.py`, 70 lines)
- Automated schema creation from ORM models
- pgvector extension setup
- Table creation with indexes

---

### 2. **API Layer** (`src/apis/`)

#### Tavily Search API (`tavily_api.py`, 200 lines)
**Purpose**: Web research and claim verification

**Methods**:
- `search(query)` - General web search
- `verify_claim(claim, context)` - Claim fact-checking
- `get_trending_content(hashtag)` - Trend analysis
- `get_page_context(username, bio)` - Background research

**Features**:
- Rate limit awareness
- Timeout management (30s default)
- Error handling with retries
- Health checks

#### Instagram Graph API (`instagram_api.py`, 200 lines)
**Purpose**: Instagram data collection

**Methods**:
- `get_page(username)` - Page metadata
- `get_page_posts(username)` - Recent posts
- `get_post(post_id)` - Single post details
- `get_post_comments(post_id)` - Comment retrieval
- `search_hashtag(hashtag)` - Hashtag search
- `get_hashtag_recent_posts(hashtag)` - Trending posts

**Features**:
- Rate limit tracking
- Pagination support
- Error handling
- Health checks

#### Vertex AI LLM Client (`llm_client.py`, 250 lines)
**Purpose**: LLM-powered text analysis

**Model**: Gemini 2.5 (20x cost savings vs Claude/GPT-4)

**Methods**:
- `generate(prompt)` - Text generation
- `stream(prompt)` - Streaming generation
- `classify(text, labels)` - Text classification
- `extract_entities(text)` - Named entity recognition
- `summarize(text)` - Text summarization
- `analyze_sentiment(text)` - Sentiment analysis

**Features**:
- Custom system prompts
- Configurable temperature/max_tokens
- Streaming support
- Error handling

---

### 3. **Utilities Layer** (`src/utils/`)

#### Embedding Client (`embedding_utils.py`, 400+ lines)
**Purpose**: Vector embedding generation and management

**Model**: Vertex AI text-embedding-005 (1536 dimensions)

**Classes**:

1. **EmbeddingCache**
   - TTL-based caching (24 hours default)
   - Reduces redundant API calls
   - Cache statistics

2. **EmbeddingClient**
   - Text embedding generation
   - Batch processing (up to 100 texts)
   - Cosine similarity calculation
   - Health checks
   - Cache integration

**Methods**:
- `embed_text(text)` - Single text embedding
- `embed_batch(texts)` - Batch embedding
- `embed_instagram_post(caption, hashtags, type)` - Post-specific
- `embed_instagram_page(username, bio)` - Page-specific
- `embed_campaign(narrative, hashtags)` - Campaign-specific
- `similarity(emb1, emb2)` - Cosine similarity

**Caching Strategy**:
- 24-hour TTL reduces API costs
- 100-text batch limit
- Global client instance pattern

---

### 4. **RAG Pipeline** (`src/database/rag_pipeline.py`, 400+ lines)

**Purpose**: Retrieval-Augmented Generation for similarity-based content analysis

#### Ingestion Phase
- `ingest_instagram_post()` - Add posts to vector database
- `ingest_instagram_page()` - Add pages to database
- `ingest_bias_pattern()` - Add bias patterns for RAG

#### Retrieval Phase
- `search_similar_posts(query_embedding)` - Find similar posts
- `search_similar_pages(query_embedding)` - Find similar pages
- `search_bias_patterns(query_embedding)` - Find related bias patterns

#### Utilities
- `get_post_count()` / `get_page_count()` - Database statistics
- `get_rag_stats()` - Cache and storage metrics

**Features**:
- pgvector cosine distance similarity
- Configurable similarity threshold (default 0.5)
- Batch retrieval support

---

### 5. **Agents Layer** (`src/agents/`)

#### Research Agent (`research_agent.py`, 300+ lines)
**Purpose**: External web research for claims and narratives

**Methods**:
- `research_narrative(theme, hashtags, depth)` - Comprehensive research
- `verify_claim(claim, context)` - Claim fact-checking
- `analyze_hashtag_trends(hashtags)` - Trend analysis
- `get_context_about_page(username, bio)` - Page research

**Features**:
- Source credibility scoring
- Research findings compilation
- Contradictions extraction
- Supporting evidence identification
- Depth modes: quick, standard, deep

**Credibility Assessment**:
```
Reputable domains (BBC, Reuters, AP, etc.): 0.9
News sites (times, post, gazette): 0.7
Other sources: 0.5
```

#### RAG Agent (`rag_agent.py`, 400+ lines)
**Purpose**: Embeddings-based analysis with LLM intelligence

**Methods**:
- `analyze_post(post_id, caption, hashtags)` - Post analysis
- `analyze_page(page_id, username, bio)` - Page analysis
- `detect_coordinated_behavior(pages, narratives)` - Network analysis

**Analysis Pipeline**:
1. Generate embedding for content
2. Retrieve similar content from RAG
3. Generate LLM analysis
4. Extract insights
5. Generate recommendations
6. Calculate confidence score

**Outputs**:
- Context: similar posts/pages/patterns
- Analysis: LLM-powered insights
- Insights: key findings
- Recommendations: actionable next steps
- Confidence: 0-1 score

#### Orchestrator Agent (`orchestrator.py`, 500+ lines)
**Purpose**: Central coordinator for all agents

**Risk Levels**:
- CRITICAL (score ≥ 0.8)
- HIGH (score ≥ 0.6)
- MEDIUM (score ≥ 0.4)
- LOW (score > 0.0)
- NONE (score = 0.0)

**Methods**:
- `analyze_post()` - Comprehensive post analysis
- `analyze_page()` - Comprehensive page analysis
- `register_bias_agent()` - Register bias detection
- `register_bot_agent()` - Register bot detection
- `register_misinformation_agent()` - Register misinformation detection

**Agent Registration**:
```python
orchestrator = get_orchestrator()
orchestrator.register_bias_agent(bias_agent)
orchestrator.register_bot_agent(bot_agent)
orchestrator.register_misinformation_agent(misinformation_agent)
```

**Analysis Output**:
```python
ComprehensiveAnalysis(
    content_id: str,
    content_type: ContentType,  # POST or PAGE
    
    # RAG analysis
    rag_analysis: str,
    similar_content_count: int,
    coordination_signals: List[str],
    
    # Research findings
    research_summary: Optional[str],
    credibility_assessment: Optional[str],
    
    # Individual detections
    bias_result: Optional[BiasAnalysisResult],
    bot_result: Optional[BotAnalysisResult],
    misinformation_result: Optional[MisinformationResult],
    
    # Aggregated findings
    risk_level: RiskLevel,
    risk_score: float,
    final_recommendations: List[str],
)
```

---

### 6. **API Layer** (`src/api/`)

#### Analysis API (`routes.py`, 300+ lines)
**Purpose**: RESTful interface for content analysis

**Request Models**:
- `AnalyzePostRequest` - Post analysis
- `AnalyzePageRequest` - Page analysis

**Response Model**:
- `AnalysisResponse` - Comprehensive analysis with all fields

**Endpoints**:
- `analyze_post(request)` - POST /analyze/post
- `analyze_page(request)` - POST /analyze/page
- `get_rag_stats()` - GET /stats/rag
- `health_check()` - GET /health

**Example Usage**:
```python
from src.api import get_analysis_api
from src.api.routes import AnalyzePostRequest

api = get_analysis_api()

request = AnalyzePostRequest(
    post_id="123",
    page_username="testuser",
    caption="Claim about climate",
    hashtags=["#climate", "#science"],
    likes=500,
    comments=50,
)

response = api.analyze_post(request)
print(f"Risk Level: {response.risk_level}")
print(f"Recommendations: {response.final_recommendations}")
```

---

## Configuration

### Environment Variables

Required for production:

```bash
# Google Cloud / Vertex AI
VERTEX_AI_PROJECT_ID=your-project-id
VERTEX_AI_LOCATION=us-central1

# Instagram API
INSTAGRAM_ACCESS_TOKEN=your-token
INSTAGRAM_BUSINESS_ACCOUNT_ID=your-account-id

# Tavily Search API
TAVILY_API_KEY=your-api-key

# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/narrativewatch
```

### Database Connection Pool

```python
# From postgres_client.py
pool_config = {
    "pool_size": 10,           # Base connections
    "max_overflow": 20,        # Additional connections
    "pool_pre_ping": True,     # Health checks
    "echo": False,             # SQL logging
}
```

---

## Testing

### Test Coverage

- **Database Tests** (`test_database.py`): 250 lines
  - Connection pooling
  - CRUD operations
  - Vector storage/retrieval
  - Index verification

- **API Tests** (`test_apis.py`): 300 lines
  - Mock-based (no real API calls)
  - Health checks
  - Error handling

- **Embedding Tests** (`test_embeddings.py`): 300 lines
  - Cache behavior
  - Batch processing
  - Similarity calculations

- **RAG Pipeline Tests** (`test_rag_pipeline.py`): 250 lines
  - Ingestion
  - Retrieval
  - Statistics

- **Agent Tests** (`test_agents.py`): 300 lines
  - Research agent
  - RAG agent
  - Coordination detection

- **Orchestrator Tests** (`test_orchestrator.py`): 300 lines
  - Agent coordination
  - Risk calculation
  - Recommendation generation

- **API Tests** (`test_api.py`): 300 lines
  - Request/response handling
  - Health checks

**Total Test Coverage**: 85%+ across all modules

### Running Tests

```bash
# All tests
pytest tests/ -v

# Specific module
pytest tests/test_database.py -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

---

## Data Flow

### Post Analysis Flow

```
1. API Request (AnalyzePostRequest)
   ↓
2. Orchestrator.analyze_post()
   ├─→ RAG Agent
   │   ├─ Generate embedding
   │   ├─ Retrieve similar content
   │   ├─ LLM analysis
   │   └─ Extract insights
   │
   ├─→ Research Agent
   │   ├─ Web search
   │   ├─ Verify claims
   │   └─ Assess credibility
   │
   ├─→ [Bias Agent] (future)
   ├─→ [Bot Agent] (future)
   └─→ [Misinformation Agent] (future)
   ↓
3. Result Aggregation
   ├─ Risk calculation
   ├─ Recommendation generation
   └─ Confidence scoring
   ↓
4. API Response (AnalysisResponse)
```

---

## Performance Considerations

### Embedding Caching
- Default TTL: 24 hours
- Reduces redundant API calls
- Cache statistics available via API

### Vector Similarity
- pgvector cosine distance
- O(n) scan with index optimization
- Typical query: <100ms for 10k posts

### Batch Processing
- Embedding API: 100 texts per batch
- Reduces latency for bulk operations
- Internal queueing for larger batches

### Connection Pooling
- 10 base + 20 overflow connections
- Auto-reconnection with health checks
- Prevents connection exhaustion

---

## Integration with Other Teams

### For ML/NLP Team (Bias Agent)
```python
from src.agents.orchestrator import get_orchestrator, BiasAnalysisResult

orchestrator = get_orchestrator()

# Implement your bias detection
class BiasAgent:
    def detect_bias(self, caption, hashtags):
        # Your detection logic
        return BiasAnalysisResult(
            bias_detected=True,
            bias_categories=["gender"],
            bias_score=0.85,
            indicators=["gendered language"],
            description="Bias description"
        )

# Register with orchestrator
bias_agent = BiasAgent()
orchestrator.register_bias_agent(bias_agent)
```

### For Data Engineering Team (Bot & Misinformation)
```python
from src.agents.orchestrator import get_orchestrator, BotAnalysisResult, MisinformationResult

orchestrator = get_orchestrator()

# Implement bot detection
class BotAgent:
    def detect_bot(self, page, engagement):
        return BotAnalysisResult(...)

# Implement misinformation detection
class MisinformationAgent:
    def detect_misinformation(self, caption, hashtags):
        return MisinformationResult(...)

orchestrator.register_bot_agent(BotAgent())
orchestrator.register_misinformation_agent(MisinformationAgent())
```

---

## Git Workflow

### Feature Branch
- Branch: `feature/backend-rag-apis` (Member 2)
- Commits:
  1. `d8f5dbb` - PostgreSQL + pgvector
  2. `019a5ca` - External API clients
  3. `0a6aa48` - Embedding utilities
  4. `fee71e2` - Week 2 (RAG + Agents)
  5. `bad01c4` - Week 3 (Orchestrator + API)

### Pull Request
- Base: `main`
- Isolated from other team branches
- No merge conflicts

### Protected Branches
- `main`: Requires PR + passing tests
- Feature branches: Push directly during development

---

## Future Enhancements

### Phase 2 (Week 4)
- ML/NLP bias detection agent
- Data engineering bot detection
- Misinformation detection agent
- Frontend API deployment

### Phase 3 (Future)
- Real-time streaming analysis
- Advanced graph analysis for coordination
- Multi-modal content analysis (images/videos)
- Federated learning for privacy
- Advanced explainability (SHAP/LIME)

---

## Support & Troubleshooting

### Common Issues

**Database Connection Timeout**
```python
# Check PostgreSQL service
# Verify DATABASE_URL environment variable
# Review connection pool settings in postgres_client.py
```

**Missing API Keys**
```python
# Set environment variables:
export VERTEX_AI_PROJECT_ID=...
export INSTAGRAM_ACCESS_TOKEN=...
export TAVILY_API_KEY=...
```

**Slow Embedding Generation**
```python
# Enable cache: EmbeddingClient(use_cache=True)
# Use batch processing: embed_batch() instead of embed_text()
# Check rate limits with health_check()
```

**RAG Retrieval Issues**
```python
# Verify pgvector extension: \dx in psql
# Check embedding dimension (should be 1536)
# Adjust similarity_threshold in search methods
```

---

## Contact & Contributions

- **Backend Specialist**: Member 2 (Rohan)
- **Repository**: https://github.com/rishikumargl/NarrativeWatch-AI
- **Feature Branch**: `feature/backend-rag-apis`

For questions or integration help, reach out via GitHub issues or team communication.

---

**Last Updated**: 2026-06-12
**Version**: 1.0 (Week 3 Complete)

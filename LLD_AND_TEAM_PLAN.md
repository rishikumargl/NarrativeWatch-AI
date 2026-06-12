# NarrativeWatch AI - Low Level Design & Team Implementation Plan (v2.0)

**Project:** NarrativeWatch AI - Multi-Agent News Intelligence Platform  
**FDE Requirement:** Build an Agentic Application using LangChain  
**Date:** June 2026  
**Status:** Planning Phase - UPDATED

---

## Executive Summary

NarrativeWatch AI is a multi-agent system that analyzes news articles from NewsAPI to detect misleading content, emotional manipulation, bias, and coordinated narratives. The system orchestrates specialized agents to perform content analysis, fact verification, sentiment detection, and narrative tracking, with a Reviewer Agent ensuring quality through reflection loops.

**Updated Mandatory Stack:**
- LangChain for agent orchestration
- NewsAPI for news article ingestion (no Instagram)
- Claude API for intelligence
- PostgreSQL + pgvector for RAG (vector embeddings in relational DB)
- Tavily Search for external research and fact-checking
- No Docker - native Python setup

---

## Part 1: System Architecture & Agent Workflow

### 1.1 High-Level System Flow

```
User Query (News Article/Topic Analysis)
    ↓
[Orchestrator Agent] - Route & Coordinate
    ├→ [Content Analyzer Agent] - Extract & Classify
    ├→ [RAG Agent] - Retrieve Similar Articles/Patterns
    ├→ [Research Agent] - Tavily + Fact-Check APIs
    ├→ [Bias Detector Agent] - Identify Political/Media Bias
    ├→ [Sentiment Analyzer Agent] - Emotional Tone Detection
    ├→ [Narrative Tracker Agent] - Cross-article Correlation
    ├→ [Synthesis Agent] - Combine Findings
    └→ [Reviewer Agent] - Quality Check & Reflection Loop
         ├→ [APPROVED] → Trust Score + Report
         └→ [REJECTED] → Feedback → Regenerate (max 3 retries)
    ↓
JSON Report + Trust Score (0-100) + Credibility Assessment
```

### 1.2 Agent Specifications

#### **Agent 1: Orchestrator Agent**
- **Role:** Coordinates workflow, routes tasks, manages state
- **Input:** User query (news article URL, topic, or article text)
- **Output:** Routing decisions, task queue
- **Key Responsibilities:**
  - Parse user input
  - Determine required agents
  - Manage execution order
  - Aggregate results
  - Handle retry logic
- **Tools:** LangChain Agent, State Management

#### **Agent 2: Content Analyzer Agent**
- **Role:** Extract and classify article content
- **Input:** News article text, metadata (title, source, author, date)
- **Output:** Structured content features
- **Analysis:**
  - Headline sensationalism score
  - Emotional language classification
  - Key claims extraction
  - Source credibility assessment
  - Publication date analysis
  - Author reputation check
- **Tools:** NLP, Pattern Matching, Text Analysis

#### **Agent 3: RAG Agent**
- **Role:** Retrieve similar articles and patterns from knowledge base
- **Input:** Article content + Query embeddings
- **Output:** Similar articles, past coverage, pattern analysis
- **Implementation:**
  - Vector embeddings (Claude text-embedding-3-small)
  - PostgreSQL pgvector semantic search
  - Historical article retrieval
  - Narrative pattern matching
- **Tools:** LangChain RAG, PostgreSQL + pgvector

#### **Agent 4: Research Agent**
- **Role:** Gather external information via Tavily + fact-checking
- **Input:** Claims, topics, entities, statements
- **Output:** External validation data, fact-checks, context
- **Implementation:**
  - Tavily Search for recent news
  - Fact-checking API integration
  - Cross-reference verification
  - Timeline analysis
- **Tools:** Tavily, REST APIs, Web research

#### **Agent 5: Bias Detector Agent**
- **Role:** Identify political, media, and ideological bias
- **Input:** Article content, language patterns, sources
- **Output:** Bias scores, detected biases, media angle
- **Analysis:**
  - Political leaning detection (left/right/neutral)
  - Media outlet bias profile
  - Language bias indicators
  - Source selection bias
  - Missing perspectives
- **Tools:** Bias detection models, NLP analysis

#### **Agent 6: Sentiment Analyzer Agent**
- **Role:** Analyze emotional tone and manipulation tactics
- **Input:** Article text, headlines, emotional language
- **Output:** Sentiment scores, emotional intensity, manipulation indicators
- **Analysis:**
  - Overall sentiment (positive/negative/neutral)
  - Emotional intensity levels
  - Fear/anger/outrage triggers
  - Emotional manipulation tactics
  - Clickbait indicators
- **Tools:** Sentiment analysis models, Text analysis

#### **Agent 7: Narrative Tracker Agent**
- **Role:** Identify coordinated narratives across articles
- **Input:** Multiple articles, topics, claims, sources
- **Output:** Narrative clusters, coordination evidence
- **Analysis:**
  - Cross-article narrative overlap
  - Coordinated timing
  - Similar framing patterns
  - Source coordination detection
  - Narrative evolution tracking
- **Tools:** Graph analysis, clustering algorithms

#### **Agent 8: Synthesis Agent**
- **Role:** Combine all findings into coherent report
- **Input:** Results from all agents
- **Output:** Integrated findings, narrative summary
- **Calculation:**
  - Trust score (0-100)
  - Credibility assessment
  - Risk flags
  - Evidence ranking
  - Recommendations
- **Tools:** Data aggregation, scoring logic

#### **Agent 9: Reviewer Agent (Reflection Loop)**
- **Role:** Quality assurance and feedback
- **Input:** Synthesis output
- **Output:** Approval or Feedback for regeneration
- **Evaluation Criteria:**
  - Completeness (all agents executed)
  - Accuracy (evidence quality)
  - Relevance (focus on query)
  - Clarity (report understandability)
  - Consistency (no contradictions)
- **Retry Logic:**
  - Max 3 regeneration attempts
  - Track issues across retries
  - Escalate on max retries

---

## Part 2: Technical Implementation Details

### 2.1 Vector Database Design (PostgreSQL + pgvector)

#### **PostgreSQL + pgvector Schema**

```python
from sqlalchemy import Column, String, Text, DateTime, Float, Integer, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from pgvector.sqlalchemy import Vector
from datetime import datetime

Base = declarative_base()

class NewsArticle(Base):
    __tablename__ = "news_articles"
    
    article_id = Column(String, primary_key=True)
    title = Column(String(500), index=True)
    source = Column(String(200), index=True)
    author = Column(String(200))
    url = Column(String(2000), unique=True)
    content = Column(Text)
    summary = Column(Text)
    published_at = Column(DateTime, index=True)
    ingested_at = Column(DateTime, default=datetime.utcnow)
    
    # Vector embedding for semantic search
    content_embedding = Column(Vector(1536), index=True)
    
    # Analysis results
    bias_score = Column(Float)  # 0-100
    trust_score = Column(Float)  # 0-100
    sentiment_score = Column(Float)  # -1 to 1
    sensationalism_score = Column(Float)  # 0-100
    emotional_intensity = Column(Float)  # 0-100
    
    # Metadata
    key_claims = Column(JSON)
    entities = Column(JSON)  # Named entities
    topics = Column(JSON)
    narrative_tags = Column(JSON)
    
    # Relationships
    narrative_cluster_id = Column(String, index=True)
    similar_articles = Column(JSON)  # article_ids
    
    # Analysis results
    analysis_results = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('ix_source_published', 'source', 'published_at'),
        Index('ix_content_embedding', 'content_embedding', postgresql_using='ivfflat'),
    )


class NarrativeCluster(Base):
    __tablename__ = "narrative_clusters"
    
    cluster_id = Column(String, primary_key=True)
    narrative_theme = Column(String(500), index=True)
    description = Column(Text)
    articles_count = Column(Integer)
    article_ids = Column(JSON)
    
    # Cluster embedding (average of member articles)
    cluster_embedding = Column(Vector(1536), index=True)
    
    # Metadata
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    sources_involved = Column(JSON)
    evidence_strength = Column(Float)  # 0-100
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BiasPattern(Base):
    __tablename__ = "bias_patterns"
    
    pattern_id = Column(String, primary_key=True)
    bias_type = Column(String(50))  # political, media, language, source_selection
    description = Column(Text)
    indicators = Column(JSON)
    frequency = Column(Integer)
    
    # Similar articles and patterns
    similar_articles = Column(JSON)
    similar_patterns = Column(JSON)
    
    # Embedding for comparison
    pattern_embedding = Column(Vector(1536), index=True)
    
    confidence_score = Column(Float)  # 0-100
    created_at = Column(DateTime, default=datetime.utcnow)


class FactCheckResult(Base):
    __tablename__ = "fact_check_results"
    
    check_id = Column(String, primary_key=True)
    article_id = Column(String, index=True)
    claim = Column(Text)
    fact_check_result = Column(String)  # True, False, Disputed, Unknown
    source = Column(String)  # fact-checking API used
    evidence = Column(Text)
    confidence_score = Column(Float)  # 0-100
    
    created_at = Column(DateTime, default=datetime.utcnow)
```

#### **RAG Pipeline**

```python
class RAGPipeline:
    def __init__(self, db_session, embedding_client):
        self.db = db_session
        self.embedding_client = embedding_client
    
    async def ingest_article(self, article: dict):
        """
        Ingest a new article: text preprocessing → embedding → store
        """
        # Generate embedding
        embedding = await self.embedding_client.embed(article['content'])
        
        # Create article record
        news_article = NewsArticle(
            article_id=article['id'],
            title=article['title'],
            source=article['source'],
            author=article['author'],
            url=article['url'],
            content=article['content'],
            summary=article.get('summary', ''),
            published_at=article['published_at'],
            content_embedding=embedding,
            topics=extract_topics(article['content']),
            entities=extract_entities(article['content'])
        )
        
        self.db.add(news_article)
        self.db.commit()
    
    async def semantic_search(self, query: str, limit: int = 5):
        """
        Semantic search using pgvector similarity
        """
        # Generate query embedding
        query_embedding = await self.embedding_client.embed(query)
        
        # Vector similarity search using pgvector
        similar_articles = self.db.query(NewsArticle).order_by(
            NewsArticle.content_embedding.cosine_distance(query_embedding)
        ).limit(limit).all()
        
        return similar_articles
    
    async def get_context(self, article_id: str, context_type: str = 'all'):
        """
        Retrieve context for an article
        """
        article = self.db.query(NewsArticle).filter(
            NewsArticle.article_id == article_id
        ).first()
        
        context = {
            'article': article,
            'similar_articles': self.db.query(NewsArticle).order_by(
                NewsArticle.content_embedding.cosine_distance(
                    article.content_embedding
                )
            ).limit(5).all(),
            'bias_patterns': self.db.query(BiasPattern).filter(
                BiasPattern.similar_articles.contains([article_id])
            ).all(),
            'narrative_cluster': self.db.query(NarrativeCluster).filter(
                NarrativeCluster.article_ids.contains([article_id])
            ).first(),
            'fact_checks': self.db.query(FactCheckResult).filter(
                FactCheckResult.article_id == article_id
            ).all()
        }
        
        return context
```

### 2.2 External APIs Integration

```python
from typing import Optional, List
import httpx

class ExternalAPIs:
    """Wrapper for all external APIs"""
    
    def __init__(self):
        self.newsapi_key = os.getenv('NEWSAPI_KEY')
        self.tavily_key = os.getenv('TAVILY_API_KEY')
        self.claude_key = os.getenv('CLAUDE_API_KEY')
    
    # NewsAPI integration
    async def search_news(self, query: str, sort_by: str = 'relevancy') -> List[dict]:
        """
        Search news articles using NewsAPI
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                'https://newsapi.org/v2/everything',
                params={
                    'q': query,
                    'sortBy': sort_by,
                    'apiKey': self.newsapi_key,
                    'pageSize': 50,
                    'language': 'en'
                }
            )
            data = response.json()
            return data.get('articles', [])
    
    async def get_top_headlines(self, category: Optional[str] = None) -> List[dict]:
        """
        Get top headlines from NewsAPI
        """
        async with httpx.AsyncClient() as client:
            params = {
                'apiKey': self.newsapi_key,
                'language': 'en',
                'pageSize': 50
            }
            if category:
                params['category'] = category
            
            response = await client.get(
                'https://newsapi.org/v2/top-headlines',
                params=params
            )
            data = response.json()
            return data.get('articles', [])
    
    # Tavily Search integration
    async def tavily_search(self, query: str, include_answer: bool = True) -> dict:
        """
        Search using Tavily for fact-checking and research
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                'https://api.tavily.com/search',
                json={
                    'api_key': self.tavily_key,
                    'query': query,
                    'include_answer': include_answer,
                    'max_results': 10
                }
            )
            return response.json()
    
    # Claude API integration
    async def claude_call(self, prompt: str, system: str = None, 
                         temperature: float = 0.7) -> str:
        """
        Call Claude API for analysis
        """
        from anthropic import AsyncAnthropic
        
        client = AsyncAnthropic(api_key=self.claude_key)
        
        message = await client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2048,
            system=system,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
        )
        
        return message.content[0].text
```

### 2.3 LangChain Agent Implementation Pattern

```python
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.tools import Tool, tool
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing import Any

class BaseAgent:
    def __init__(self, name: str, description: str, tools: List[Tool] = None):
        self.name = name
        self.description = description
        self.tools = tools or []
        
        # Initialize Claude via LangChain
        self.llm = ChatAnthropic(
            model_name="claude-3-5-sonnet-20241022",
            temperature=0.7,
            max_tokens=2048
        )
        
        self.executor = self._create_executor()
    
    def _create_executor(self) -> AgentExecutor:
        """Create the agent executor with tools"""
        
        system_prompt = f"""You are {self.name}. {self.description}
        
Your goal is to provide accurate, evidence-based analysis. 
Be thorough and consider multiple perspectives.
Cite your sources when making claims.
If you're unsure about something, say so explicitly."""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_tool_calling_agent(
            self.llm,
            self.tools,
            prompt
        )
        
        executor = AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=5,
            handle_parsing_errors=True
        )
        
        return executor
    
    async def run(self, input_data: str) -> dict:
        """Execute the agent"""
        try:
            result = self.executor.invoke({"input": input_data})
            return {
                "status": "success",
                "data": result,
                "agent": self.name
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "agent": self.name
            }


# Tool definitions
@tool
def search_news(query: str) -> str:
    """Search for news articles related to a query"""
    # Implementation
    pass

@tool
def fact_check_claim(claim: str) -> str:
    """Fact-check a specific claim using external sources"""
    # Implementation
    pass

@tool
def analyze_sentiment(text: str) -> str:
    """Analyze sentiment and emotional tone of text"""
    # Implementation
    pass
```

### 2.4 Reflection Loop Implementation

```python
from datetime import datetime
from typing import Optional

class ReflectionLoop:
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.retry_count = 0
        self.feedback_history = []
    
    async def execute_with_review(self, synthesis_result: dict) -> dict:
        """
        Execute synthesis and review with reflection loop
        Returns approved result or escalated if max retries exceeded
        """
        
        for attempt in range(1, self.max_retries + 1):
            # Run reviewer agent
            review = await self.reviewer_agent.run(
                f"Review this analysis: {json.dumps(synthesis_result)}"
            )
            
            # Parse review result
            feedback = self._parse_review(review)
            
            if feedback['status'] == 'APPROVED':
                return {
                    "result": synthesis_result,
                    "approved": True,
                    "attempt": attempt,
                    "timestamp": datetime.utcnow().isoformat(),
                    "feedback": feedback
                }
            
            # If rejected, regenerate with feedback
            if attempt < self.max_retries:
                feedback_prompt = self._format_feedback(
                    feedback,
                    synthesis_result
                )
                
                synthesis_result = await self.synthesis_agent.run(
                    feedback_prompt
                )
                
                self.feedback_history.append(feedback)
        
        # Max retries reached - escalate
        return {
            "result": synthesis_result,
            "approved": False,
            "attempt": self.max_retries,
            "timestamp": datetime.utcnow().isoformat(),
            "feedback_history": self.feedback_history,
            "status": "ESCALATED_MAX_RETRIES"
        }
    
    def _parse_review(self, review: dict) -> dict:
        """Parse reviewer output"""
        # Extract status and feedback from review
        return {
            "status": review.get("status", "REJECTED"),
            "issues": review.get("issues", []),
            "suggestions": review.get("suggestions", []),
            "confidence": review.get("confidence", 0)
        }
    
    def _format_feedback(self, feedback: dict, previous_result: dict) -> str:
        """Format feedback into a regeneration prompt"""
        prompt = f"""
Previous analysis had the following issues:
{json.dumps(feedback['issues'], indent=2)}

Suggestions for improvement:
{json.dumps(feedback['suggestions'], indent=2)}

Please regenerate the analysis addressing these issues.
Previous result:
{json.dumps(previous_result, indent=2)}
"""
        return prompt
```

---

## Part 3: Technology Stack & Setup

### 3.1 Dependencies

```yaml
# Core LLM & Agents
langchain: ">=0.1.0"
langchain-anthropic: ">=0.1.0"
anthropic: ">=0.25.0"
langchain-community: ">=0.1.0"

# Database & Vector Search
sqlalchemy: ">=2.0.0"
psycopg2-binary: ">=2.9.0"
pgvector: ">=0.3.0"

# External APIs
newsapi: ">=1.0.0"
tavily-python: ">=1.0.0"
httpx: ">=0.25.0"

# Data & Processing
pydantic: ">=2.0.0"
pydantic-settings: ">=2.0.0"
numpy: ">=1.24.0"
pandas: ">=2.0.0"

# NLP & Text Analysis
nltk: ">=3.8.0"
textblob: ">=0.17.0"
spacy: ">=3.6.0"
transformers: ">=4.30.0"
sentence-transformers: ">=2.2.0"

# Sentiment & Emotion
transformers[torch]: ">=4.30.0"
torch: ">=2.0.0"

# API & Web
fastapi: ">=0.104.0"
uvicorn: ">=0.24.0"
requests: ">=2.31.0"

# Utilities
python-dotenv: ">=1.0.0"
loguru: ">=0.7.0"
pyyaml: ">=6.0"
```

### 3.2 Directory Structure

```
NarrativeWatch-AI/
├── .env.example
├── .env (ignored)
├── .gitignore
├── README.md
├── LLD_AND_TEAM_PLAN.md
├── requirements.txt
│
├── src/
│   ├── __init__.py
│   ├── config.py                 # Configuration management
│   ├── logger.py                 # Logging setup
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py         # Base agent class
│   │   ├── orchestrator.py       # Orchestrator Agent
│   │   ├── content_analyzer.py   # Content Analyzer Agent
│   │   ├── rag_agent.py          # RAG Agent
│   │   ├── research_agent.py     # Research Agent (Tavily)
│   │   ├── bias_detector.py      # Bias Detector Agent
│   │   ├── sentiment_analyzer.py # Sentiment Analyzer Agent
│   │   ├── narrative_tracker.py  # Narrative Tracker Agent
│   │   ├── synthesis_agent.py    # Synthesis Agent
│   │   └── reviewer_agent.py     # Reviewer Agent
│   │
│   ├── apis/
│   │   ├── __init__.py
│   │   ├── external_apis.py      # NewsAPI, Tavily, Claude
│   │   ├── newsapi_client.py     # NewsAPI wrapper
│   │   ├── tavily_client.py      # Tavily wrapper
│   │   └── claude_client.py      # Claude API wrapper
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py         # PostgreSQL connection
│   │   ├── models.py             # SQLAlchemy models
│   │   ├── rag_pipeline.py       # RAG ingestion & retrieval
│   │   └── migrations/           # Alembic migrations
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── search_tools.py       # Search and research tools
│   │   ├── analysis_tools.py     # Analysis tools
│   │   └── fact_check_tools.py   # Fact-checking tools
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── request.py            # Request models
│   │   ├── response.py           # Response models
│   │   └── enums.py              # Enums
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── text_processor.py     # Text processing
│   │   ├── embedding_utils.py    # Embedding generation
│   │   ├── scoring.py            # Trust score calculation
│   │   ├── validators.py         # Input validation
│   │   └── extractors.py         # Entity/claim extraction
│   │
│   ├── workflow/
│   │   ├── __init__.py
│   │   ├── orchestration.py      # Main orchestration logic
│   │   ├── reflection_loop.py    # Reflection loop logic
│   │   └── state_manager.py      # State management
│   │
│   └── app.py                    # FastAPI application
│
├── scripts/
│   ├── __init__.py
│   ├── setup_db.py               # Database initialization
│   ├── ingest_news.py            # Ingest articles from NewsAPI
│   └── run_demo.py               # Run demo analysis
│
├── tests/
│   ├── __init__.py
│   ├── test_agents.py
│   ├── test_apis.py
│   ├── test_rag.py
│   ├── test_reflection_loop.py
│   └── test_integration.py
│
├── notebooks/
│   ├── exploration.ipynb
│   └── testing.ipynb
│
└── docs/
    ├── API_REFERENCE.md
    ├── SETUP_GUIDE.md
    ├── DEPLOYMENT.md
    └── ARCHITECTURE.md
```

### 3.3 Environment Setup (.env.example)

```bash
# PostgreSQL Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=narrativewatch_ai
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password

# APIs
NEWSAPI_KEY=your_newsapi_key
TAVILY_API_KEY=your_tavily_key
CLAUDE_API_KEY=your_claude_api_key

# LangChain
LANGCHAIN_API_KEY=your_langchain_api_key
LANGCHAIN_TRACING_V2=true

# Application
DEBUG=false
LOG_LEVEL=INFO
APP_PORT=8000
APP_HOST=0.0.0.0

# Ray (optional, for distributed agents)
RAY_ENABLED=false
```

---

## Part 4: Team Structure & Role Assignments

### Team Member 1: **Rohan Urmude** (Project Lead / Orchestrator Lead)

**Responsibilities:**
1. Overall project coordination and timeline management
2. Orchestrator Agent development
3. Workflow orchestration logic
4. System integration and state management
5. Reflection loop implementation

**Deliverables:**
- [ ] `src/agents/orchestrator.py`
- [ ] `src/workflow/orchestration.py`
- [ ] `src/workflow/state_manager.py`
- [ ] `src/workflow/reflection_loop.py`
- [ ] Project timeline & milestones
- [ ] Integration test suite

**Timeline:** Week 1-4

---

### Team Member 2: **Backend/Database Specialist**

**Responsibilities:**
1. PostgreSQL + pgvector setup and configuration
2. Database schema design and migrations
3. RAG pipeline implementation
4. External API integration (NewsAPI, Tavily, Claude)
5. Research Agent development

**Deliverables:**
- [ ] `src/database/connection.py`
- [ ] `src/database/models.py`
- [ ] `src/database/rag_pipeline.py`
- [ ] `src/apis/newsapi_client.py`
- [ ] `src/apis/tavily_client.py`
- [ ] `src/apis/claude_client.py`
- [ ] `src/agents/rag_agent.py`
- [ ] `src/agents/research_agent.py`
- [ ] Database setup script

**Timeline:** Week 1-3

---

### Team Member 3: **NLP/Text Analysis Specialist**

**Responsibilities:**
1. Content Analyzer Agent development
2. Bias detection implementation
3. Sentiment analysis implementation
4. Text processing utilities
5. Entity and claim extraction

**Deliverables:**
- [ ] `src/agents/content_analyzer.py`
- [ ] `src/agents/bias_detector.py`
- [ ] `src/agents/sentiment_analyzer.py`
- [ ] `src/utils/text_processor.py`
- [ ] `src/utils/extractors.py`
- [ ] `src/tools/analysis_tools.py`
- [ ] Unit tests for agents

**Timeline:** Week 2-3

---

### Team Member 4: **Data Analysis/Synthesis Specialist**

**Responsibilities:**
1. Narrative Tracker Agent development
2. Synthesis Agent implementation
3. Trust score calculation algorithm
4. Reviewer Agent implementation
5. Quality assurance logic

**Deliverables:**
- [ ] `src/agents/narrative_tracker.py`
- [ ] `src/agents/synthesis_agent.py`
- [ ] `src/agents/reviewer_agent.py`
- [ ] `src/utils/scoring.py`
- [ ] Quality assurance test suite
- [ ] Validation metrics document

**Timeline:** Week 2-4

---

### Team Member 5: **Full-Stack Developer** (Optional but recommended)

**Responsibilities:**
1. FastAPI service setup and endpoints
2. Request/response models
3. API service deployment
4. Demo application development
5. Documentation

**Deliverables:**
- [ ] `src/app.py`
- [ ] `src/models/request.py` & `response.py`
- [ ] Demo CLI or web interface
- [ ] `docs/SETUP_GUIDE.md`
- [ ] `docs/API_REFERENCE.md`
- [ ] Setup and run scripts

**Timeline:** Week 3-4

---

## Part 5: Detailed Milestones & Timeline

### **Phase 1: Setup & Infrastructure (Week 1)**

#### Milestone 1.1: Development Environment Setup
**Owner:** Rohan + Backend Specialist  
**Tasks:**
- [ ] Create Git repository with proper structure
- [ ] Set up `.env.example` configuration
- [ ] Configure logging system
- [ ] Set up Python virtual environment
- [ ] Create requirements.txt with all dependencies

**Success Criteria:**
- Team can clone and setup locally
- All dependencies install without issues
- Logging works correctly

---

#### Milestone 1.2: PostgreSQL + pgvector Setup
**Owner:** Backend Specialist  
**Tasks:**
- [ ] Install PostgreSQL locally or cloud
- [ ] Install pgvector extension
- [ ] Design database schema
- [ ] Implement SQLAlchemy models
- [ ] Create database initialization script
- [ ] Test connection and basic operations

**Deliverables:**
- Running PostgreSQL with pgvector
- `src/database/models.py` complete
- `src/database/connection.py` complete
- `scripts/setup_db.py` ready

**Success Criteria:**
- Can create/read/update/delete records
- Vector operations work correctly
- Schema supports all agent needs

---

#### Milestone 1.3: External APIs Setup
**Owner:** Backend Specialist  
**Tasks:**
- [ ] Set up NewsAPI account and get API key
- [ ] Set up Tavily API account
- [ ] Verify Claude API access
- [ ] Create API wrapper classes
- [ ] Test all APIs with sample requests
- [ ] Document rate limits and quotas

**Deliverables:**
- All API credentials in `.env`
- API wrapper classes skeleton
- Test scripts for each API
- Rate limit documentation

**Success Criteria:**
- All APIs responding correctly
- Rate limits understood and handled
- Error handling in place

---

#### Milestone 1.4: Base Agent Architecture
**Owner:** Rohan  
**Tasks:**
- [ ] Create BaseAgent class with LangChain integration
- [ ] Set up agent executor pattern
- [ ] Configure Claude as LLM backend
- [ ] Implement agent logging
- [ ] Create tool system for agents
- [ ] Test base agent with simple tool

**Deliverables:**
- `src/agents/base_agent.py` complete
- LangChain + Claude integration working
- Simple test agent running
- Tool system tested

**Success Criteria:**
- Can create and run agents
- Agents execute tools correctly
- Logging captures agent execution

---

### **Phase 2: Agent Development (Week 2-3)**

#### Milestone 2.1: RAG Pipeline
**Owner:** Backend Specialist  
**Tasks:**
- [ ] Implement embedding generation with Claude
- [ ] Create RAG ingestion pipeline
- [ ] Implement pgvector similarity search
- [ ] Build article storage and retrieval
- [ ] Create test data and validation
- [ ] Optimize vector search queries

**Deliverables:**
- `src/database/rag_pipeline.py` complete
- Embedding utils working
- Test data loaded
- Vector search tested

**Success Criteria:**
- Embeddings generated correctly
- Similarity search returns relevant results
- Handles 10k+ articles efficiently
- Search performance < 500ms

---

#### Milestone 2.2: Content & Analysis Agents
**Owner:** NLP Specialist  
**Tasks:**
- [ ] Implement Content Analyzer Agent
- [ ] Build text preprocessing pipeline
- [ ] Implement article feature extraction
- [ ] Create headline sensationalism detection
- [ ] Build unit tests
- [ ] Test with real articles

**Deliverables:**
- `src/agents/content_analyzer.py` complete
- Text processing utilities
- Feature extraction working
- Unit tests (80%+ coverage)

**Success Criteria:**
- Correctly analyzes article structure
- Extracts all key features
- Handles various text formats
- Performance < 2s per article

---

#### Milestone 2.3: Bias & Sentiment Agents
**Owner:** NLP Specialist  
**Tasks:**
- [ ] Implement Bias Detector Agent
- [ ] Build political leaning detection
- [ ] Implement Sentiment Analyzer Agent
- [ ] Add emotional intensity scoring
- [ ] Create manipulation detection
- [ ] Build integration tests

**Deliverables:**
- `src/agents/bias_detector.py` complete
- `src/agents/sentiment_analyzer.py` complete
- Detection models integrated
- Test suite with real articles

**Success Criteria:**
- Detects bias indicators accurately
- Sentiment analysis matches human review
- Identifies emotional manipulation
- Performance < 3s per analysis

---

#### Milestone 2.4: Research & RAG Agents
**Owner:** Backend Specialist  
**Tasks:**
- [ ] Implement RAG Agent with vector search
- [ ] Implement Research Agent with Tavily
- [ ] Build API result aggregation
- [ ] Create fact-checking integration
- [ ] Add result validation
- [ ] Integration testing

**Deliverables:**
- `src/agents/rag_agent.py` complete
- `src/agents/research_agent.py` complete
- Integration tests
- API response handling

**Success Criteria:**
- RAG retrieves similar articles
- Research finds current information
- Results properly aggregated
- Performance < 5s for research

---

#### Milestone 2.5: Narrative & Synthesis Agents
**Owner:** Data Analysis Specialist  
**Tasks:**
- [ ] Implement Narrative Tracker Agent
- [ ] Build cross-article correlation
- [ ] Implement Synthesis Agent
- [ ] Create report generation
- [ ] Build trust score algorithm
- [ ] Create test suite

**Deliverables:**
- `src/agents/narrative_tracker.py` complete
- `src/agents/synthesis_agent.py` complete
- Trust score logic
- Report generation working

**Success Criteria:**
- Detects narrative clusters
- Synthesis creates coherent reports
- Trust scores are accurate
- Reports include evidence

---

#### Milestone 2.6: Reviewer Agent & Reflection Loop
**Owner:** Data Analysis Specialist  
**Tasks:**
- [ ] Implement Reviewer Agent
- [ ] Build evaluation criteria
- [ ] Implement reflection loop logic
- [ ] Create retry mechanism
- [ ] Build escalation handling
- [ ] Full testing

**Deliverables:**
- `src/agents/reviewer_agent.py` complete
- `src/workflow/reflection_loop.py` complete
- Reflection loop tests
- Escalation handling

**Success Criteria:**
- Reviewer evaluates accurately
- Loop converges in ≤3 iterations
- Escalation works correctly
- Quality improves with iterations

---

### **Phase 3: Integration & Service (Week 3-4)**

#### Milestone 3.1: Workflow Orchestration
**Owner:** Rohan  
**Tasks:**
- [ ] Implement main orchestration logic
- [ ] Build task routing and queuing
- [ ] Implement state management
- [ ] Create error handling
- [ ] Build retry logic
- [ ] End-to-end workflow testing

**Deliverables:**
- `src/workflow/orchestration.py` complete
- `src/workflow/state_manager.py` complete
- Error handling documented
- Workflow diagram

**Success Criteria:**
- All agents execute in order
- State properly managed
- Errors don't crash system
- Failed tasks can retry

---

#### Milestone 3.2: FastAPI Service
**Owner:** Full-Stack Developer  
**Tasks:**
- [ ] Build FastAPI application
- [ ] Create request/response models
- [ ] Implement API endpoints
- [ ] Add request validation
- [ ] Create API documentation
- [ ] Build service tests

**Deliverables:**
- `src/app.py` complete
- Request/response models
- OpenAPI documentation
- Service test suite

**Success Criteria:**
- API accepts valid requests
- Returns proper responses
- Validates input correctly
- Documentation complete

---

#### Milestone 3.3: Integration & Performance Testing
**Owner:** Rohan + Full-Stack Developer  
**Tasks:**
- [ ] Create integration test suite
- [ ] Test complete workflow end-to-end
- [ ] Performance benchmarking
- [ ] Load testing
- [ ] Identify bottlenecks
- [ ] Optimize critical paths

**Deliverables:**
- Integration test suite
- Performance report
- Optimization recommendations
- Benchmarks documented

**Success Criteria:**
- Full workflow completes successfully
- Response time < 30s for full analysis
- No data loss or corruption
- Handles edge cases

---

### **Phase 4: Demo & Deployment (Week 4)**

#### Milestone 4.1: Demo Application
**Owner:** Full-Stack Developer  
**Tasks:**
- [ ] Create demo interface (CLI/Web)
- [ ] Prepare demo scenarios
- [ ] Create sample articles
- [ ] Script demo walkthrough
- [ ] Test end-to-end
- [ ] Create demo documentation

**Deliverables:**
- Working demo application
- Demo scenarios with articles
- Demo walkthrough script
- Demo documentation

**Success Criteria:**
- Demo runs without errors
- Shows all agent capabilities
- Completes in < 5 minutes
- Results are impressive

---

#### Milestone 4.2: Documentation
**Owner:** All (Rohan coordinates)  
**Tasks:**
- [ ] Write API documentation
- [ ] Write setup guide
- [ ] Write deployment guide
- [ ] Create architecture diagrams
- [ ] Write agent descriptions
- [ ] Create troubleshooting guide

**Deliverables:**
- Complete API documentation
- Setup guide
- Deployment guide
- Architecture diagrams
- Agent runbooks

**Success Criteria:**
- Anyone can setup from docs
- All APIs documented
- Deployment process clear
- Architecture understood

---

#### Milestone 4.3: Deployment
**Owner:** Full-Stack Developer  
**Tasks:**
- [ ] Prepare production configuration
- [ ] Set up environment variables
- [ ] Optimize database indexes
- [ ] Create backup strategy
- [ ] Set up monitoring (optional)
- [ ] Deploy to staging/production

**Deliverables:**
- Production configuration
- Deployment checklist
- Monitoring setup (optional)
- Running deployment

**Success Criteria:**
- System runs in production
- All services healthy
- Performance acceptable
- Monitoring in place

---

#### Milestone 4.4: Final Testing & QA
**Owner:** All (Rohan coordinates)  
**Tasks:**
- [ ] Final functionality testing
- [ ] Security review
- [ ] Performance validation
- [ ] Documentation review
- [ ] Sign-off process
- [ ] Demo preparation

**Deliverables:**
- Final test report
- Security assessment
- Performance report
- Sign-off document

**Success Criteria:**
- All features working
- No critical bugs
- Security verified
- Ready for presentation

---

## Part 6: Detailed Agent Implementation Guide

### ContentAnalyzer Agent Example

```python
# src/agents/content_analyzer.py
from typing import List, Dict, Any
from src.agents.base_agent import BaseAgent
from src.tools.analysis_tools import (
    extract_headline_sensationalism,
    extract_key_claims,
    extract_entities,
    analyze_structure
)

class ContentAnalyzerAgent(BaseAgent):
    def __init__(self):
        tools = [
            extract_headline_sensationalism,
            extract_key_claims,
            extract_entities,
            analyze_structure
        ]
        
        super().__init__(
            name="Content Analyzer",
            description="""You are an expert content analyzer. Your role is to:
1. Extract and analyze the main claims in articles
2. Identify sensationalism in headlines
3. Extract key entities (people, places, organizations)
4. Analyze article structure and flow
5. Identify emotional language patterns
            
Provide structured analysis with clear metrics.""",
            tools=tools
        )
    
    async def analyze_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a news article"""
        prompt = f"""
Analyze this news article thoroughly:

Title: {article['title']}
Source: {article['source']}
Published: {article['published_at']}

Content:
{article['content']}

Please provide:
1. Sensationalism score (0-100)
2. Key claims made in the article
3. Main entities mentioned
4. Emotional language indicators
5. Factual vs opinion content breakdown
        """
        
        result = await self.run(prompt)
        return result
```

---

## Part 7: API Endpoints Specification

```python
# FastAPI endpoints for analysis

POST /api/v1/analyze/article
- Input: {"url": "https://..."} or {"content": "..."}
- Output: Full analysis report

POST /api/v1/analyze/topic
- Input: {"topic": "...", "days": 7}
- Output: Narrative analysis across multiple articles

POST /api/v1/articles/search
- Input: {"query": "...", "limit": 10}
- Output: List of relevant articles

GET /api/v1/narratives
- Output: Current narrative clusters

GET /api/v1/health
- Output: System status
```

---

## Part 8: Database Setup Instructions

```bash
# Install PostgreSQL (if not installed)
# macOS: brew install postgresql
# Linux: sudo apt-get install postgresql postgresql-contrib
# Windows: Download from postgresql.org

# Start PostgreSQL
# macOS/Linux: brew services start postgresql
# Windows: Start PostgreSQL service

# Install pgvector
sudo -u postgres psql
CREATE EXTENSION IF NOT EXISTS vector;

# Create database
createdb narrativewatch_ai

# Run migrations
python scripts/setup_db.py
```

---

## Part 9: Success Criteria & Definition of Done

### FDE Requirements Met ✓
- [x] LangChain for agent orchestration
- [x] Multiple specialized agents (9 total)
- [x] Reflection loop with quality verification
- [x] Vector database integration (pgvector)
- [x] External API integration (NewsAPI, Tavily)
- [x] Claude API for intelligence
- [x] Trust scoring system
- [x] Live demonstration capability

### System-Level Criteria
- [ ] All 9 agents implemented and tested
- [ ] Reflection loop converges in ≤3 iterations
- [ ] Vector DB populated with articles
- [ ] APIs integrated with rate limiting
- [ ] Full end-to-end workflow tested
- [ ] Demo runs successfully
- [ ] Documentation complete
- [ ] All tests passing (90%+ coverage)

---

## Part 10: Quick Start Guide

```bash
# 1. Clone repository
git clone <repo-url>
cd NarrativeWatch-AI

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment
cp .env.example .env
# Edit .env with your API keys

# 5. Set up database
python scripts/setup_db.py

# 6. Ingest sample articles
python scripts/ingest_news.py --query "technology" --limit 100

# 7. Run demo
python scripts/run_demo.py

# 8. Start API service (optional)
uvicorn src.app:app --reload

# 9. Access API at http://localhost:8000/docs
```

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-06-12 | Rohan | Initial LLD & Team Plan |
| 2.0 | 2026-06-12 | Rohan | Updated: NewsAPI instead of Instagram, PostgreSQL + pgvector, no Docker |

---

## Next Steps

1. **Review & Approval:** Get team approval on this plan
2. **Setup Week 1:** Begin infrastructure setup
3. **Agent Development:** Parallel development starting Week 2
4. **Integration:** Full system integration Week 3
5. **Demo:** Final demo preparation Week 4
6. **Presentation:** FDE requirement submission

---

# NarrativeWatch AI - Low Level Design & Team Implementation Plan

**Project:** NarrativeWatch AI - Multi-Agent Social Media Intelligence Platform  
**FDE Requirement:** Build an Agentic Application using LangChain  
**Date:** June 2026  
**Status:** Planning Phase

---

## Executive Summary

NarrativeWatch AI is a multi-agent system that analyzes Instagram pages to detect misleading content, emotional manipulation, bias, and coordinated influence campaigns. The system orchestrates specialized agents to perform content analysis, fact verification, bot detection, and campaign tracking, with a Reviewer Agent ensuring quality through reflection loops.

**Mandatory Stack:**
- LangChain for agent orchestration
- Tavily Search for external research
- PostgreSQL + pgvector for RAG (vector embeddings in relational DB)
- Vertex AI / Gemini 2.5 for intelligence (20x cost savings)
- Instagram API / Web Scraping for data ingestion

---

## Part 1: System Architecture & Agent Workflow

### 1.1 High-Level System Flow

```
User Query (Instagram Page/Post Analysis)
    ↓
[Orchestrator Agent] - Route & Coordinate
    ├→ [Content Analyzer Agent] - Extract & Classify
    ├→ [RAG Agent] - Retrieve Similar Patterns
    ├→ [Research Agent] - Tavily + External APIs
    ├→ [Bias Detector Agent] - Identify Bias
    ├→ [Bot Detector Agent] - Analyze Engagement
    ├→ [Campaign Detector Agent] - Cross-page Correlation
    ├→ [Synthesis Agent] - Combine Findings
    └→ [Reviewer Agent] - Quality Check & Reflection Loop
         ├→ [APPROVED] → Trust Score + Report
         └→ [REJECTED] → Feedback → Regenerate (max 3 retries)
    ↓
JSON Report + Trust Score (0-100)
```

### 1.2 Agent Specifications

#### **Agent 1: Orchestrator Agent**
- **Role:** Coordinates workflow, routes tasks, manages state
- **Input:** User query (Instagram page/post URL or text)
- **Output:** Routing decisions, task queue
- **Key Responsibilities:**
  - Parse user input
  - Determine required agents
  - Manage execution order
  - Aggregate results
  - Handle retry logic
- **Tools:** LangChain Agent, State Management

#### **Agent 2: Content Analyzer Agent**
- **Role:** Extract and classify post/page content
- **Input:** Instagram data (text, captions, hashtags)
- **Output:** Structured content features
- **Analysis:**
  - Emotional language classification
  - Narrative themes
  - Hashtag patterns
  - Post timing & frequency
  - Engagement metrics
- **Tools:** NLP, Pattern Matching

#### **Agent 3: RAG Agent**
- **Role:** Retrieve similar patterns from knowledge base
- **Input:** Content features + Query embeddings
- **Output:** Similar campaigns, posts, patterns
- **Implementation:**
  - Vector embeddings (Vertex AI text-embedding-005)
  - PostgreSQL pgvector queries (similarity search)
  - SQL-based similarity matching
  - Historical context retrieval from relational DB
- **Tools:** LangChain RAG, PostgreSQL + pgvector

#### **Agent 4: Research Agent**
- **Role:** Gather external information via Tavily + APIs
- **Input:** Topics, claims, hashtags, usernames
- **Output:** External validation data, fact-checks
- **Implementation:**
  - Tavily Search queries
  - Instagram API (graph-api)
  - Twitter API for cross-platform correlation
  - Fact-checking APIs (NewsGuard, ClaimBuster)
- **Tools:** Tavily, REST APIs, Web scraping

#### **Agent 5: Bias Detector Agent**
- **Role:** Identify political, gender, or ideological bias
- **Input:** Post content, language patterns
- **Output:** Bias scores, detected biases
- **Analysis:**
  - Political leaning detection
  - Gender representation
  - Source credibility
  - Language toxicity
- **Tools:** Hugging Face bias models, VADER sentiment

#### **Agent 6: Bot Detector Agent**
- **Role:** Analyze engagement patterns for bot activity
- **Input:** Comments, likes, follower data
- **Output:** Bot activity indicators
- **Analysis:**
  - Comment authenticity
  - Like velocity patterns
  - Follower growth anomalies
  - Coordinated engagement detection
- **Tools:** Statistical analysis, ML models

#### **Agent 7: Campaign Detector Agent**
- **Role:** Identify coordinated influence campaigns
- **Input:** Multiple pages, hashtags, timing patterns
- **Output:** Campaign clusters, coordination evidence
- **Analysis:**
  - Cross-page hashtag overlap
  - Timing correlation
  - Narrative similarity
  - Account relationship mapping
- **Tools:** Graph analysis, clustering

#### **Agent 8: Synthesis Agent**
- **Role:** Combine all findings into coherent report
- **Input:** Results from all agents
- **Output:** Integrated findings, narrative summary
- **Calculation:**
  - Trust score (0-100)
  - Risk flags
  - Evidence ranking
  - Recommendation
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
- **Retry Logic:**
  - Max 3 regeneration attempts
  - Track issues across retries
  - Escalate on max retries

---

## Part 2: Technical Implementation Details

### 2.1 Vector Database Design

#### **PostgreSQL + pgvector Setup** (Recommended)
```python
# Database Schema with SQLAlchemy + pgvector
from pgvector.sqlalchemy import Vector

class InstagramPost(Base):
    __tablename__ = "instagram_posts"
    
    post_id = Column(String, primary_key=True)
    page_username = Column(String, index=True)
    caption = Column(Text)
    hashtags = Column(JSON)
    engagement_metrics = Column(JSON)
    posting_time = Column(DateTime)
    embedding = Column(Vector(1536))  # pgvector column
    campaign_cluster = Column(String)
    trust_score = Column(Float)
    analysis_results = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class Campaign(Base):
    __tablename__ = "campaigns"
    
    campaign_id = Column(String, primary_key=True)
    pages_involved = Column(JSON)
    hashtags = Column(JSON)
    narrative_theme = Column(Text)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    evidence_count = Column(Integer)
    cluster_embedding = Column(Vector(1536))  # pgvector

class BiasPattern(Base):
    __tablename__ = "bias_patterns"
    
    pattern_id = Column(String, primary_key=True)
    bias_type = Column(String)  # political, gender, ideological
    indicators = Column(JSON)
    frequency = Column(Integer)
    similar_posts = Column(JSON)
    pattern_embedding = Column(Vector(1536))  # pgvector
```

#### **RAG Pipeline**
1. **Ingestion:** Instagram data → text preprocessing → embeddings
2. **Storage:** Vector embeddings in PostgreSQL with pgvector
3. **Query:** User query → embedding → SQL similarity search (top-k)
4. **Retrieval:** Similar posts, campaigns, patterns via pgvector similarity
5. **Context:** Feed into RAG agent for analysis

### 2.2 External APIs Integration

```python
# API Layer
class ExternalAPIs:
    
    # Tavily Search
    tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
    
    # Instagram Graph API
    instagram_api = InstagramAPI(access_token=INSTA_TOKEN)
    
    # LLM (Vertex AI Gemini 2.5)
    gemini_client = ChatVertexAI(model_name="gemini-2.5-pro")
    
    # Fact-checking
    newsguard_api = NewsGuardAPI(api_key=NEWSGUARD_KEY)
    claimster_api = ClaimBusterAPI(api_key=CLAIMSTER_KEY)
    
    # Twitter API (for cross-platform)
    twitter_client = tweepy.Client(bearer_token=TWITTER_TOKEN)
```

### 2.3 LangChain Agent Implementation Pattern

```python
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.tools import Tool
from langchain_google_vertexai import ChatVertexAI

class BaseAgent:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.llm = ChatVertexAI(model_name="gemini-2.5-pro")
        self.tools = self._define_tools()
        self.executor = self._create_executor()
    
    def _define_tools(self) -> list[Tool]:
        """Override in subclasses"""
        return []
    
    def _create_executor(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"You are {self.name}. {self.description}"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        agent = create_tool_calling_agent(self.llm, self.tools, prompt)
        return AgentExecutor.from_agent_and_tools(
            agent=agent, 
            tools=self.tools, 
            verbose=True,
            max_iterations=5
        )
    
    def run(self, input_data: str) -> dict:
        return self.executor.invoke({"input": input_data})
```

### 2.4 Reflection Loop Implementation

```python
class ReflectionLoop:
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.retry_count = 0
        self.feedback_history = []
    
    def execute_with_review(self, synthesis_result: dict) -> dict:
        """
        Execute synthesis and review with reflection loop
        """
        for attempt in range(1, self.max_retries + 1):
            # Get reviewer feedback
            feedback = self.reviewer_agent.run(synthesis_result)
            
            if feedback['status'] == 'APPROVED':
                return {
                    "result": synthesis_result,
                    "approved": True,
                    "attempt": attempt
                }
            
            # Regenerate with feedback
            feedback_prompt = self._format_feedback(feedback)
            synthesis_result = self.synthesis_agent.run(
                original_query=synthesis_result['original_query'],
                agent_results=synthesis_result['agent_results'],
                reviewer_feedback=feedback_prompt
            )
            
            self.feedback_history.append(feedback)
        
        # Max retries reached
        return {
            "result": synthesis_result,
            "approved": False,
            "attempt": self.max_retries,
            "feedback_history": self.feedback_history,
            "status": "ESCALATED"
        }
```

---

## Part 3: Technology Stack & Setup

### 3.1 Dependencies

```yaml
# Core LLM & Agents
langchain: ">=0.1.0"
langchain-google-vertexai: ">=0.1.0"  # Using Vertex AI Gemini 2.5
langchain-community: ">=0.1.0"

# Database & Vector Search
sqlalchemy: ">=2.0.0"
psycopg2-binary: ">=2.9.0"  # PostgreSQL driver
pgvector: ">=0.3.0"  # PostgreSQL vector extension

# External APIs
tavily-python: ">=1.0.0"
instagrapi: ">=2.0.0"  # Instagram API wrapper
tweepy: ">=4.14.0"

# Data & Processing
pydantic: ">=2.0.0"
numpy: ">=1.24.0"
pandas: ">=2.0.0"

# NLP & ML
sentence-transformers: ">=2.2.0"
transformers: ">=4.30.0"  # For bias detection
nltk: ">=3.8.0"
textblob: ">=0.17.0"

# Web & API
requests: ">=2.31.0"
fastapi: ">=0.104.0"
pydantic-settings: ">=2.0.0"

# Utilities
python-dotenv: ">=1.0.0"
loguru: ">=0.7.0"
```

### 3.2 Directory Structure

```
NarrativeWatch-AI/
├── .env.example
├── .env (ignored)
├── .gitignore
├── requirements.txt
├── README.md
├── LLD_AND_TEAM_PLAN.md
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
│   │   ├── bot_detector.py       # Bot Detector Agent
│   │   ├── campaign_detector.py  # Campaign Detector Agent
│   │   ├── synthesis_agent.py    # Synthesis Agent
│   │   └── reviewer_agent.py     # Reviewer Agent
│   │
│   ├── apis/
│   │   ├── __init__.py
│   │   ├── instagram_api.py      # Instagram Graph API wrapper
│   │   ├── tavily_api.py         # Tavily Search wrapper
│   │   ├── twitter_api.py        # Twitter API wrapper
│   │   ├── fact_check_api.py     # Fact-checking APIs
│   │   └── llm_client.py         # LLM client (Claude)
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── weaviate_client.py    # Vector DB client
│   │   ├── schema.py             # Weaviate schema definition
│   │   └── rag_pipeline.py       # RAG ingestion & retrieval
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── request.py            # Request models
│   │   ├── response.py           # Response models
│   │   └── enums.py              # Enums
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── text_processor.py     # Text processing utilities
│   │   ├── embedding_utils.py    # Embedding generation
│   │   ├── scoring.py            # Trust score calculation
│   │   └── validators.py         # Input validation
│   │
│   ├── workflow/
│   │   ├── __init__.py
│   │   ├── orchestration.py      # Main orchestration logic
│   │   ├── reflection_loop.py    # Reflection loop logic
│   │   └── state_manager.py      # State management
│   │
│   └── app.py                    # FastAPI application
│
├── tests/
│   ├── __init__.py
│   ├── test_agents.py
│   ├── test_apis.py
│   ├── test_rag.py
│   └── test_integration.py
│
├── notebooks/
│   ├── exploration.ipynb
│   └── testing.ipynb
│
└── docs/
    ├── API_REFERENCE.md
    ├── SETUP_GUIDE.md
    └── DEPLOYMENT.md
```

---

## Part 4: Team Structure & Role Assignments

### Team Composition
Assuming 4-6 team members. Adjust based on actual team size.

---

## Team Member 1: **Rohan Urmude** (Project Lead / Orchestrator Lead)

### Responsibilities:
1. **Overall Project Coordination**
   - Create and maintain project timeline
   - Conduct bi-weekly team sync
   - Monitor progress against milestones
   - Resolve blockers and dependencies

2. **Orchestrator Agent Development**
   - Design orchestrator architecture
   - Implement task routing logic
   - Build state management system
   - Integration testing of workflow

3. **System Integration**
   - Ensure all agents communicate properly
   - Build reflection loop logic
   - API coordination between modules
   - Error handling and fallback strategies

### Deliverables:
- [ ] `src/agents/orchestrator.py` - Complete implementation
- [ ] `src/workflow/orchestration.py` - Main workflow logic
- [ ] `src/workflow/state_manager.py` - State management
- [ ] Project timeline & milestones doc
- [ ] Integration test suite

### Timeline: Week 1-4 (with dependencies from other members)

---

## Team Member 2: **Backend/API Specialist**

### Responsibilities:
1. **RAG Agent & Vector Database**
   - Set up Weaviate instance
   - Design schema and data models
   - Implement RAG pipeline
   - Embedding generation

2. **External API Integration**
   - Build Tavily API wrapper
   - Implement Instagram Graph API client
   - Twitter API integration
   - Fact-checking API integration

3. **Research Agent Development**
   - Implement research agent using APIs
   - Query optimization
   - Response aggregation

### Deliverables:
- [ ] `src/database/weaviate_client.py` - Full implementation
- [ ] `src/database/schema.py` - Schema design
- [ ] `src/database/rag_pipeline.py` - RAG logic
- [ ] `src/apis/tavily_api.py` - Tavily wrapper
- [ ] `src/apis/instagram_api.py` - Instagram wrapper
- [ ] `src/agents/rag_agent.py` - RAG agent
- [ ] `src/agents/research_agent.py` - Research agent
- [ ] API documentation

### Timeline: Week 1-3

---

## Team Member 3: **ML/NLP Specialist**

### Responsibilities:
1. **Content Analysis**
   - Implement content analyzer agent
   - NLP preprocessing pipeline
   - Pattern extraction

2. **Bias Detection**
   - Integrate bias detection models
   - Implement bias analyzer agent
   - Score calculation

3. **Bot Detection**
   - Build statistical analysis models
   - Implement bot detector agent
   - Engagement pattern analysis

### Deliverables:
- [ ] `src/agents/content_analyzer.py` - Complete implementation
- [ ] `src/agents/bias_detector.py` - Complete implementation
- [ ] `src/agents/bot_detector.py` - Complete implementation
- [ ] `src/utils/text_processor.py` - Text processing utilities
- [ ] `src/utils/embedding_utils.py` - Embedding utilities
- [ ] ML model selection document
- [ ] Unit tests for agents

### Timeline: Week 2-3

---

## Team Member 4: **Senior Data/Analytics Engineer**

### Responsibilities:
1. **Campaign Detection**
   - Graph analysis implementation
   - Clustering algorithms
   - Cross-page correlation logic

2. **Synthesis & Scoring**
   - Build synthesis agent
   - Trust score calculation algorithm
   - Report generation logic

3. **Quality Assurance & Reviewer Agent**
   - Implement reviewer agent
   - Reflection loop logic
   - Validation criteria definition

### Deliverables:
- [ ] `src/agents/campaign_detector.py` - Complete implementation
- [ ] `src/agents/synthesis_agent.py` - Complete implementation
- [ ] `src/agents/reviewer_agent.py` - Complete implementation
- [ ] `src/workflow/reflection_loop.py` - Reflection loop
- [ ] `src/utils/scoring.py` - Scoring logic
- [ ] Quality assurance test suite
- [ ] Validation metrics document

### Timeline: Week 2-4

---

## Team Member 5: **Frontend/Full-Stack Developer** (Optional)

### Responsibilities:
1. **API Service Setup**
   - Build FastAPI application
   - Endpoint design and implementation
   - Request/response models

2. **Live Demonstration Setup**
   - Create demo interface (web/CLI)
   - Integration with agents
   - Result visualization

3. **Deployment & Documentation**
   - Docker containerization
   - Deployment guide
   - User documentation

### Deliverables:
- [ ] `src/app.py` - FastAPI application
- [ ] `src/models/request.py` & `response.py` - Data models
- [ ] Demo application (web or CLI)
- [ ] `docs/SETUP_GUIDE.md` - Setup instructions
- [ ] `docs/DEPLOYMENT.md` - Deployment guide
- [ ] Docker configuration

### Timeline: Week 3-4

---

## Team Member 6: **QA & Testing Lead** (Optional)

### Responsibilities:
1. **Test Planning & Execution**
   - Create test cases for all agents
   - Integration testing
   - End-to-end workflow testing

2. **Performance & Reliability**
   - Load testing
   - Error scenario testing
   - Resilience validation

3. **Demo Preparation**
   - Prepare test data
   - Create demo scenarios
   - Validate all flows work end-to-end

### Deliverables:
- [ ] `tests/test_agents.py` - Agent unit tests
- [ ] `tests/test_apis.py` - API integration tests
- [ ] `tests/test_rag.py` - RAG pipeline tests
- [ ] `tests/test_integration.py` - End-to-end tests
- [ ] Test report with coverage metrics
- [ ] Demo test data sets

### Timeline: Week 2-4 (ongoing)

---

## Part 5: Detailed Milestones & Timeline

### **Phase 1: Setup & Infrastructure (Week 1)**

#### Milestone 1.1: Development Environment
**Owner:** Rohan + Backend Specialist  
**Tasks:**
- [ ] Create Git repository with proper structure
- [ ] Set up `.env.example` and configuration management
- [ ] Set up logging and monitoring
- [ ] Initialize Docker environment
- [ ] Create requirements.txt with all dependencies

**Deliverables:**
- Git repo with directory structure
- `.env.example` file
- `src/config.py` ready for use
- Docker setup script

**Success Criteria:**
- All team members can clone and run setup
- No missing dependencies
- Logging works correctly

---

#### Milestone 1.2: Vector Database Setup
**Owner:** Backend Specialist  
**Tasks:**
- [ ] Provision Weaviate instance (local/cloud)
- [ ] Design and implement database schema
- [ ] Test connection and basic operations
- [ ] Create schema initialization script
- [ ] Document connection requirements

**Deliverables:**
- Running Weaviate instance
- `src/database/schema.py` with full schema
- `src/database/weaviate_client.py` with client
- Connection test script

**Success Criteria:**
- Can create/read/update/delete objects
- Schema matches design
- Supports 10M+ documents

---

#### Milestone 1.3: External API Setup
**Owner:** Backend Specialist  
**Tasks:**
- [ ] Set up Tavily Search API and test
- [ ] Get Instagram Graph API credentials and test
- [ ] Set up Twitter API (optional) and test
- [ ] Create API wrapper classes skeleton
- [ ] Document API endpoints and rate limits

**Deliverables:**
- All API credentials in `.env`
- Test scripts for each API
- API wrapper class skeletons
- Rate limiting documentation

**Success Criteria:**
- All APIs responding correctly
- Rate limits understood
- Error handling in place

---

#### Milestone 1.4: Base Agent Architecture
**Owner:** Rohan  
**Tasks:**
- [ ] Create `BaseAgent` class with tool support
- [ ] Set up LangChain integration
- [ ] Implement agent executor pattern
- [ ] Create logging for agents
- [ ] Test base agent with simple tool

**Deliverables:**
- `src/agents/base_agent.py` fully implemented
- Simple test agent working
- Logging configured
- Documentation on agent pattern

**Success Criteria:**
- Can create and run simple agents
- Logging works correctly
- Tools integrate properly with LangChain

---

### **Phase 2: Agent Development (Week 2-3)**

#### Milestone 2.1: RAG Pipeline
**Owner:** Backend Specialist  
**Tasks:**
- [ ] Implement embedding generation (OpenAI/Cohere)
- [ ] Create RAG ingestion pipeline
- [ ] Build similarity search logic
- [ ] Implement retrieval augmentation
- [ ] Create test data and validation

**Deliverables:**
- `src/database/rag_pipeline.py` complete
- `src/utils/embedding_utils.py` complete
- RAG ingestion script
- Test dataset loaded into Weaviate

**Success Criteria:**
- Embeddings generated correctly
- Similarity search returns relevant results
- Can handle 10k+ documents efficiently

---

#### Milestone 2.2: Content Analysis Agents
**Owner:** ML/NLP Specialist  
**Tasks:**
- [ ] Implement Content Analyzer Agent
- [ ] Build text preprocessing pipeline
- [ ] Implement hashtag and pattern extraction
- [ ] Create emotional language classifier
- [ ] Build unit tests

**Deliverables:**
- `src/agents/content_analyzer.py` complete
- `src/utils/text_processor.py` complete
- Unit tests with 80%+ coverage
- Sample analysis outputs

**Success Criteria:**
- Correctly extracts all content features
- Handles various text formats
- Performance: < 2s per post

---

#### Milestone 2.3: Research & RAG Agents
**Owner:** Backend Specialist  
**Tasks:**
- [ ] Implement RAG Agent with vector search
- [ ] Implement Research Agent with Tavily
- [ ] Build API result aggregation
- [ ] Create result validation
- [ ] Integration testing

**Deliverables:**
- `src/agents/rag_agent.py` complete
- `src/agents/research_agent.py` complete
- Integration tests
- API response handling logic

**Success Criteria:**
- RAG retrieves relevant historical data
- Research agent finds current information
- Results properly aggregated
- Performance: < 5s for research

---

#### Milestone 2.4: Detection Agents
**Owner:** ML/NLP Specialist  
**Tasks:**
- [ ] Implement Bias Detector Agent
- [ ] Implement Bot Detector Agent
- [ ] Implement Campaign Detector Agent
- [ ] Create scoring algorithms
- [ ] Build test suite

**Deliverables:**
- `src/agents/bias_detector.py` complete
- `src/agents/bot_detector.py` complete
- `src/agents/campaign_detector.py` complete
- Detection test cases
- Performance benchmarks

**Success Criteria:**
- Detects bias indicators accurately
- Bot detection identifies suspicious patterns
- Campaign detection finds coordinated accounts
- Scoring is reproducible

---

#### Milestone 2.5: Synthesis & Reviewer Agents
**Owner:** Senior Data Engineer  
**Tasks:**
- [ ] Implement Synthesis Agent
- [ ] Build report generation logic
- [ ] Create trust score calculation
- [ ] Implement Reviewer Agent
- [ ] Build reflection loop logic

**Deliverables:**
- `src/agents/synthesis_agent.py` complete
- `src/agents/reviewer_agent.py` complete
- `src/workflow/reflection_loop.py` complete
- `src/utils/scoring.py` complete
- Reflection loop tests

**Success Criteria:**
- Synthesis creates coherent reports
- Trust scores are calculated correctly
- Reviewer provides actionable feedback
- Reflection loop converges in ≤3 iterations

---

### **Phase 3: Integration & Orchestration (Week 3)**

#### Milestone 3.1: Workflow Orchestration
**Owner:** Rohan  
**Tasks:**
- [ ] Implement main orchestration logic
- [ ] Build task routing system
- [ ] Implement state management
- [ ] Create error handling
- [ ] Build retry logic

**Deliverables:**
- `src/workflow/orchestration.py` complete
- `src/workflow/state_manager.py` complete
- Error handling documentation
- State flow diagrams

**Success Criteria:**
- All agents execute in correct order
- State is properly managed
- Errors don't crash system
- Can retry failed tasks

---

#### Milestone 3.2: API Service
**Owner:** Frontend/Full-Stack Developer (or Rohan)  
**Tasks:**
- [ ] Build FastAPI application
- [ ] Create request/response models
- [ ] Implement endpoints
- [ ] Add request validation
- [ ] Create API documentation

**Deliverables:**
- `src/app.py` complete
- `src/models/request.py` and `response.py`
- OpenAPI/Swagger documentation
- API test suite

**Success Criteria:**
- API accepts valid requests
- Returns proper responses
- Validates input correctly
- Handles errors gracefully

---

#### Milestone 3.3: End-to-End Integration Testing
**Owner:** QA Lead (or Rohan)  
**Tasks:**
- [ ] Create integration test suite
- [ ] Test complete workflow
- [ ] Performance testing
- [ ] Load testing
- [ ] Stress testing

**Deliverables:**
- `tests/test_integration.py` complete
- Test report with results
- Performance benchmarks
- Identified bottlenecks

**Success Criteria:**
- Full workflow executes end-to-end
- Response times acceptable (< 30s)
- No data loss or corruption
- Handles edge cases

---

### **Phase 4: Demo & Deployment (Week 4)**

#### Milestone 4.1: Demo Application
**Owner:** Frontend/Full-Stack Developer  
**Tasks:**
- [ ] Create demo interface (CLI/Web)
- [ ] Prepare demo scenarios
- [ ] Create sample data
- [ ] Document demo flow
- [ ] Test demo end-to-end

**Deliverables:**
- Working demo application
- Demo dataset (Instagram pages/posts)
- Demo script/walkthrough
- Demo video (optional)

**Success Criteria:**
- Demo runs without errors
- Shows all agent capabilities
- Completes in < 2 minutes
- Results are clear and impressive

---

#### Milestone 4.2: Documentation
**Owner:** Rohan + All members  
**Tasks:**
- [ ] Write API documentation
- [ ] Write setup guide
- [ ] Write deployment guide
- [ ] Create architecture diagrams
- [ ] Write agent descriptions

**Deliverables:**
- `docs/API_REFERENCE.md`
- `docs/SETUP_GUIDE.md`
- `docs/DEPLOYMENT.md`
- Architecture diagrams
- Agent runbooks

**Success Criteria:**
- Anyone can set up from docs
- All APIs documented
- Deployment process clear
- Architecture understood

---

#### Milestone 4.3: Docker & Deployment
**Owner:** Frontend/Full-Stack Developer  
**Tasks:**
- [ ] Create Dockerfile
- [ ] Create docker-compose.yml
- [ ] Set up environment variables
- [ ] Test Docker build
- [ ] Deploy to staging/cloud

**Deliverables:**
- Dockerfile with all dependencies
- docker-compose.yml for full stack
- Deployment documentation
- Running instance (cloud or local)

**Success Criteria:**
- Docker builds successfully
- All services start correctly
- Can deploy new versions easily
- System runs in container

---

#### Milestone 4.4: Final Testing & QA
**Owner:** QA Lead  
**Tasks:**
- [ ] Final functionality testing
- [ ] Security testing
- [ ] Performance validation
- [ ] Documentation review
- [ ] Demo preparation

**Deliverables:**
- Final test report
- Security assessment
- Performance report
- Sign-off document

**Success Criteria:**
- All major features working
- No critical bugs
- Performance meets targets
- Ready for demonstration

---

## Part 6: Collaboration & Dependency Map

### Dependencies Between Workstreams

```
Week 1:
  Infrastructure Setup (Parallel)
  ├── Config & Logging
  ├── Vector DB Setup
  ├── API Setup
  └── Base Agent Architecture
  
Week 2-3:
  Agent Development (Parallel with dependencies)
  ├── RAG Pipeline (depends on: Vector DB)
  ├── Research Agent (depends on: API Setup)
  ├── Content Analysis (no dependencies)
  ├── Detection Agents (depends on: Content Analysis)
  ├── Synthesis Agent (depends on: All detection agents)
  └── Reviewer Agent (depends on: Synthesis Agent)
  
Week 3:
  Integration (Sequential)
  ├── Orchestration (depends on: All agents)
  ├── API Service (depends on: Orchestration)
  └── E2E Testing (depends on: API Service)
  
Week 4:
  Demo & Deployment (Sequential)
  ├── Demo App (depends on: API Service)
  ├── Documentation (depends on: All)
  ├── Docker & Deployment (depends on: All)
  └── Final Testing (depends on: All)
```

### Communication Protocol

**Daily Standups:** 15 min  
- Focus: Blockers and progress
- Time: 10 AM

**Weekly Sync:** 1 hour  
- Review: Milestone progress
- Discuss: Blockers and solutions
- Plan: Next week tasks

**Bi-weekly Demos:** 30 min  
- Showcase: Completed features
- Gather: Feedback
- Adjust: Plan if needed

---

## Part 7: Tools & Environment Setup

### Development Tools
```bash
# Version Control
git >= 2.40
GitHub/GitLab account with repo access

# Python
Python 3.10+
pip >= 23.0 or Poetry >= 1.5

# Database
Weaviate >= 1.0 (cloud or local)
Docker (for local Weaviate)

# APIs
Tavily API key
Instagram Graph API token
(Optional) Twitter API key
(Optional) Claude API key

# IDE
VS Code or PyCharm (recommended)
```

### Environment Setup Script

```bash
#!/bin/bash
# setup.sh

# Clone repo
git clone <repo-url>
cd NarrativeWatch-AI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy env file
cp .env.example .env
# Edit .env with your API keys

# Initialize database
python scripts/init_db.py

# Run tests
pytest tests/ -v

echo "Setup complete! Ready for development."
```

---

## Part 8: Success Criteria & Definition of Done

### Agent Development DoD

**For Each Agent:**
- [ ] Code written and documented
- [ ] Unit tests (min 80% coverage)
- [ ] Integration with orchestrator tested
- [ ] Input/output validation implemented
- [ ] Error handling implemented
- [ ] Performance benchmarked (< 5s avg)
- [ ] Code reviewed by peer
- [ ] Documented with examples

### System-Level DoD

- [ ] All agents implemented
- [ ] Reflection loop working (< 3 retries)
- [ ] Vector DB populated with initial data
- [ ] APIs integrated and rate-limited
- [ ] API service running
- [ ] End-to-end workflow tested
- [ ] Demo working flawlessly
- [ ] Documentation complete
- [ ] Docker deployment working
- [ ] All tests passing (90%+ coverage)

### Demo Success Criteria (FDE Requirements)

**Technical:**
- [ ] Agent Orchestration: All 9 agents working together (25 pts)
- [ ] RAG Implementation: Vector search + retrieval functional (15 pts)
- [ ] Tavily & API Usage: External data integration working (15 pts)
- [ ] Reviewer & Reflection Loop: Quality checks + regeneration (20 pts)
- [ ] Innovation: Multi-agent collaboration + reflection loop (15 pts)

**Demo Quality (10 pts):**
- [ ] Live demonstration runs without errors
- [ ] Shows all agent capabilities
- [ ] Clear trust score and reasoning
- [ ] Professional presentation
- [ ] Complete within time limit

---

## Part 9: Risk Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|-----------|
| API rate limits exceeded | Service outage | Medium | Implement caching and rate limit handling |
| Vector DB performance | Slow responses | Medium | Index optimization and query tuning |
| Agent hallucination | Wrong conclusions | High | Reviewer agent + reflection loop |
| Integration issues | Delays | High | Daily integration testing |
| Scope creep | Missed deadline | Medium | Strict requirement discipline |
| Team knowledge gaps | Quality issues | Medium | Documentation and pair programming |
| Data privacy concerns | Regulatory issues | Low | Use anonymized data and secure storage |

---

## Part 10: Additional Features (Bonus)

### Multi-Agent Collaboration
- [ ] Agents share context and learnings
- [ ] Dynamic agent selection based on query type
- [ ] Consensus mechanism for disagreements

### Human-in-the-Loop Approval
- [ ] Reviewer can request human validation
- [ ] Web interface for human approval
- [ ] Audit trail of decisions

### Memory Across Conversations
- [ ] Store analysis results in vector DB
- [ ] Learn from previous analyses
- [ ] Improve accuracy over time
- [ ] Conversation history management

### Advanced Planning & Task Decomposition
- [ ] Break complex queries into sub-tasks
- [ ] Dynamic workflow generation
- [ ] Parallel task execution with dependencies

---

## Appendix A: Key Technologies & Why They're Used

| Technology | Purpose | Alternative | Why Chosen |
|-----------|---------|-------------|-----------|
| LangChain | Agent orchestration | AutoGen, CrewAI | Industry standard, good docs |
| Claude (Anthropic) | LLM | GPT-4, Gemini | Superior reasoning, context window |
| Tavily | Web search | SerpAPI, Exa | Real-time data, reliable |
| Weaviate | Vector DB | Pinecone, Milvus | Open-source, flexible, scalable |
| FastAPI | API service | Flask, Django | High performance, async support |
| Docker | Containerization | VM, Kubernetes | Lightweight, portable, reproducible |

---

## Appendix B: Estimated Effort & Timeline

**Total Team Effort:** ~200-240 person-hours  
**Timeline:** 4 weeks (with 4-6 team members)

**Breakdown by Phase:**
- Phase 1 (Setup): 40 hours
- Phase 2 (Agents): 120 hours
- Phase 3 (Integration): 50 hours
- Phase 4 (Demo): 30-40 hours

**Optimal Team Size:** 5-6 people  
**Minimum Team Size:** 3 people (with scope reduction)

---

## Appendix C: Post-Launch Roadmap

**V1.1 (2 weeks post-launch):**
- [ ] Multi-language support
- [ ] Real-time notification alerts
- [ ] Advanced filtering options

**V1.2 (1 month post-launch):**
- [ ] Mobile app (iOS/Android)
- [ ] Advanced visualizations
- [ ] API rate limiting & authentication

**V2.0 (3 months post-launch):**
- [ ] Multi-platform support (TikTok, YouTube, Twitter)
- [ ] Machine learning model fine-tuning
- [ ] Advanced analytics dashboard
- [ ] Enterprise licensing

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-06-12 | Rohan | Initial LLD & Team Plan |


# NarrativeWatch AI - Implementation Checklist

**Quick Reference for Team Members**

---

## Phase 1: Setup & Infrastructure (Week 1)

### [ ] Repository & Environment
- [ ] Create Git repository
- [ ] Clone from remote
- [ ] Create directory structure (see LLD Part 3.2)
- [ ] Copy `.env.example` → `.env` and fill in API keys
- [ ] Create `requirements.txt`
- [ ] Create `setup.sh` script
- [ ] Test setup on all team member machines

**Owner:** Rohan  
**Deadline:** Monday EOD  
**Acceptance:** All team members can run `setup.sh` successfully

---

### [ ] Logging & Configuration
- [ ] Create `src/config.py` with all settings
- [ ] Create `src/logger.py` with logging setup
- [ ] Test logging across modules
- [ ] Create `logs/` directory with `.gitignore`

**Owner:** Rohan  
**Deadline:** Monday EOD  
**Acceptance:** All modules log correctly

---

### [ ] Database Setup (PostgreSQL + pgvector)
- [ ] Set up PostgreSQL instance (local or Docker)
  ```bash
  docker run -p 5432:5432 -e POSTGRES_PASSWORD=postgres pgvector/pgvector:latest
  ```
- [ ] Install pgvector extension in PostgreSQL
  ```sql
  CREATE EXTENSION vector;
  ```
- [ ] Create `src/database/postgres_client.py` (SQLAlchemy)
- [ ] Create `src/database/models.py` with ORM models
- [ ] Test connection and CRUD operations
- [ ] Create migration scripts

**Owner:** Backend Specialist  
**Deadline:** Tuesday EOD  
**Acceptance:** PostgreSQL running, pgvector enabled, tables created

---

### [ ] External APIs
- [ ] Register and get API keys for:
  - Tavily Search
  - Instagram Graph API
  - (Optional) Twitter API
- [ ] Create `src/apis/tavily_api.py` wrapper
- [ ] Create `src/apis/instagram_api.py` wrapper
- [ ] Test each API independently
- [ ] Create `src/apis/llm_client.py` for Vertex AI Gemini 2.5

**Owner:** Backend Specialist  
**Deadline:** Wednesday EOD  
**Acceptance:** All APIs responding correctly, rate limits documented

---

### [ ] Base Agent Architecture
- [ ] Create `src/agents/base_agent.py`
  ```python
  class BaseAgent:
      - __init__(name, description)
      - _define_tools()
      - _create_executor()
      - run(input_data)
  ```
- [ ] Test with simple example agent
- [ ] Document agent pattern
- [ ] Create template for new agents

**Owner:** Rohan  
**Deadline:** Friday EOD  
**Acceptance:** Can create and run simple agents with tools

---

## Phase 2: Agent Development (Week 2-3)

### [ ] RAG Pipeline with PostgreSQL + pgvector
- [ ] Create `src/utils/embedding_utils.py`
  - Use Vertex AI text-embedding-005 for embeddings
  - Test on sample texts
- [ ] Create `src/database/rag_pipeline.py`
  - PostgreSQL pgvector ingestion function
  - SQL similarity search queries
  - Cosine/L2 distance optimization
- [ ] Load sample Instagram posts into PostgreSQL
- [ ] Test pgvector similarity search (top-k results)
- [ ] Benchmark: query performance, accuracy

**Owner:** Backend Specialist  
**Deadline:** Tuesday (Week 2) EOD  
**Acceptance:** Embeddings in pgvector, similarity search returns relevant results

---

### [ ] Content Analyzer Agent
- [ ] Create `src/utils/text_processor.py`
  - Tokenization
  - Stopword removal
  - Stemming/lemmatization
  - NER (named entity recognition)
- [ ] Create `src/agents/content_analyzer.py`
  - Extract hashtags
  - Identify narrative themes
  - Classify emotional language
  - Extract engagement metrics
- [ ] Write unit tests (80%+ coverage)
- [ ] Test on sample posts

**Owner:** ML/NLP Specialist  
**Deadline:** Wednesday (Week 2) EOD  
**Acceptance:** Extracts all required features, tests pass

---

### [ ] RAG Agent
- [ ] Create `src/agents/rag_agent.py`
  - Query embedding (Vertex AI)
  - PostgreSQL pgvector similarity search
  - Result aggregation from database
  - Context building
- [ ] Integrate with PostgreSQL client
- [ ] Write integration tests (pgvector queries)
- [ ] Benchmark: should return results in < 1s (pgvector is fast!)

**Owner:** Backend Specialist  
**Deadline:** Thursday (Week 2) EOD  
**Acceptance:** Returns relevant historical data quickly

---

### [ ] Research Agent
- [ ] Create `src/agents/research_agent.py`
  - Tavily search queries
  - Instagram API queries
  - Result aggregation
  - Response formatting
- [ ] Implement rate limiting
- [ ] Handle API errors gracefully
- [ ] Write tests

**Owner:** Backend Specialist  
**Deadline:** Friday (Week 2) EOD  
**Acceptance:** Finds current information, aggregates results

---

### [ ] Bias Detector Agent
- [ ] Select bias detection model/approach
  - Option 1: Pre-trained HuggingFace model
  - Option 2: Custom classifier with training
- [ ] Create `src/agents/bias_detector.py`
  - Detect political bias
  - Detect gender bias
  - Detect ideological bias
  - Score calculation
- [ ] Write tests with diverse examples
- [ ] Validate accuracy

**Owner:** ML/NLP Specialist  
**Deadline:** Monday (Week 3) EOD  
**Acceptance:** Detects multiple bias types, scoring consistent

---

### [ ] Bot Detector Agent
- [ ] Research bot detection techniques
- [ ] Create `src/agents/bot_detector.py`
  - Comment pattern analysis
  - Engagement velocity analysis
  - Follower growth anomalies
  - Engagement timing analysis
- [ ] Write statistical analysis functions
- [ ] Test on sample accounts

**Owner:** ML/NLP Specialist  
**Deadline:** Tuesday (Week 3) EOD  
**Acceptance:** Identifies suspicious engagement patterns

---

### [ ] Campaign Detector Agent
- [ ] Create `src/agents/campaign_detector.py`
  - Graph construction (pages, hashtags)
  - Clustering algorithm (k-means or DBSCAN)
  - Similarity scoring
  - Coordination evidence extraction
- [ ] Implement cross-page analysis
- [ ] Write tests

**Owner:** Senior Data Engineer  
**Deadline:** Wednesday (Week 3) EOD  
**Acceptance:** Finds coordinated pages/hashtags, ranks by confidence

---

### [ ] Synthesis Agent
- [ ] Create `src/agents/synthesis_agent.py`
  - Aggregate all agent results
  - Generate narrative summary
  - Highlight key findings
  - Build evidence list
- [ ] Create `src/utils/scoring.py`
  - Trust score calculation (0-100)
  - Risk flag identification
  - Recommendation generation
- [ ] Test with sample results

**Owner:** Senior Data Engineer  
**Deadline:** Thursday (Week 3) EOD  
**Acceptance:** Creates coherent reports, trust scores calculated

---

### [ ] Reviewer Agent & Reflection Loop
- [ ] Create `src/agents/reviewer_agent.py`
  - Evaluate completeness
  - Check accuracy of evidence
  - Verify relevance
  - Assess clarity
- [ ] Create `src/workflow/reflection_loop.py`
  - Feedback generation
  - Retry logic (max 3)
  - Tracking history
  - Escalation handling
- [ ] Write tests

**Owner:** Senior Data Engineer  
**Deadline:** Friday (Week 3) EOD  
**Acceptance:** Provides actionable feedback, reflection loop converges

---

## Phase 3: Integration & Orchestration (Week 3)

### [ ] Workflow Orchestration
- [ ] Create `src/workflow/orchestration.py`
  - Main orchestration logic
  - Agent execution sequencing
  - Error handling
  - State passing between agents
- [ ] Create `src/workflow/state_manager.py`
  - Initialize state
  - Update state
  - Retrieve state
  - Clear state
- [ ] Test complete workflow manually
- [ ] Document state flow

**Owner:** Rohan  
**Deadline:** Wednesday (Week 3) EOD  
**Acceptance:** All agents execute in correct order, state properly managed

---

### [ ] FastAPI Service
- [ ] Create `src/app.py`
  - FastAPI app initialization
  - CORS setup
  - Error handling middleware
  - Logging middleware
- [ ] Create `src/models/request.py`
  - InstagramPageRequest
  - InstagramPostRequest
  - QueryRequest
- [ ] Create `src/models/response.py`
  - AnalysisResponse
  - TrustScoreResponse
  - ErrorResponse
- [ ] Create endpoints:
  - POST `/analyze/page` - Analyze Instagram page
  - POST `/analyze/post` - Analyze single post
  - GET `/status` - Health check
  - GET `/results/{id}` - Get cached results
- [ ] Add request validation
- [ ] Add Swagger documentation
- [ ] Write API tests

**Owner:** Frontend/Full-Stack Developer  
**Deadline:** Thursday (Week 3) EOD  
**Acceptance:** API endpoints working, docs complete

---

### [ ] End-to-End Integration Testing
- [ ] Create `tests/test_integration.py`
  - Test complete workflow
  - Test with real Instagram data
  - Test error scenarios
  - Test timeout handling
- [ ] Create `tests/test_agents.py`
  - Unit tests for each agent
  - Input validation tests
  - Output format tests
- [ ] Run full test suite
- [ ] Measure coverage (goal: 80%+)
- [ ] Document test results

**Owner:** QA Lead  
**Deadline:** Friday (Week 3) EOD  
**Acceptance:** All tests pass, coverage ≥ 80%

---

## Phase 4: Demo & Deployment (Week 4)

### [ ] Demo Application
- [ ] Create demo interface
  - Option 1: CLI tool using Click/Typer
  - Option 2: Simple web dashboard using Streamlit
- [ ] Create demo dataset
  - 5-10 sample Instagram pages
  - Mix of legitimate and suspicious pages
  - Various content types
- [ ] Create demo script
  - Step-by-step walkthrough
  - Example queries
  - Expected outputs
- [ ] Test demo end-to-end multiple times
- [ ] Create presentation slides

**Owner:** Frontend/Full-Stack Developer  
**Deadline:** Tuesday (Week 4) EOD  
**Acceptance:** Demo runs flawlessly, completes in < 2 min

---

### [ ] Documentation
- [ ] Create `docs/API_REFERENCE.md`
  - All endpoints
  - Request/response schemas
  - Example usage
  - Error codes
- [ ] Create `docs/SETUP_GUIDE.md`
  - Prerequisites
  - Step-by-step setup
  - Environment variables
  - Verification steps
- [ ] Create `docs/DEPLOYMENT.md`
  - Docker instructions
  - Cloud deployment options
  - Configuration for production
  - Monitoring setup
- [ ] Create architecture diagrams
  - Agent flow diagram
  - Data flow diagram
  - System architecture
- [ ] Create agent runbooks
  - Agent purpose
  - Inputs/outputs
  - Tools used
  - Error scenarios

**Owner:** Rohan + All members  
**Deadline:** Wednesday (Week 4) EOD  
**Acceptance:** Documentation complete and tested

---

### [ ] Docker & Deployment
- [ ] Create `Dockerfile`
  - Python 3.10+ base image
  - Copy code and requirements
  - Install dependencies
  - Expose port 8000
  - Health check
- [ ] Create `docker-compose.yml`
  - FastAPI service
  - Weaviate service
  - Network setup
  - Volume mounts
- [ ] Build and test Docker image
  - docker build -t narrativewatch-ai .
  - docker run -p 8000:8000 narrativewatch-ai
- [ ] Test docker-compose setup
- [ ] Deploy to staging environment (optional)

**Owner:** Frontend/Full-Stack Developer  
**Deadline:** Thursday (Week 4) EOD  
**Acceptance:** Docker builds, services start, app works in container

---

### [ ] Final Testing & QA
- [ ] Run complete test suite
- [ ] Verify all features working
- [ ] Performance testing
  - Single request: < 30s
  - Concurrent requests (10): < 5min total
- [ ] Error scenario testing
  - Invalid input
  - API failures
  - DB connection loss
- [ ] Security testing
  - SQL injection attempts
  - XSS attempts
  - API rate limiting
- [ ] Documentation review
- [ ] Create final test report

**Owner:** QA Lead  
**Deadline:** Friday (Week 4) EOD  
**Acceptance:** All tests pass, no critical issues, ready for demo

---

## Critical Path & Dependencies

```
Week 1:
├─ Setup & Config (Mon EOD)
├─ Vector DB (Tue EOD) ◄─ blocks RAG
├─ APIs Setup (Wed EOD) ◄─ blocks Research Agent
└─ Base Agents (Fri EOD) ◄─ blocks all agents

Week 2-3:
├─ RAG Pipeline (Tue W2 EOD)
├─ Content Analyzer (Wed W2 EOD)
├─ Research Agent (Fri W2 EOD)
├─ Detection Agents (Tue W3 EOD)
├─ Synthesis (Thu W3 EOD)
└─ Reviewer Agent (Fri W3 EOD)

Week 3:
├─ Orchestration (Wed W3 EOD) ◄─ blocks API
├─ API Service (Thu W3 EOD) ◄─ blocks demo
└─ Integration Tests (Fri W3 EOD)

Week 4:
├─ Demo App (Tue EOD)
├─ Documentation (Wed EOD)
├─ Docker (Thu EOD)
└─ Final Testing (Fri EOD)
```

---

## Definition of Done for Each Task

**Code Quality:**
- [ ] Code follows Python PEP 8
- [ ] Type hints included
- [ ] Docstrings for all functions
- [ ] No hardcoded values
- [ ] Proper error handling

**Testing:**
- [ ] Unit tests written (80%+ coverage)
- [ ] Integration tests pass
- [ ] Manual testing done
- [ ] Edge cases covered
- [ ] Performance acceptable

**Documentation:**
- [ ] Code commented (where WHY is non-obvious)
- [ ] Function docstrings complete
- [ ] Usage examples provided
- [ ] Assumptions documented
- [ ] Limitations noted

**Review:**
- [ ] Code reviewed by peer
- [ ] Feedback incorporated
- [ ] Changes tested after review
- [ ] Approved before merge

---

## Status Tracking Template

For each team member to update daily:

```markdown
## [Name] - Week [N] Status

### Completed This Week
- [ ] Task 1
- [ ] Task 2
- [ ] Task 3

### In Progress
- [ ] Task 4 (70% complete)
- [ ] Task 5 (20% complete)

### Blockers
- Issue: [Description]
  - Impact: [What's blocked]
  - Resolution: [Help needed]

### Next Week Plan
- [ ] Task X
- [ ] Task Y
```

---

## Emergency Contacts

**Project Lead (Rohan):** [Phone/Email]  
**Backend Lead:** [Phone/Email]  
**ML/NLP Lead:** [Phone/Email]  
**Data Engineer Lead:** [Phone/Email]  
**DevOps/Frontend Lead:** [Phone/Email]  

---

## Key Dates

- **Week 1 Checkpoint:** Friday 5pm (Infrastructure ready)
- **Week 2 Checkpoint:** Friday 5pm (50% agents done)
- **Week 3 Checkpoint:** Friday 5pm (Integration complete)
- **Demo Day:** Monday Week 5 (9am sharp)

---

## Notes

- All code pushed to `main` branch daily (or feature branches with daily PRs)
- Daily standup at 10am, async updates in Slack
- Weekly Friday sync at 4pm
- Use GitHub Issues for tracking blockers
- Use Pull Requests for code review
- Update this document as blockers/changes emerge


# Team Member 3: ML/NLP Specialist - Execution Plan
## NarrativeWatch AI - Detailed Implementation Guide

**Team Member:** You (ML/NLP Specialist)  
**Role:** Develop Content Analyzer, Bias Detector, and Bot Detector Agents  
**Timeline:** Week 2-3 (4-5 days of intensive development)  
**Current Branch:** `feature/ml-nlp-agents`  
**Target Merge:** Into `develop` (then to `main`)

---

## Part 1: Your Responsibilities & Deliverables

### High-Level Overview
You are responsible for implementing **3 core agents** that perform NLP and ML-based analysis:
1. **Content Analyzer Agent** - Extract and classify Instagram post/page content
2. **Bias Detector Agent** - Identify political, gender, and ideological bias
3. **Bot Detector Agent** - Detect suspicious engagement patterns and bot activity

### Deliverables Checklist
- [x] `src/agents/content_analyzer.py` - Complete implementation
- [x] `src/agents/bias_detector.py` - Complete implementation
- [x] `src/agents/bot_detector.py` - Complete implementation
- [x] `src/utils/text_processor.py` - Text processing utilities
- [x] `src/utils/embedding_utils.py` - Embedding utilities (may reuse/reference)
- [x] Unit tests for all agents (80%+ coverage)
- [x] ML model selection document
- [ ] Code review and approval from Rohan/Backend Specialist
- [ ] Merge to develop without conflicts

---

## Part 2: Dependency Tree & Prerequisites

### What You Need From Others (Blocking Dependencies)

#### **Critical Path (MUST be done before you start)**
1. ✅ **Base Agent Architecture** - Rohan should have completed `src/agents/base_agent.py`
   - Your agents will inherit from `BaseAgent` class
   - Defines pattern for tools and executors
   - Status: Should be ready by Friday Week 1

2. ✅ **Configuration & Logging** - Rohan should have setup `src/config.py` and `src/logger.py`
   - You'll use these for configuration and logging in your agents
   - Status: Should be ready by Monday Week 2

#### **Non-Blocking (You can work around if needed)**
- Backend Specialist's API wrappers (RAG Agent, Research Agent)
  - You can mock these if needed for testing
  - Not required for your agent development

### What Others Depend On From You

**Critical dependencies on your work:**
1. **Synthesis Agent** (Data Engineer) - Needs your agent outputs
   - Will receive: Content features, bias scores, bot detection flags
   - Timeline: Your agents must be done by Tuesday Week 3

2. **Orchestrator Agent** (Rohan) - Needs your agent implementations to call
   - Will coordinate execution of your agents
   - Timeline: Rohan starts integration Wednesday Week 3

---

## Part 3: Development Roadmap (Day-by-Day)

### Day 1: Setup & Architecture (Monday Week 2)

**Objectives:**
- Set up your development environment
- Review codebase and dependencies
- Design your agents' architecture
- Plan implementation sequence

**Tasks:**

1. **Pull latest from develop/main**
   ```bash
   cd c:/Users/l.venkat/Desktop/NarrativeWatch-AI/NarrativeWatch-AI
   git fetch origin
   git pull origin develop
   ```

2. **Verify your branch is up to date**
   ```bash
   git branch -a
   git status
   ```

3. **Create/update virtual environment**
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Review existing code**
   - Read `src/agents/base_agent.py` (if exists)
   - Read `src/config.py` (if exists)
   - Review the LLD Part 2.3 (Agent Implementation Pattern)

5. **Design document: Create `AGENT_DESIGN.md`**
   ```markdown
   # ML/NLP Agents Design Document
   
   ## Content Analyzer Agent
   - Input: Instagram caption, hashtags, posting_time
   - Output: {emotional_language, narrative_themes, hashtag_patterns, post_timing, engagement_metrics}
   - Libraries: NLTK, TextBlob, spaCy
   
   ## Bias Detector Agent
   - Input: Post content, language patterns
   - Output: {political_bias_score, gender_bias_score, ideology_score, toxicity_score}
   - Libraries: HuggingFace transformers, VADER sentiment
   
   ## Bot Detector Agent
   - Input: Comments, likes, follower_data, engagement_timing
   - Output: {bot_activity_score, comment_authenticity, engagement_velocity, follower_anomalies}
   - Libraries: scipy, numpy, sklearn
   ```

**Deliverable:** Design document + Environment ready

---

### Day 2: Text Processor & Utilities (Tuesday Week 2)

**Objectives:**
- Build reusable text processing utilities
- Set up embedding utilities infrastructure
- Create utility functions for all agents

**Tasks:**

1. **Create `src/utils/text_processor.py`**
   ```python
   class TextProcessor:
       - tokenize(text) -> List[str]
       - remove_stopwords(tokens) -> List[str]
       - lemmatize(tokens) -> List[str]
       - extract_named_entities(text) -> Dict
       - extract_hashtags(text) -> List[str]
       - extract_mentions(text) -> List[str]
       - calculate_sentiment(text) -> float
       - analyze_emotion(text) -> Dict[str, float]
   ```

2. **Create `src/utils/embedding_utils.py`**
   ```python
   class EmbeddingUtils:
       - generate_embedding(text) -> List[float]
       - batch_embedding(texts) -> List[List[float]]
       - cosine_similarity(vec1, vec2) -> float
   ```

3. **Install NLP dependencies**
   ```bash
   pip install nltk spacy textblob
   python -m spacy download en_core_web_sm
   python -m textblob.download_corpora
   ```

4. **Write unit tests for utilities**
   - `tests/test_text_processor.py`
   - Test each function with various inputs

**Deliverable:** Complete utility modules with tests (80%+ coverage)

---

### Day 3: Content Analyzer Agent (Wednesday Week 2)

**Objectives:**
- Implement full Content Analyzer Agent
- Extract all required content features
- Create comprehensive tests

**Tasks:**

1. **Create `src/agents/content_analyzer.py`**
   ```python
   class ContentAnalyzerAgent(BaseAgent):
       def __init__(self):
           super().__init__("Content Analyzer", "Extract and classify post/page content")
           self.text_processor = TextProcessor()
       
       def analyze_caption(self, caption: str) -> dict:
           # Emotional language, themes, sentiment
       
       def analyze_hashtags(self, hashtags: list) -> dict:
           # Hashtag patterns, frequency, trends
       
       def analyze_posting_pattern(self, posts: list) -> dict:
           # Timing, frequency, consistency
       
       def run(self, instagram_data: dict) -> dict:
           # Main orchestration of analysis
   ```

2. **Implement features extraction**
   - Emotional language classification (positive/negative/neutral)
   - Narrative theme identification (conspiracy, propaganda, etc.)
   - Hashtag pattern detection
   - Posting frequency and timing analysis
   - Engagement metric classification

3. **Write tests**
   - `tests/test_content_analyzer.py`
   - Test with sample Instagram posts
   - Mock Instagram data for testing

4. **Test on sample data**
   - Create test data in `tests/fixtures/sample_posts.json`
   - Verify output format matches spec

**Deliverable:** Content Analyzer Agent fully implemented + tested

---

### Day 4: Bias Detector Agent (Thursday Week 2)

**Objectives:**
- Implement Bias Detector Agent
- Detect multiple bias types
- Create scoring mechanisms

**Tasks:**

1. **Choose bias detection approach**
   - Option A: HuggingFace pre-trained models (recommended)
     - `distilbert-base-uncased-finetuned-sst-2-english` (sentiment)
     - `cardiffnlp/twitter-xlm-roberta-base` (political bias)
   - Option B: Custom rules + sentiment analysis (simpler but less accurate)

2. **Create `src/agents/bias_detector.py`**
   ```python
   class BiasDetectorAgent(BaseAgent):
       def __init__(self):
           super().__init__("Bias Detector", "Identify political, gender, and ideological bias")
           self.political_model = load_model("political-bias-classifier")
           self.gender_model = load_model("gender-bias-classifier")
       
       def detect_political_bias(self, text: str) -> Dict[str, float]:
           # Returns: {left_score, center_score, right_score, confidence}
       
       def detect_gender_bias(self, text: str) -> Dict[str, float]:
           # Returns: {male_bias, female_bias, neutral_score}
       
       def detect_ideological_bias(self, text: str) -> Dict[str, float]:
           # Returns: {progressive_score, conservative_score, neutral_score}
       
       def calculate_toxicity(self, text: str) -> float:
           # Returns: 0-1 toxicity score
       
       def run(self, content: str) -> dict:
           # Comprehensive bias analysis
   ```

3. **Implement bias scoring**
   - Weighted combination of different bias indicators
   - Confidence scores for each detection
   - Evidence extraction (which phrases indicate bias)

4. **Write tests**
   - `tests/test_bias_detector.py`
   - Test with politically charged text samples
   - Test with gender-biased content
   - Test edge cases (neutral content)

**Deliverable:** Bias Detector Agent fully implemented + tested

---

### Day 5: Bot Detector Agent (Friday Week 2)

**Objectives:**
- Implement Bot Detector Agent
- Create statistical analysis functions
- Complete Week 2 deliverables

**Tasks:**

1. **Create `src/agents/bot_detector.py`**
   ```python
   class BotDetectorAgent(BaseAgent):
       def __init__(self):
           super().__init__("Bot Detector", "Analyze engagement patterns for bot activity")
       
       def analyze_engagement_velocity(self, engagement_data: list) -> Dict:
           # Sudden spikes in likes/comments (bot-like behavior)
       
       def analyze_comment_patterns(self, comments: list) -> Dict:
           # Repeated phrases, timing patterns
       
       def analyze_follower_growth(self, follower_history: list) -> Dict:
           # Anomalies in growth rate
       
       def detect_coordinated_engagement(self, accounts: list) -> Dict:
           # Similar comments, same timing on different accounts
       
       def calculate_bot_score(self, all_indicators: dict) -> float:
           # 0-1 score indicating bot activity likelihood
       
       def run(self, engagement_data: dict) -> dict:
           # Main orchestration
   ```

2. **Implement statistical functions**
   - Velocity analysis (Z-score for outlier detection)
   - Pattern matching (string similarity for comments)
   - Timing analysis (inter-event time distribution)
   - Anomaly detection using isolation forest or statistical methods

3. **Write tests**
   - `tests/test_bot_detector.py`
   - Test with known bot patterns
   - Test with legitimate engagement data
   - Test edge cases (new accounts, viral posts)

4. **Integration test**
   - Create `tests/test_integration_ml_agents.py`
   - Test all three agents together
   - Verify output format compatibility

**Deliverable:** Bot Detector Agent + complete agent integration tests

---

### Days 6-7: Testing & Documentation (Week 2 Wrap-up)

**Objectives:**
- Achieve 80%+ test coverage
- Document your code
- Prepare for handoff to Data Engineer

**Tasks:**

1. **Comprehensive testing**
   ```bash
   pytest tests/ --cov=src/agents --cov=src/utils -v
   # Target: 80%+ coverage
   ```

2. **Code quality checks**
   ```bash
   black src/
   flake8 src/
   mypy src/ --ignore-missing-imports
   ```

3. **Documentation**
   - Add docstrings to all functions
   - Create `docs/AGENT_PATTERNS.md` with usage examples
   - Document model choices and why
   - Create ML model selection document

4. **Prepare outputs for next phases**
   - Create output schema documentation
   - Provide test fixtures for Data Engineer
   - Document any mocking/dependencies needed

**Deliverable:** Production-ready agents with full documentation

---

## Part 4: Preventing Merge Conflicts

### Strategy 1: Isolated Feature Branch

**Current state:**
```
main
  └── develop
       ├── feature/orchestrator-agent (Rohan)
       ├── feature/backend-rag-apis (Backend Specialist)
       ├── feature/data-eng-agents (Data Engineer)
       ├── feature/frontend-api-deployment (Frontend Dev)
       └── feature/ml-nlp-agents (YOU) ← You are here
```

**What you need to do:**

1. **Stay on your branch `feature/ml-nlp-agents`**
   ```bash
   git checkout feature/ml-nlp-agents
   git pull origin feature/ml-nlp-agents
   ```

2. **Only commit to your own files**
   ```
   src/agents/content_analyzer.py      ← Only you touch
   src/agents/bias_detector.py         ← Only you touch
   src/agents/bot_detector.py          ← Only you touch
   src/utils/text_processor.py         ← Only you touch
   src/utils/embedding_utils.py        ← Only you touch
   tests/test_content_analyzer.py      ← Only you touch
   tests/test_bias_detector.py         ← Only you touch
   tests/test_bot_detector.py          ← Only you touch
   ```

3. **AVOID touching these files** (other teams work here):
   ```
   src/agents/orchestrator.py          ← Rohan
   src/agents/rag_agent.py             ← Backend Specialist
   src/agents/research_agent.py        ← Backend Specialist
   src/agents/synthesis_agent.py       ← Data Engineer
   src/agents/reviewer_agent.py        ← Data Engineer
   src/agents/campaign_detector.py     ← Data Engineer
   src/workflow/                       ← Rohan
   src/apis/                           ← Backend Specialist
   src/database/                       ← Backend Specialist
   ```

### Strategy 2: File Ownership

**Your safe zone (no conflicts expected):**
```
src/
├── agents/
│   ├── content_analyzer.py       ✅ YOURS
│   ├── bias_detector.py          ✅ YOURS
│   └── bot_detector.py           ✅ YOURS
└── utils/
    ├── text_processor.py         ✅ YOURS
    └── embedding_utils.py        ✅ YOURS
```

**Shared but organized files:**
- `src/agents/__init__.py` - Add your agents to imports
- `src/utils/__init__.py` - Add your utilities to imports
- `tests/__init__.py` - Keep empty
- `requirements.txt` - Only add ML/NLP specific packages

### Strategy 3: Git Workflow to Avoid Conflicts

#### Daily commit pattern:
```bash
# Morning - pull latest develop to stay in sync
git fetch origin
git rebase origin/develop  # Get latest changes from other teams

# Work on your code
git add src/agents/content_analyzer.py
git commit -m "feat: implement content analyzer agent"

# End of day - push to your feature branch
git push origin feature/ml-nlp-agents
```

#### When merging to develop (end of Week 3):
```bash
# Pull latest develop
git fetch origin develop
git rebase origin/develop

# If conflicts (unlikely if you followed strategy):
git rebase --continue
# OR manually fix conflicts in your files only

# Force push to your feature branch
git push origin feature/ml-nlp-agents --force-with-lease

# Create PR for code review
# Let Rohan approve and merge via GitHub
```

### Strategy 4: Communication Protocol

**To avoid conflicts, sync daily:**
1. Check your team's agents' status
2. If using `BaseAgent`, ask Rohan if it's finalized
3. If your utilities are used elsewhere, coordinate with Backend Specialist

**Daily standup questions:**
- "Is `BaseAgent` finalized?" → Rohan
- "Are you using my utilities?" → Backend Specialist, Data Engineer
- "What output format do you expect?" → Data Engineer (Synthesis Agent)

---

## Part 5: Testing Strategy

### Unit Testing (Your responsibility)

**Content Analyzer Tests:**
```python
def test_extract_emotional_language():
    # Test happy, sad, neutral texts
    
def test_extract_hashtags():
    # Test with/without hashtags
    
def test_analyze_posting_pattern():
    # Test regular, irregular, viral patterns
```

**Bias Detector Tests:**
```python
def test_political_bias_detection():
    # Test left, right, center political text
    
def test_toxicity_detection():
    # Test toxic vs non-toxic content
    
def test_confidence_scores():
    # Verify scores are 0-1 and valid
```

**Bot Detector Tests:**
```python
def test_velocity_analysis():
    # Test sudden spikes
    
def test_comment_authenticity():
    # Test repeated vs varied comments
    
def test_bot_score_calculation():
    # Verify output is 0-1 score
```

### Integration Testing (with other agents)

**Mock data for integration:**
```python
# Create fixtures in tests/fixtures/
sample_content = {
    "caption": "...",
    "hashtags": ["#trending"],
    "comments": [...],
    "engagement": {...}
}

# Test your agent produces correct output
output = content_analyzer.run(sample_content)
assert output["emotional_language"] in ["positive", "negative", "neutral"]
```

---

## Part 6: Code Quality Standards

### Required for all code:

1. **Type hints**
   ```python
   def analyze_text(self, text: str) -> Dict[str, float]:
       pass
   ```

2. **Docstrings (one-liner for obvious functions)**
   ```python
   def tokenize(self, text: str) -> List[str]:
       """Tokenize text using NLTK."""
       pass
   ```

3. **Error handling**
   ```python
   try:
       result = self.model.predict(text)
   except Exception as e:
       logger.error(f"Prediction failed: {e}")
       return {"error": str(e), "status": "failed"}
   ```

4. **No hardcoded values**
   - Use `src/config.py` for all constants
   - Use environment variables for sensitive data

5. **Follow PEP 8**
   ```bash
   black src/agents/ src/utils/
   ```

---

## Part 7: Output Format Specification

### Content Analyzer Output
```json
{
    "status": "success",
    "analysis": {
        "emotional_language": {
            "positive_score": 0.7,
            "negative_score": 0.2,
            "neutral_score": 0.1
        },
        "narrative_themes": ["conspiracy", "propaganda"],
        "hashtag_patterns": {
            "#trending": 5,
            "#politics": 3
        },
        "posting_pattern": {
            "frequency": "daily",
            "consistency": 0.8,
            "timing_pattern": "morning_peaks"
        },
        "engagement_metrics": {
            "avg_likes": 1000,
            "avg_comments": 50,
            "engagement_rate": 0.05
        }
    }
}
```

### Bias Detector Output
```json
{
    "status": "success",
    "analysis": {
        "political_bias": {
            "left_score": 0.2,
            "center_score": 0.3,
            "right_score": 0.5,
            "confidence": 0.85
        },
        "gender_bias": {
            "male_bias": 0.1,
            "female_bias": 0.8,
            "neutral": 0.1
        },
        "ideological_bias": {
            "progressive": 0.3,
            "conservative": 0.6,
            "neutral": 0.1
        },
        "toxicity_score": 0.2
    }
}
```

### Bot Detector Output
```json
{
    "status": "success",
    "analysis": {
        "bot_activity_score": 0.75,
        "engagement_velocity": {
            "anomaly_detected": true,
            "z_score": 3.2
        },
        "comment_authenticity": {
            "repetition_percentage": 0.6,
            "suspicion_level": "high"
        },
        "follower_anomalies": {
            "growth_anomaly": true,
            "avg_daily_growth": 100
        }
    }
}
```

---

## Part 8: Risk Mitigation & Troubleshooting

### Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Import errors for nltk/spacy | Not installed | `pip install nltk spacy` + download models |
| BaseAgent not found | Rohan hasn't committed | Create mock base agent temporarily |
| Slow embedding generation | Model loading overhead | Lazy-load models, cache embeddings |
| Conflicting requirements.txt | Different package versions | Coordinate with Backend Specialist on versions |
| Test failures on different machine | Python version mismatch | Use Python 3.10+ consistently |

### Performance Targets

- **Content Analyzer**: < 2 seconds per post
- **Bias Detector**: < 3 seconds per post
- **Bot Detector**: < 5 seconds (requires engagement data)

---

## Part 9: Checklist for Successful Completion

### Code Implementation
- [ ] `src/agents/content_analyzer.py` - Complete and tested
- [ ] `src/agents/bias_detector.py` - Complete and tested
- [ ] `src/agents/bot_detector.py` - Complete and tested
- [ ] `src/utils/text_processor.py` - Complete with 80%+ coverage
- [ ] `src/utils/embedding_utils.py` - Complete with proper integration
- [ ] All agents inherit from `BaseAgent` properly
- [ ] All agents follow output schema specification

### Testing
- [ ] Unit test coverage: 80%+
- [ ] Integration tests pass
- [ ] Performance targets met
- [ ] Edge cases covered
- [ ] Error handling tested

### Documentation
- [ ] All functions have docstrings
- [ ] Code comments for non-obvious logic
- [ ] Usage examples provided
- [ ] ML model selection documented
- [ ] Output schemas documented

### Git & Collaboration
- [ ] Only touched assigned files
- [ ] No conflicts with other branches
- [ ] Daily commits with clear messages
- [ ] Ready for code review
- [ ] No hardcoded values

### Code Quality
- [ ] Passed `black` formatting
- [ ] Passed `flake8` linting
- [ ] Type hints included
- [ ] No unused imports
- [ ] Proper error handling

---

## Part 10: Success Criteria & Sign-Off

You're done when:

✅ **Functionality:**
- All three agents fully implemented
- Output formats match specification
- Performance targets met
- Tests pass with 80%+ coverage

✅ **Code Quality:**
- Type hints present
- Proper error handling
- No hardcoded values
- Follows PEP 8

✅ **Integration Ready:**
- Can be called by Synthesis Agent (Data Engineer)
- Can be orchestrated by Orchestrator Agent (Rohan)
- Output matches what downstream agents expect

✅ **Collaboration:**
- No merge conflicts
- Code reviewed and approved
- Ready to merge to develop
- Documentation complete

---

## Next Steps

1. **Now:** Review this document, confirm you understand all deliverables
2. **Tomorrow (Mon Week 2):** Start Day 1 tasks (Setup & Architecture)
3. **Daily:** Update status in team sync/Slack
4. **Friday Week 2:** All agents done and tested
5. **Week 3:** Ready for integration with orchestrator

**Questions?** Reach out to:
- Rohan (Project Lead) - Architecture/integration questions
- Backend Specialist - Dependency/API questions
- Data Engineer - Output format/downstream usage questions

Good luck! You've got this! 🚀

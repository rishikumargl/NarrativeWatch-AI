# Team Member 4 - Implementation Plan
## Senior Data/Analytics Engineer - Campaign Detection, Synthesis, & Quality Assurance

**Prepared for:** Shreya Adepu  
**Date:** 2026-06-12  
**Role:** Senior Data Engineer (Team Member 4)  
**Timeline:** Week 2-4  
**Branch:** `feature/data-eng-agents` (use this exclusively to avoid merge conflicts)

---

## ✅ YOUR RESPONSIBILITIES

### 1. **Campaign Detector Agent** (Week 3)
- Graph analysis of cross-page coordinated activity
- Clustering algorithms for campaign grouping
- Engagement timing correlation
- Narrative similarity scoring

### 2. **Synthesis Agent** (Week 3)
- Combine findings from all 7 agents
- Generate coherent final report
- Highlight key evidence
- Build recommendation

### 3. **Reviewer Agent + Reflection Loop** (Week 3-4)
- Quality assurance agent implementation
- Feedback generation logic
- Auto-regeneration with feedback (max 3 retries)
- Escalation handling

### 4. **Trust Score Algorithm** (Week 3)
- Evidence-based scoring (0-100)
- Risk flag calculation
- Confidence weighting

---

## 🛑 HOW TO AVOID MERGE CONFLICTS

### **Your Safe Zone (NO CONFLICTS)**
```
✅ src/agents/campaign_detector.py (YOU ONLY)
✅ src/agents/synthesis_agent.py (YOU ONLY)
✅ src/agents/reviewer_agent.py (YOU ONLY)
✅ src/workflow/reflection_loop.py (YOU ONLY)
✅ src/utils/scoring.py (YOU ONLY)
✅ tests/test_campaigns.py (YOU ONLY)
✅ tests/test_synthesis.py (YOU ONLY)
✅ tests/test_reviewer.py (YOU ONLY)
```

### **SHARED FILES - COORDINATE CAREFULLY**
```
⚠️  src/agents/__init__.py
    → Only add your agent imports at the END
    → Format: from .reviewer_agent import ReviewerAgent
    
⚠️  src/workflow/orchestration.py
    → Rohan (Team Member 1) is implementing this
    → YOU should NOT modify this
    → Your agents will be imported INTO this file
    
⚠️  tests/test_integration.py
    → Work with QA lead
    → Add your specific tests in isolation
    → Use separate test functions
```

### **GOLDEN RULES**
1. **Work ONLY on your branch:** `feature/data-eng-agents`
2. **Never modify orchestration.py** - Rohan owns this
3. **Never touch base_agent.py** - Rohan owns this
4. **Always add to imports, never replace**
5. **Commit daily** to avoid massive merge conflicts
6. **Use clear commit messages** with your task reference

---

## 📋 PHASE TIMELINE

### **PHASE 1: Dependency Waiting (Week 1-2)**
- ✅ Base Agent (Rohan finishes Fri Week 1)
- ✅ RAG Pipeline (Backend finishes Tue Week 2)
- ✅ All detection agents (ML/NLP finishes Mon Week 3)

**Your work:** Start Week 2 - Review agent architecture, plan campaign detection logic

---

### **PHASE 2: YOUR IMPLEMENTATION (Week 2-3)**

#### **Week 2: Foundation & Research**
```
Monday-Tuesday:
  └─ Read BaseAgent pattern & understand LangChain setup
  └─ Create src/agents/campaign_detector.py skeleton
  └─ Research graph clustering algorithms
  └─ Plan campaign detection data structures
  
Wednesday-Friday:
  └─ Implement campaign_detector.py basic structure
  └─ Write 5+ unit tests
  └─ Test with sample data
```

#### **Week 3: Implementation Sprint**
```
Monday-Wednesday:
  └─ Complete Campaign Detector Agent
  └─ Implement Synthesis Agent
  └─ Start Reviewer Agent
  
Thursday-Friday:
  └─ Complete Reviewer Agent
  └─ Finish Reflection Loop
  └─ Write integration tests
```

#### **Week 4: Integration & Polishing**
```
Monday-Wednesday:
  └─ Integration testing with Rohan
  └─ Final bug fixes
  └─ Performance optimization
  
Thursday-Friday:
  └─ Documentation
  └─ Code review feedback
  └─ Demo preparation
```

---

## 📝 DETAILED DELIVERABLES

### **Deliverable 1: Campaign Detector Agent**
**File:** `src/agents/campaign_detector.py`

```python
# DELIVERABLE CHECKLIST:
class CampaignDetectorAgent(BaseAgent):
    """
    Detects coordinated influence campaigns across multiple pages.
    
    Input:
      - pages: List[Dict] - Page data with engagement metrics
      - posts: List[Dict] - Post data with timestamps & hashtags
      - query_context: str - Original user query context
    
    Output:
      - campaigns: List[Campaign] - Grouped coordinated pages
      - confidence_scores: List[float] - 0-100 confidence per campaign
      - evidence: Dict - Supporting evidence & analysis
      - relationships: List[Tuple] - Page-to-page connections
    """
    
    # Core Methods:
    # ✅ __init__(self, name="Campaign Detector", description="...")
    # ✅ _define_tools(self) -> List[Tool]
    # ✅ run(self, input_data: dict) -> dict
    
    # Campaign Detection Methods:
    # ✅ detect_campaigns(self, pages: List[dict]) -> List[Campaign]
    # ✅ build_page_graph(self, pages: List[dict]) -> networkx.Graph
    # ✅ cluster_pages(self, graph) -> List[Set[str]]
    # ✅ calculate_campaign_confidence(self, cluster) -> float
    # ✅ extract_evidence(self, cluster) -> Dict
    
    # Analysis Methods:
    # ✅ analyze_hashtag_overlap(self, pages) -> Dict
    # ✅ analyze_timing_correlation(self, posts) -> Dict
    # ✅ analyze_narrative_similarity(self, posts) -> Dict
    # ✅ analyze_engagement_patterns(self, pages) -> Dict
```

**Dependencies:**
- networkx (graph analysis)
- scikit-learn (clustering)
- BaseAgent (from Rohan)

**Tests:**
```python
# src/tests/test_campaigns.py
def test_campaign_detection_basic():
    """Test clustering 3 coordinated pages"""
    
def test_campaign_detection_unrelated():
    """Test that unrelated pages aren't clustered"""
    
def test_hashtag_overlap_calculation():
    """Verify hashtag similarity scoring"""
    
def test_timing_correlation():
    """Test engagement timing analysis"""
    
def test_narrative_similarity():
    """Test narrative theme correlation"""
    
def test_confidence_scoring():
    """Verify confidence score 0-100 range"""
```

**Success Criteria:**
- Detects coordinated pages with 80%+ accuracy
- Handles 10+ pages efficiently (< 2s)
- Provides actionable evidence
- Clear separation of campaign clusters

---

### **Deliverable 2: Synthesis Agent**
**File:** `src/agents/synthesis_agent.py`

```python
class SynthesisAgent(BaseAgent):
    """
    Synthesizes findings from all 7 agents into final report.
    
    Input:
      - agent_results: Dict - Results from all agents:
          {
            'content': {...},
            'rag': [...],
            'research': {...},
            'bias': {...},
            'bot': {...},
            'campaigns': {...},
            'original_query': str
          }
    
    Output:
      - report: str - Coherent narrative summary
      - key_findings: List[str] - Top 5-10 findings
      - evidence_list: List[Evidence] - Ranked evidence items
      - trust_score_components: Dict - Breakdown of score
      - recommendation: str - Next steps/action items
    """
    
    # Core Methods:
    # ✅ __init__(self, ...)
    # ✅ run(self, agent_results: dict) -> dict
    
    # Report Generation:
    # ✅ synthesize_findings(self, agent_results) -> str
    # ✅ extract_key_findings(self, agent_results) -> List[str]
    # ✅ build_evidence_list(self, agent_results) -> List[Evidence]
    # ✅ rank_evidence(self, evidence) -> List[Evidence]
    # ✅ generate_recommendation(self, findings, trust_score) -> str
    
    # Report Quality:
    # ✅ validate_report(self, report) -> bool
    # ✅ ensure_coherence(self, report) -> bool
    # ✅ check_completeness(self, report, agent_results) -> bool
```

**Tests:**
```python
# src/tests/test_synthesis.py
def test_synthesis_basic():
    """Synthesize results from all 7 agents"""
    
def test_key_findings_extraction():
    """Verify 5-10 key findings are extracted"""
    
def test_evidence_ranking():
    """Test evidence is ranked by relevance"""
    
def test_report_coherence():
    """Ensure synthesized report flows logically"""
    
def test_empty_results_handling():
    """Handle agents that return no findings"""
```

**Success Criteria:**
- Synthesizes all agent outputs coherently
- Extracts 5-10 key findings
- Provides actionable evidence list
- Generates professional-quality report
- Report length: 500-2000 words

---

### **Deliverable 3: Reviewer Agent + Reflection Loop**
**File 1:** `src/agents/reviewer_agent.py`

```python
class ReviewerAgent(BaseAgent):
    """
    Quality assurance agent that reviews synthesis output.
    
    Input:
      - synthesis_result: Dict - Output from Synthesis Agent
      - agent_results: Dict - Original agent results for context
      - max_iterations: int - Max review feedback iterations
    
    Output:
      - status: str - "APPROVED" or "NEEDS_REVISION"
      - feedback: str - Specific feedback for improvement
      - issues: List[str] - List of identified issues
      - confidence: float - Confidence in assessment (0-1)
    """
    
    # Evaluation Methods:
    # ✅ evaluate_synthesis(self, synthesis_result) -> Dict
    # ✅ check_completeness(self, result, agent_results) -> bool
    # ✅ check_accuracy(self, result, agent_results) -> bool
    # ✅ check_relevance(self, result, query) -> bool
    # ✅ check_clarity(self, result) -> bool
    # ✅ generate_feedback(self, issues) -> str
```

**File 2:** `src/workflow/reflection_loop.py`

```python
class ReflectionLoop:
    """
    Implements feedback loop for synthesis improvement.
    
    Flow:
    1. Synthesis Agent generates initial report
    2. Reviewer Agent evaluates report
    3. If APPROVED: Return result
    4. If REJECTED: Synthesis Agent regenerates with feedback
    5. Repeat max 3 times
    """
    
    # Core Methods:
    # ✅ __init__(self, synthesis_agent, reviewer_agent, max_retries=3)
    # ✅ execute_with_review(self, agent_results) -> Dict
    # ✅ run_retry_loop(self, synthesis_result, feedback) -> Dict
    # ✅ track_feedback_history(self, feedback) -> None
    # ✅ escalate_on_failure(self, feedback_history) -> Dict
```

**Tests:**
```python
# src/tests/test_reviewer.py
def test_reviewer_approves_good_synthesis():
    """Reviewer approves complete, accurate synthesis"""
    
def test_reviewer_rejects_incomplete():
    """Reviewer rejects synthesis missing key elements"""
    
def test_reflection_loop_convergence():
    """Reflection loop converges in ≤3 iterations"""
    
def test_feedback_generation():
    """Feedback is specific and actionable"""
    
def test_escalation_on_max_retries():
    """Escalates after 3 failed attempts"""
```

**Success Criteria:**
- Reviewer identifies real quality issues
- Reflection loop converges in ≤3 iterations
- Feedback is actionable and specific
- Max retries prevent infinite loops
- Escalation handling is graceful

---

### **Deliverable 4: Trust Score Algorithm**
**File:** `src/utils/scoring.py`

```python
class TrustScoreCalculator:
    """
    Calculates evidence-based trust score (0-100).
    
    Score Components:
    - Authenticity (30%): Bot activity, fake engagement
    - Truthfulness (25%): Fact-check results, source credibility
    - Bias (20%): Political/gender/ideological bias level
    - Manipulation (15%): Emotional manipulation tactics
    - Campaign Activity (10%): Coordinated influence presence
    
    Output:
    - trust_score: int (0-100)
    - risk_level: str ("critical" | "high" | "medium" | "low")
    - component_scores: Dict - Breakdown
    - confidence: float - (0-1) Confidence in score
    """
    
    # Main Methods:
    # ✅ calculate_trust_score(self, agent_results) -> int
    # ✅ calculate_component_scores(self, agent_results) -> Dict
    # ✅ weigh_components(self, components) -> Dict
    # ✅ determine_risk_level(self, score) -> str
    # ✅ calculate_confidence(self, agent_results) -> float
    # ✅ generate_score_reasoning(self, breakdown) -> str
```

**Algorithm Example:**
```python
# Pseudocode for scoring logic:
trust_score = (
    authenticity_score * 0.30 +      # 0-100
    truthfulness_score * 0.25 +      # 0-100
    (100 - bias_score) * 0.20 +      # Inverse: high bias = low trust
    (100 - manipulation_score) * 0.15 +
    (100 - campaign_score) * 0.10
)
# Result: 0-100, where higher = more trustworthy
```

**Tests:**
```python
# src/tests/test_scoring.py
def test_perfect_content_scores_high():
    """Authentic, truthful, unbiased → 80-100"""
    
def test_bot_activity_lowers_score():
    """High bot activity → 20-40"""
    
def test_component_weighting():
    """Verify 30/25/20/15/10 weighting applied"""
    
def test_risk_level_assignment():
    """Score 0-20: critical, 21-40: high, etc."""
    
def test_confidence_calculation():
    """More evidence = higher confidence"""
```

**Success Criteria:**
- Score ranges 0-100
- Reflects actual content trustworthiness
- Component breakdown is understandable
- Risk levels match score ranges
- Confidence increases with evidence

---

## 🔗 INTEGRATION POINTS

### **How Your Work Connects**

```
Week 2-3: Detection Agents Done ← From ML/NLP Specialist
                   ↓
        Your Campaign Detector reads results
                   ↓
        Synthesis Agent aggregates all findings
                   ↓
        Reviewer Agent quality checks
                   ↓
        Reflection Loop auto-improves
                   ↓
Week 3: Rohan's Orchestrator calls all your agents
                   ↓
Week 4: Demo shows everything working together
```

### **Dependency Requirements**
- **BaseAgent** (Rohan) - Week 1 Friday
  - You inherit from this for all 3 agents
  
- **Content Analyzer, RAG, Research, Bias, Bot, Campaign Agents** (ML/NLP + Backend)
  - You consume results from all 6 agents
  - Format: Dict with standardized keys
  
- **Trust Score Utility** (You own this)
  - Used by Synthesis Agent internally
  - No other teams depend on it

### **Who Depends on You**
- **Rohan (Orchestrator)** - Needs your agents callable
- **Frontend/API team** - Needs final output format
- **QA team** - Needs comprehensive test suite

---

## 🚀 WEEK-BY-WEEK EXECUTION

### **WEEK 2**

**Monday (6/17):**
- [ ] Read `LLD_AND_TEAM_PLAN.md` Part 1-2 (focus on agent definitions)
- [ ] Study `BaseAgent` pattern (when Rohan finishes)
- [ ] Create branch: `git checkout -b feature/data-eng-agents`
- [ ] Create skeleton files:
  - `src/agents/campaign_detector.py`
  - `src/agents/synthesis_agent.py`
  - `src/agents/reviewer_agent.py`
  - `src/workflow/reflection_loop.py`
  - `src/utils/scoring.py`
  - `tests/test_campaigns.py`
  - `tests/test_synthesis.py`
  - `tests/test_reviewer.py`
  - `tests/test_scoring.py`

**Tuesday-Wednesday (6/18-6/19):**
- [ ] Read RAG Pipeline implementation (Backend)
- [ ] Research graph clustering algorithms
  - networkx for graph construction
  - scikit-learn for clustering
  - cosine similarity for narrative matching
- [ ] Design Campaign Detector data structures
- [ ] Write test cases for Campaign Detector

**Thursday-Friday (6/20-6/21):**
- [ ] Implement Campaign Detector skeleton with stubs
- [ ] Implement 3-5 test cases
- [ ] Test with sample data
- [ ] Daily commits with progress
- [ ] Code review with team (if available)

**End of Week 2:**
- Push to `feature/data-eng-agents` branch
- Share progress update in standup
- Identify any blockers

---

### **WEEK 3**

**Monday (6/24):**
- [ ] Verify all detection agents are complete
- [ ] Review their output formats
- [ ] Finalize Campaign Detector Agent implementation
- [ ] Write comprehensive unit tests (80%+ coverage)

**Tuesday (6/25):**
- [ ] Implement Synthesis Agent
- [ ] Build report generation logic
- [ ] Extract key findings algorithm
- [ ] Write unit tests

**Wednesday (6/26):**
- [ ] Implement Reviewer Agent
- [ ] Implement Reflection Loop
- [ ] Write unit tests for both
- [ ] Test loop convergence (≤3 iterations)

**Thursday (6/27):**
- [ ] Implement Trust Score Calculator
- [ ] Write scoring tests
- [ ] Verify all component agents produce expected output
- [ ] Integration testing with all agents

**Friday (6/28):**
- [ ] Final code review
- [ ] Bug fixes
- [ ] Performance optimization
- [ ] Prepare for Week 3 checkpoint

**End of Week 3:**
- All 5 deliverables COMPLETE
- 80%+ test coverage
- Ready for Rohan's orchestration integration

---

### **WEEK 4**

**Monday (7/1):**
- [ ] Integration testing with Rohan's orchestration
- [ ] Fix any orchestration integration issues
- [ ] End-to-end workflow testing

**Tuesday-Wednesday (7/2-7/3):**
- [ ] Demo preparation
- [ ] Create sample test data
- [ ] Document your agents
- [ ] Prepare runbooks

**Thursday-Friday (7/4-7/5):**
- [ ] Final code review feedback
- [ ] Performance benchmarking
- [ ] Demo dry-run
- [ ] Production readiness

---

## 🧪 TESTING STRATEGY

### **Test Coverage Target: 80%+**

```
Campaign Detector Agent:
  ├─ Clustering accuracy: 10 test cases
  ├─ Hashtag overlap: 5 test cases
  ├─ Timing correlation: 5 test cases
  ├─ Narrative similarity: 5 test cases
  ├─ Edge cases: 5 test cases
  └─ Total: ~30 tests

Synthesis Agent:
  ├─ Report generation: 5 test cases
  ├─ Key findings extraction: 5 test cases
  ├─ Evidence ranking: 5 test cases
  ├─ Empty results handling: 3 test cases
  └─ Total: ~18 tests

Reviewer Agent:
  ├─ Quality evaluation: 5 test cases
  ├─ Feedback generation: 5 test cases
  ├─ Issue detection: 5 test cases
  └─ Total: ~15 tests

Reflection Loop:
  ├─ Loop convergence: 5 test cases
  ├─ Retry logic: 5 test cases
  ├─ Escalation handling: 3 test cases
  └─ Total: ~13 tests

Scoring:
  ├─ Component scoring: 5 test cases
  ├─ Risk level assignment: 4 test cases
  ├─ Confidence calculation: 3 test cases
  └─ Total: ~12 tests

TOTAL TESTS: ~88 test cases
```

### **Running Tests**
```bash
# Run all your tests
pytest tests/test_campaigns.py tests/test_synthesis.py tests/test_reviewer.py tests/test_scoring.py -v

# With coverage
pytest tests/ --cov=src.agents.campaign_detector --cov=src.agents.synthesis_agent --cov=src.agents.reviewer_agent --cov=src.workflow.reflection_loop --cov=src.utils.scoring -v
```

---

## 📦 FILE STRUCTURE YOU'LL CREATE

```
NarrativeWatch-AI/
├── src/
│   ├── agents/
│   │   ├── campaign_detector.py       ← YOU (Week 3)
│   │   ├── synthesis_agent.py         ← YOU (Week 3)
│   │   └── reviewer_agent.py          ← YOU (Week 3)
│   │
│   ├── workflow/
│   │   └── reflection_loop.py         ← YOU (Week 3)
│   │
│   ├── utils/
│   │   └── scoring.py                 ← YOU (Week 3)
│   │
│   └── models/
│       └── response.py                ← You may need to extend
│
├── tests/
│   ├── test_campaigns.py              ← YOU (Week 3)
│   ├── test_synthesis.py              ← YOU (Week 3)
│   ├── test_reviewer.py               ← YOU (Week 3)
│   ├── test_scoring.py                ← YOU (Week 3)
│   └── test_integration.py            ← Coordinate with QA
│
└── docs/
    └── MEMBER4_IMPLEMENTATION_PLAN.md ← This file
```

---

## ⚡ GIT WORKFLOW (ZERO CONFLICTS)

### **Step 1: Create Your Branch**
```bash
git checkout main
git pull origin main
git checkout -b feature/data-eng-agents
```

### **Step 2: Daily Commits**
```bash
# Work on your files (campaign_detector.py, synthesis_agent.py, etc.)
# At end of day:
git add src/agents/campaign_detector.py src/utils/scoring.py tests/test_campaigns.py ...
git commit -m "feat(campaign-detector): Implement clustering logic

- Added graph construction from page data
- Implemented DBSCAN clustering
- Added hashtag overlap analysis
- 10 tests with 85% coverage"
```

### **Step 3: Push Daily**
```bash
git push origin feature/data-eng-agents
```

### **Step 4: When Ready to Merge (End of Week 3)**
```bash
# Pull latest main (others may have merged)
git fetch origin
git rebase origin/main  # Rebase on latest main

# Fix any conflicts (unlikely if you followed rules)
git push origin feature/data-eng-agents --force-with-lease

# Create Pull Request on GitHub/GitLab
# Get review from Rohan (Team Lead)
# Merge when approved
```

### **Safety Rules**
✅ DO: Commit daily  
✅ DO: Push daily to your branch  
✅ DO: Only modify your 5 files  
✅ DO: Only add to shared __init__.py files  

❌ DON'T: Modify orchestration.py  
❌ DON'T: Modify base_agent.py  
❌ DON'T: Modify content_analyzer, rag_agent, research_agent  
❌ DON'T: Force push to main  
❌ DON'T: Rewrite history  

---

## 🔍 CODE QUALITY CHECKLIST

Before each commit, verify:

```python
# Campaign Detector Agent
- [ ] Inherits from BaseAgent properly
- [ ] All methods have type hints
- [ ] Docstrings on all public methods
- [ ] Error handling for invalid input
- [ ] Logging statements for debugging
- [ ] No hardcoded values (use config)
- [ ] Tests pass locally
- [ ] 80%+ test coverage

# Synthesis Agent
- [ ] Handles empty/partial results gracefully
- [ ] Report is coherent and readable
- [ ] Evidence ranked by relevance
- [ ] Key findings (5-10) properly extracted
- [ ] Professional tone throughout
- [ ] All agent results accounted for

# Reviewer Agent
- [ ] Clear evaluation criteria
- [ ] Specific, actionable feedback
- [ ] Identifies real issues
- [ ] Doesn't approve poor syntheses
- [ ] Tests cover edge cases

# Reflection Loop
- [ ] Converges in ≤3 iterations
- [ ] Escalates gracefully on failure
- [ ] Tracks feedback history
- [ ] Prevents infinite loops
- [ ] Logs each iteration

# Trust Score
- [ ] Score range: 0-100
- [ ] Components weighted correctly
- [ ] Risk level assignment accurate
- [ ] Confidence score meaningful
- [ ] Algorithm documented

# All Code
- [ ] Uses snake_case for functions/variables
- [ ] Classes use PascalCase
- [ ] No trailing whitespace
- [ ] Lines < 88 chars (black formatter)
- [ ] Imports organized (stdlib, third-party, local)
```

---

## 🤝 COMMUNICATION WITH TEAM

### **Daily (10 AM Standup)**
- What you completed yesterday
- What you're working on today
- Any blockers you hit

### **Weekly (Friday 4 PM)**
- Full week review
- Milestone status
- Next week plan

### **If You Get Stuck**
1. Check LLD_AND_TEAM_PLAN.md (Part 2)
2. Review related agent implementations
3. Ask in standup immediately
4. Reach out to Rohan (Team Lead)

### **Interdependencies to Track**
- **Depends on:** ML/NLP Specialist completing detection agents (by Mon Week 3)
- **Blocks:** Rohan's orchestration integration (needs your agents Wed Week 3)
- **Needs from:** BaseAgent from Rohan (Fri Week 1)

---

## 📊 SUCCESS METRICS

### **By End of Week 3**
- [ ] All 5 deliverables implemented
- [ ] 88+ test cases written
- [ ] 80%+ code coverage
- [ ] All tests passing
- [ ] Zero merge conflicts
- [ ] Agents callable by Rohan's orchestrator

### **By End of Week 4**
- [ ] End-to-end integration working
- [ ] Demo runs without errors
- [ ] Code reviewed and approved
- [ ] Documentation complete
- [ ] Performance benchmarked

### **Demo Day Success**
- [ ] Campaign detection shows 2-3 coordinated pages
- [ ] Synthesis report is coherent & professional
- [ ] Reviewer + loop improves report (if needed)
- [ ] Trust score matches page quality
- [ ] All tests pass (80%+ coverage)
- [ ] No bugs during demo

---

## 💡 TIPS FOR SUCCESS

1. **Start with skeleton code** (Week 2) - Get structure right first
2. **Test-driven development** - Write tests before implementation
3. **Use sample data** - Create realistic test datasets early
4. **Coordinate with ML/NLP** - Understand their agent outputs
5. **Pair with Rohan weekly** - Ensure orchestration compatibility
6. **Document as you go** - Don't leave docs for Week 4
7. **Commit daily** - Small, frequent commits = zero conflicts
8. **Review your own code first** - Before asking for review
9. **Performance test** - Make sure agents run in < 5s
10. **Plan buffer time** - Reserve Friday for unexpected fixes

---

## 📚 HELPFUL RESOURCES

### **LangChain Documentation**
- Agent types: https://python.langchain.com/docs/modules/agents/
- Tool use: https://python.langchain.com/docs/modules/agents/tools/
- Agent executor: https://python.langchain.com/docs/modules/agents/agent_executor/

### **Graph Analysis**
- NetworkX docs: https://networkx.org/
- Clustering: https://scikit-learn.org/stable/modules/clustering.html

### **Team Resources**
- LLD_AND_TEAM_PLAN.md - Complete architecture
- IMPLEMENTATION_CHECKLIST.md - Weekly breakdown
- Test examples from ML/NLP team (once available)

---

## 🎯 FINAL DELIVERABLE CHECKLIST

```markdown
## Week 3 Completion - Ready for Merge

### Campaign Detector Agent
- [ ] src/agents/campaign_detector.py (200+ lines)
- [ ] tests/test_campaigns.py (30+ tests, 85%+ coverage)
- [ ] Detects coordinated pages accurately
- [ ] Handles edge cases (1-page, 100-pages)
- [ ] Performance: < 2s for 10 pages

### Synthesis Agent
- [ ] src/agents/synthesis_agent.py (200+ lines)
- [ ] tests/test_synthesis.py (18+ tests, 85%+ coverage)
- [ ] Generates coherent reports
- [ ] Extracts 5-10 key findings
- [ ] Professional writing quality

### Reviewer Agent
- [ ] src/agents/reviewer_agent.py (150+ lines)
- [ ] Evaluates all quality criteria
- [ ] Provides actionable feedback
- [ ] High precision (few false positives)

### Reflection Loop
- [ ] src/workflow/reflection_loop.py (100+ lines)
- [ ] tests/test_reviewer.py (13+ tests)
- [ ] Converges in ≤3 iterations
- [ ] Graceful escalation

### Scoring System
- [ ] src/utils/scoring.py (150+ lines)
- [ ] tests/test_scoring.py (12+ tests)
- [ ] Score range 0-100
- [ ] Accurate risk levels
- [ ] Interpretable confidence

### Code Quality
- [ ] 80%+ test coverage overall
- [ ] All tests passing
- [ ] Type hints on all functions
- [ ] Docstrings complete
- [ ] No hardcoded values
- [ ] Proper error handling
- [ ] Comprehensive logging

### Integration
- [ ] All agents inherit from BaseAgent
- [ ] Compatible with orchestrator interface
- [ ] Output formats match expectations
- [ ] No dependencies between your agents
- [ ] Ready for Rohan's workflow integration

### Documentation
- [ ] Function docstrings with examples
- [ ] Algorithm documentation
- [ ] Test case documentation
- [ ] Usage examples
- [ ] Assumptions and limitations
```

---

## 📞 EMERGENCY CONTACTS

**Project Lead (Rohan):** [Will provide during Week 1]  
**Backup (Team Lead):** [Will provide during Week 1]  
**Your GitHub/Email:** adepu.shreya@[company]

---

**Version:** 1.0  
**Created:** 2026-06-12  
**Last Updated:** 2026-06-12  
**Status:** Ready to Execute

🚀 **You've got this! Start Week 2 with confidence knowing your scope is clear and merge conflicts are impossible.**


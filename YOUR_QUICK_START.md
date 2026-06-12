# Quick Start Guide for Team Member 3 (ML/NLP Specialist)

**Time to Read This:** 5 minutes  
**Then Read Full Plan:** `TEAM_MEMBER_3_EXECUTION_PLAN.md` (30 minutes)

---

## Your Mission in 30 Seconds

You are **Team Member 3 - ML/NLP Specialist**. You need to build **3 agents** for NarrativeWatch AI:

1. **Content Analyzer** - Extract features from Instagram posts (emotions, themes, hashtags)
2. **Bias Detector** - Detect political, gender, and ideological bias
3. **Bot Detector** - Analyze engagement patterns for bot activity

**Timeline:** Week 2-3 (5-10 days of focused work)  
**Deadline:** Friday Week 2 (all agents done + tested)  
**Then:** Week 3 - Integrate with orchestrator

---

## Your File Ownership (CRITICAL - Avoid Merge Conflicts)

### ✅ ONLY YOU TOUCH THESE FILES:
```
src/agents/content_analyzer.py     ← Agent 1
src/agents/bias_detector.py        ← Agent 2
src/agents/bot_detector.py         ← Agent 3
src/utils/text_processor.py        ← Utilities for agents
src/utils/embedding_utils.py       ← Embedding helpers
tests/test_content_analyzer.py     ← Your tests
tests/test_bias_detector.py        ← Your tests
tests/test_bot_detector.py         ← Your tests
```

### ❌ DO NOT TOUCH (Other teams):
```
src/agents/orchestrator.py         ← Rohan
src/agents/rag_agent.py            ← Backend Specialist
src/agents/research_agent.py       ← Backend Specialist
src/agents/synthesis_agent.py      ← Data Engineer
src/agents/campaign_detector.py    ← Data Engineer
src/agents/reviewer_agent.py       ← Data Engineer
src/workflow/                      ← Rohan
src/apis/                          ← Backend Specialist
src/database/                      ← Backend Specialist
```

### 🤝 SHARED (Be careful, coordinate):
```
src/agents/__init__.py             ← Add your agents to imports
src/utils/__init__.py              ← Add utilities to imports
requirements.txt                   ← Add ML/NLP libraries
```

---

## Your Timeline (Day by Day)

| When | What | Deliverable |
|------|------|-------------|
| **Mon Week 2** | Setup & Design | Development environment ready, design document |
| **Tue Week 2** | Utilities | text_processor.py + embedding_utils.py complete |
| **Wed Week 2** | Content Analyzer | Agent + unit tests done |
| **Thu Week 2** | Bias Detector | Agent + unit tests done |
| **Fri Week 2** | Bot Detector | Agent + integration tests done |
| **Mon-Tue Week 3** | Testing & Docs | 80%+ test coverage, documentation complete |
| **Wed Week 3** | Integration Ready | Agents callable by orchestrator, sign-off |

---

## What Agents Should Output (JSON Format)

### Content Analyzer Output
```json
{
    "status": "success",
    "analysis": {
        "emotional_language": {"positive": 0.7, "negative": 0.2, "neutral": 0.1},
        "narrative_themes": ["conspiracy", "propaganda"],
        "hashtag_patterns": {"#trending": 5},
        "posting_pattern": {"frequency": "daily", "consistency": 0.8},
        "engagement_metrics": {"avg_likes": 1000, "engagement_rate": 0.05}
    }
}
```

### Bias Detector Output
```json
{
    "status": "success",
    "analysis": {
        "political_bias": {"left": 0.2, "center": 0.3, "right": 0.5, "confidence": 0.85},
        "gender_bias": {"male": 0.1, "female": 0.8, "neutral": 0.1},
        "ideological_bias": {"progressive": 0.3, "conservative": 0.6},
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
        "engagement_velocity": {"anomaly_detected": true, "z_score": 3.2},
        "comment_authenticity": {"repetition_percentage": 0.6},
        "follower_anomalies": {"growth_anomaly": true}
    }
}
```

---

## Your Dependencies (What You Need)

### From Rohan (Project Lead)
- [x] `src/agents/base_agent.py` - Base class for all agents
- [x] `src/config.py` - Configuration management
- [x] `src/logger.py` - Logging setup
- **Expected:** Ready by Monday Week 2

### From Backend Specialist
- [ ] API wrappers (optional - you can mock for testing)
- **Expected:** Can help if needed

### What You DON'T Need
- ✅ You can work independently
- ✅ You can mock external dependencies
- ✅ You can test in isolation

---

## ML/NLP Libraries to Use

```bash
# Install these in your virtual environment
pip install nltk spacy textblob
pip install transformers torch  # For bias detection
pip install scikit-learn scipy numpy pandas  # For bot detection
pip install pytest pytest-cov  # For testing

# Then download NLTK/spacy data
python -m spacy download en_core_web_sm
python -m textblob.download_corpora
```

---

## Code Quality Checklist

Before you commit/push, verify:

- [ ] Type hints on all functions: `def run(self, data: str) -> dict:`
- [ ] Docstrings (one-liner for obvious): `"""Extract hashtags from caption."""`
- [ ] Error handling: try/except with proper logging
- [ ] No hardcoded values (use config.py)
- [ ] Tests for all functions (80%+ coverage)
- [ ] Run black formatter: `black src/agents/ src/utils/`
- [ ] Run flake8: `flake8 src/agents/ src/utils/`

---

## Git Workflow (Avoid Conflicts!)

### Daily routine:
```bash
# Morning - stay in sync
git fetch origin
git rebase origin/develop

# Work on your code
git add src/agents/content_analyzer.py
git commit -m "feat: implement content analyzer with hashtag extraction"

# End of day - push
git push origin feature/ml-nlp-agents
```

### Golden Rule:
**Only commit to files you own. Only push to your own branch.**

If you see conflicts, it means someone else is touching your files (bad!) or you're on wrong branch (very bad!).

---

## Who to Ask For Help

| Question | Ask |
|----------|-----|
| "Is BaseAgent ready?" | Rohan |
| "What output format for synthesis agent?" | Data Engineer |
| "Should I use transformers or huggingface?" | Rohan (he knows the stack) |
| "How do I use the API wrappers?" | Backend Specialist |
| "Merge conflicts!" | Rohan (project lead) |

---

## Success = No Merge Conflicts + Great Code

✅ **You succeed when:**
1. All 3 agents implemented
2. 80%+ test coverage
3. Output matches spec exactly
4. Zero merge conflicts
5. Code reviewed and approved
6. Ready to integrate with orchestrator

❌ **You fail if:**
1. Agents not done by Friday Week 2
2. Tests don't pass
3. Merge conflicts with other teams (should be 0)
4. Output format doesn't match spec
5. Code quality issues

---

## Your Detailed Plan

**Full execution plan with day-by-day tasks:** `TEAM_MEMBER_3_EXECUTION_PLAN.md`

Read it after this. It has:
- Detailed day-by-day breakdown
- Code templates to get started
- Conflict avoidance strategies
- Performance targets
- All output schema specs
- Troubleshooting guide

---

## Next Steps RIGHT NOW

1. ✅ You read this file (5 min)
2. 📖 Read `TEAM_MEMBER_3_EXECUTION_PLAN.md` (30 min)
3. 💻 Set up environment tomorrow (Mon Week 2)
4. 🏗️ Start with text_processor.py
5. 🧪 Write tests as you go
6. 📤 Push daily (no merge conflicts!)
7. ✨ Ship Friday Week 2

---

**You've got this! Questions? Reach out to Rohan.** 🚀

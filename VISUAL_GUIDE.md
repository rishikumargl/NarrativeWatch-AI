# Visual Guide: Your Role in NarrativeWatch AI

---

## 1. System Architecture (Where You Fit)

```
┌─────────────────────────────────────────────────────────────┐
│              USER QUERY (Instagram Page Analysis)           │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│         ORCHESTRATOR AGENT (Rohan) - Route & Coordinate    │
└────┬─────────┬─────────┬───────────┬──────────┬───────────┬─┘
     ↓         ↓         ↓           ↓          ↓           ↓
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│Content  │ │  Bias   │ │  Bot    │ │  RAG   │ │Research│ │Campaign│
│Analyzer │ │Detector │ │Detector │ │Agent   │ │Agent   │ │Detector│
│ (YOU)   │ │ (YOU)   │ │ (YOU)   │ │(Backend)│ │(Backend)│ │(Data)  │
└────┬────┘ └────┬────┘ └────┬────┘ └────────┘ └────────┘ └────────┘
     │           │           │
     └───────────┴───────────┘
                 ↓
      ┌──────────────────────┐
      │ SYNTHESIS AGENT      │
      │ (Data Engineer)      │
      │ Combine findings     │
      └──────────┬───────────┘
                 ↓
      ┌──────────────────────┐
      │ REVIEWER AGENT       │
      │ (Data Engineer)      │
      │ Quality Check Loop   │
      └──────────┬───────────┘
                 ↓
      ┌──────────────────────┐
      │ Approved Report +    │
      │ Trust Score (0-100)  │
      └──────────────────────┘
```

**KEY:** Your agents (content analyzer, bias detector, bot detector) are called by the Orchestrator and feed data to the Synthesis Agent.

---

## 2. Your 3 Agents: Input → Process → Output

```
┌──────────────────────────────────────────────────────────────┐
│                   CONTENT ANALYZER AGENT                      │
├──────────────────────────────────────────────────────────────┤
│ INPUT: {caption, hashtags, posting_time, engagement_data}    │
│                                                               │
│ PROCESS:                                                      │
│  1. Tokenize caption → NLP processing                         │
│  2. Extract hashtag patterns → Count frequencies              │
│  3. Classify emotional language → Sentiment analysis          │
│  4. Identify narrative themes → Pattern matching              │
│  5. Analyze posting pattern → Timing analysis                 │
│                                                               │
│ OUTPUT: {emotions, themes, hashtags, timing, engagement}      │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                   BIAS DETECTOR AGENT                         │
├──────────────────────────────────────────────────────────────┤
│ INPUT: {caption, language_patterns, comments}                │
│                                                               │
│ PROCESS:                                                      │
│  1. Load bias detection models → HuggingFace transformers     │
│  2. Analyze political bias → Left/Center/Right scoring        │
│  3. Analyze gender bias → Male/Female/Neutral scoring         │
│  4. Analyze ideological bias → Progressive/Conservative       │
│  5. Calculate toxicity score → Text toxicity model            │
│                                                               │
│ OUTPUT: {political_bias, gender_bias, ideology, toxicity}     │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                   BOT DETECTOR AGENT                          │
├──────────────────────────────────────────────────────────────┤
│ INPUT: {comments, likes, follower_data, engagement_timing}   │
│                                                               │
│ PROCESS:                                                      │
│  1. Analyze engagement velocity → Z-score anomaly detection   │
│  2. Analyze comment patterns → String similarity analysis     │
│  3. Analyze follower growth → Growth rate anomalies           │
│  4. Detect coordinated engagement → Timing correlation        │
│  5. Calculate bot_activity_score → Weighted combination       │
│                                                               │
│ OUTPUT: {velocity_anomaly, comment_patterns, followers, score}│
└──────────────────────────────────────────────────────────────┘
```

---

## 3. Weekly Timeline for You

```
┌─────────────────────────────────────────────────────────────┐
│                     WEEK 2 (Agent Dev)                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ MON: Setup & Design                                          │
│  └─ Environment ready, design doc created                    │
│     DELIVERABLE: textprocessor.py skeleton + test plan       │
│                                                              │
│ TUE: Text Processing Utilities                              │
│  └─ text_processor.py + embedding_utils.py complete         │
│  └─ Unit tests for utilities                                │
│     DELIVERABLE: 2 utility modules with 80%+ coverage        │
│                                                              │
│ WED: Content Analyzer Agent                                 │
│  └─ Full implementation                                      │
│  └─ Unit tests for extraction logic                         │
│     DELIVERABLE: Working agent, 5-10 test cases             │
│                                                              │
│ THU: Bias Detector Agent                                    │
│  └─ Model integration (HuggingFace)                         │
│  └─ Scoring logic implementation                            │
│     DELIVERABLE: Working agent, comprehensive tests          │
│                                                              │
│ FRI: Bot Detector Agent + Integration                       │
│  └─ Statistical analysis functions                          │
│  └─ Integration testing of all 3 agents                     │
│     DELIVERABLE: All 3 agents done, ready for orchestrator  │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                  WEEK 3 (Integration)                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ MON-TUE: Testing & Documentation                            │
│  └─ Achieve 80%+ test coverage                             │
│  └─ Write docstrings and usage examples                    │
│  └─ Create output schema documentation                     │
│                                                              │
│ WED-FRI: Integration Ready                                  │
│  └─ Meet with Data Engineer (Synthesis integration)         │
│  └─ Meet with Rohan (Orchestrator integration)              │
│  └─ Final code review and sign-off                         │
│  └─ Merge to develop branch                                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. File Organization & Ownership

```
NarrativeWatch-AI/
│
├── src/
│   │
│   ├── agents/
│   │   ├── base_agent.py          ← Rohan (DO NOT TOUCH)
│   │   ├── orchestrator.py         ← Rohan (DO NOT TOUCH)
│   │   │
│   │   ├── content_analyzer.py     ★ YOU WRITE THIS
│   │   ├── bias_detector.py        ★ YOU WRITE THIS
│   │   ├── bot_detector.py         ★ YOU WRITE THIS
│   │   │
│   │   ├── rag_agent.py            ← Backend (DO NOT TOUCH)
│   │   ├── research_agent.py       ← Backend (DO NOT TOUCH)
│   │   │
│   │   ├── synthesis_agent.py      ← Data Engineer (DO NOT TOUCH)
│   │   ├── campaign_detector.py    ← Data Engineer (DO NOT TOUCH)
│   │   └── reviewer_agent.py       ← Data Engineer (DO NOT TOUCH)
│   │
│   ├── utils/
│   │   ├── text_processor.py       ★ YOU WRITE THIS
│   │   ├── embedding_utils.py      ★ YOU WRITE THIS
│   │   │
│   │   └── scoring.py              ← Data Engineer (DO NOT TOUCH)
│   │
│   ├── workflow/                   ← Rohan (DO NOT TOUCH)
│   ├── apis/                       ← Backend (DO NOT TOUCH)
│   ├── database/                   ← Backend (DO NOT TOUCH)
│   │
│   ├── config.py                   ← Rohan (READ ONLY)
│   ├── logger.py                   ← Rohan (READ ONLY)
│   └── app.py                      ← Frontend (DO NOT TOUCH)
│
├── tests/
│   ├── test_content_analyzer.py    ★ YOU WRITE THIS
│   ├── test_bias_detector.py       ★ YOU WRITE THIS
│   ├── test_bot_detector.py        ★ YOU WRITE THIS
│   │
│   ├── test_agents.py              ← Others (might reference your code)
│   ├── test_apis.py                ← Backend
│   ├── test_integration.py         ← QA Lead
│   └── fixtures/                   ← Shared test data
│
└── requirements.txt                ← Shared (coordinate changes)

★ = You own this file - ONLY you modify it
← = Someone else owns - DO NOT MODIFY
```

---

## 5. Git Branches & Merging Strategy

```
                              main
                               ↑
                          (final merge)
                               │
                            develop
                               ↑
        ┌──────────┬──────────┬─┼─┬──────────┬──────────┐
        │          │          │ │ │          │          │
    orchestrator backend   ml-nlp  data-eng frontend  qa
    (Rohan)     (Backend)   (YOU)  (Data)    (Frontend) (QA)
    
    Each team works on their own branch
    ✅ ONLY commits to own files
    ✅ Daily push to own branch
    ✅ Weekly PR to develop
    ✅ Zero conflicts if file ownership respected

YOUR BRANCH: feature/ml-nlp-agents
NEVER switch to other branches during development
ONLY merge TO develop at end of Week 3
```

---

## 6. Merge Conflict Prevention Strategy

```
┌─ DO THIS ────────────────────────────────────────────┐
│                                                       │
│ ✅ Only modify YOUR assigned files                   │
│ ✅ Daily git push to YOUR branch                     │
│ ✅ Weekly rebase from develop (absorb others' work) │
│ ✅ Coordinate with Data Engineer on output schema    │
│ ✅ Ask Rohan before using BaseAgent features        │
│                                                       │
└───────────────────────────────────────────────────────┘

┌─ DON'T DO THIS ──────────────────────────────────────┐
│                                                       │
│ ❌ Touch other teams' files                          │
│ ❌ Merge other branches into your branch              │
│ ❌ Modify shared files without coordination           │
│ ❌ Push to develop directly (create PR instead)      │
│ ❌ Revert others' changes                            │
│                                                       │
└───────────────────────────────────────────────────────┘

RESULT: If you follow ✅, you will have ZERO merge conflicts
```

---

## 7. Agent Output Flow

```
Your Agent Outputs          Data Engineer Uses             Synthesis Agent
(Your Responsibility)    (Their Responsibility)          (Their Output)

Content Analyzer:
├─ emotions
├─ themes              ┐
├─ hashtags            │
├─ posting_pattern     ├─→  Synthesis  ──→  Combined Report
├─ engagement_metrics  │    Agent          (all findings)
│                      │
Bias Detector:         │
├─ political_bias      ├─→  Synthesis  ──→  Trust Score
├─ gender_bias         │    Agent          (0-100)
├─ ideology            │
└─ toxicity            │
                       │
Bot Detector:          │
├─ bot_activity_score  │
├─ velocity_anomaly    ├─→  Synthesis  ──→  Risk Flags
├─ comment_patterns    │    Agent
└─ follower_anomalies  │
                       ├─→  Reviewer   ──→  Approved Report
RAG Agent (Backend):   │    Agent
└─ similar_patterns    │
                       │
Research Agent (Backend):
└─ external_data       ┘

Campaign Detector (Data Engineer):
└─ campaign_info       ┘
```

---

## 8. Critical Success Factors

```
╔════════════════════════════════════════════════════════════╗
║ SUCCESS = Code Quality + Testing + Zero Conflicts          ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║ MUST ACHIEVE:                                              ║
║  ✓ All 3 agents implemented (Friday Week 2)               ║
║  ✓ 80%+ test coverage                                      ║
║  ✓ Output matches specification exactly                    ║
║  ✓ Zero merge conflicts                                    ║
║  ✓ Code review approved                                    ║
║  ✓ Integrated with orchestrator (Wed Week 3)              ║
║                                                            ║
║ PERFORMANCE TARGETS:                                       ║
║  • Content Analyzer: < 2 seconds per post                  ║
║  • Bias Detector: < 3 seconds per post                     ║
║  • Bot Detector: < 5 seconds (with engagement data)        ║
║                                                            ║
║ CODE QUALITY STANDARDS:                                    ║
║  • Type hints: `def run(self, data: str) -> dict:`        ║
║  • Docstrings: One-liner for obvious, multi-line for WHY   ║
║  • Error handling: try/except with logging                 ║
║  • No hardcoded values: Use config.py                      ║
║  • PEP 8 compliant: Run `black` formatter                  ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
```

---

## 9. Communication & Escalation Matrix

```
QUESTION                          ASK WHO              RESPONSE TIME
────────────────────────────────────────────────────────────────
"Is BaseAgent ready?"              Rohan (Lead)         Same day
"What output format expected?"     Data Engineer        Same day
"How to use API wrapper?"          Backend Specialist   Same day
"Should I use Model X or Y?"       Rohan                Same day
"Merge conflict!"                  Rohan (URGENT)       30 min
"Requirements unclear?"            Rohan + Data Engineer Same day
"Need test data for agent?"        Backend Specialist   Next day
```

---

## 10. Success Checklist (Fill this out daily)

```
WEEK 2 DAILY CHECKLIST:

MON ▢ Environment setup complete
    ▢ BaseAgent class reviewed
    ▢ Design document created
    ▢ First commit pushed

TUE ▢ text_processor.py done
    ▢ embedding_utils.py done
    ▢ Unit tests written
    ▢ Code review passed

WED ▢ content_analyzer.py done
    ▢ Integration tests passed
    ▢ Coverage > 80%
    ▢ Push to branch

THU ▢ bias_detector.py done
    ▢ Model loading tested
    ▢ Scoring logic verified
    ▢ Push to branch

FRI ▢ bot_detector.py done
    ▢ All agents working together
    ▢ Output format verified
    ▢ Ready for integration review
    ▢ Pull request created

Status: Track daily in team standup
```

---

**Everything clear? → Start with `TEAM_MEMBER_3_EXECUTION_PLAN.md` (30-min read)**

**Questions? → Reach out to Rohan immediately**

**Ready to code? → Start Monday Week 2!** 🚀

# LLM Model Strategy for NarrativeWatch AI

**Date:** June 12, 2026  
**LLM Provider:** Groq  
**Strategy:** Multi-model for optimal performance

---

## 🎯 Model Selection Rationale

Different agents need different models based on their role:

- **Lightweight/Fast agents**: mixtral-8x7b-32768 (balanced, fast)
- **Complex reasoning**: llama-3.1-70b-versatile (more capable)
- **Critical analysis**: llama-3.1-70b-versatile (best for quality)

---

## 📊 Agent Model Assignments

### Tier 1: Best Model (llama-3.1-70b-versatile)
**Use case:** Critical analysis, quality assurance, complex reasoning

```python
ReviewerAgent()           # Quality assurance with reflection loop
SynthesisAgent()         # Combines 8 agent outputs into coherent report
```

**Why:**
- Better at catching inconsistencies
- Superior reasoning for complex patterns
- Critical for ensuring output quality
- Reflection loop needs best possible analysis

---

### Tier 2: Balanced Model (mixtral-8x7b-32768) - DEFAULT
**Use case:** Standard analysis, fast processing, parallel execution

```python
OrchestratorAgent()      # Routes tasks between agents
ContentAnalyzerAgent()   # Extracts article features
RAGAgent()               # Vector semantic search
ResearchAgent()          # Tavily queries
BiasDetectorAgent()      # Detects bias indicators
SentimentAnalyzerAgent() # Emotional tone analysis
NarrativeTrackerAgent()  # Pattern detection
BotDetectorAgent()       # Bot activity analysis
CampaignDetectorAgent()  # Coordinated narratives
```

**Why:**
- Fast inference (important for parallel execution)
- Balanced quality for standard analysis tasks
- Cost effective
- Low latency for real-time analysis

---

## 🚀 Groq Model Comparison

| Model | Speed | Quality | Best For | Tokens/Min |
|-------|-------|---------|----------|-----------|
| mixtral-8x7b-32768 | ⚡⚡⚡ Fast | ⭐⭐⭐⭐ Good | General tasks, fast processing | ~30k |
| llama-3.1-70b-versatile | ⚡⚡ Medium | ⭐⭐⭐⭐⭐ Excellent | Complex reasoning, QA, analysis | ~6-10k |
| llama-3.1-405b | ⚡ Slower | ⭐⭐⭐⭐⭐⭐ Best | Very complex tasks (avoid for latency) | ~1-2k |

---

## 💡 Performance Metrics

### Single Article Analysis (Expected)
```
ContentAnalyzer (mixtral)      ~2s
RAGAgent (mixtral)             ~1.5s
ResearchAgent (mixtral)        ~3s
BiasDetector (mixtral)         ~1.5s
SentimentAnalyzer (mixtral)    ~1s
NarrativeTracker (mixtral)     ~1.5s
BotDetector (mixtral)          ~1s
CampaignDetector (mixtral)     ~1.5s
─────────────────────────────────────
Parallel execution total:      ~3s (all run in parallel)

SynthesisAgent (mixtral)       ~2s
ReviewerAgent (llama-70b)      ~2s (more analysis, worth the time)
─────────────────────────────────────
Total: ~7-8 seconds for full analysis
```

---

## 🎯 Model Implementation

### Current Implementation

```python
# src/agents/base_agent.py
class BaseAgent:
    def __init__(self, ..., model_name: str = "mixtral-8x7b-32768"):
        self.model_name = model_name
        # Uses specified model for this agent
```

### Agent Initialization Examples

```python
# Default (mixtral)
class ContentAnalyzerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Content Analyzer",
            description="...",
            model_name="mixtral-8x7b-32768"  # Default
        )

# Premium (llama-70b)
class ReviewerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Reviewer Agent",
            description="...",
            model_name="llama-3.1-70b-versatile"  # Premium for quality
        )

# Explicit override
class CustomAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Custom Agent",
            description="...",
            model_name="llama-3.1-405b"  # For ultra-complex tasks
        )
```

---

## 🔧 Groq Available Models

```
Mixtral Series:
  • mixtral-8x7b-32768      Default, fast, balanced

Llama Series:
  • llama-3.1-8b-instant    Small, very fast
  • llama-3.1-70b-versatile Medium, best value
  • llama-3.1-405b          Large, most capable

Claude Series (if available):
  • (Check Groq documentation for latest)
```

---

## 📈 Cost & Performance Tradeoff

**Optimization Strategy:**

1. **Default Agent (mixtral-8x7b-32768)**
   - Cost: Base rate (~$0.02/1M tokens)
   - Speed: Fast (~30k tokens/min)
   - Quality: Good for standard tasks

2. **ReviewerAgent (llama-3.1-70b-versatile)**
   - Cost: 2-3x higher (~0.05-0.06/1M tokens)
   - Speed: Medium (~6-10k tokens/min)
   - Quality: Superior for critical analysis
   - ROI: Worth the cost for quality assurance

3. **Avoid for now: llama-3.1-405b**
   - Cost: 10x higher
   - Speed: Very slow
   - Quality: Maximum (overkill for most tasks)
   - Use: Only for ultra-critical analysis if needed

---

## 🎯 Recommended Configuration

**Production Setup:**

```python
# Tier 1: Quality (Reviewer, Synthesis)
REVIEWER_MODEL = "llama-3.1-70b-versatile"
SYNTHESIS_MODEL = "llama-3.1-70b-versatile"  # Or mixtral if latency critical

# Tier 2: Standard (All other agents)
DEFAULT_MODEL = "mixtral-8x7b-32768"

# Tier 3: Small (Optional, if latency becomes bottleneck)
# FAST_MODEL = "llama-3.1-8b-instant"
```

---

## 🚀 How to Change Models

### Method 1: Agent-specific override
```python
class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="My Agent",
            description="...",
            model_name="llama-3.1-70b-versatile"  # Use specific model
        )
```

### Method 2: Environment variable (future enhancement)
```python
# In config.py
REVIEWER_MODEL = os.getenv("REVIEWER_MODEL", "llama-3.1-70b-versatile")
SYNTHESIS_MODEL = os.getenv("SYNTHESIS_MODEL", "mixtral-8x7b-32768")
DEFAULT_MODEL = os.getenv("LLM_MODEL", "mixtral-8x7b-32768")
```

### Method 3: Dynamic selection based on task
```python
class DynamicAgent(BaseAgent):
    def __init__(self, task_complexity: str = "medium"):
        model = "mixtral-8x7b-32768" if task_complexity == "simple" else "llama-3.1-70b-versatile"
        super().__init__(
            name="Dynamic Agent",
            description="...",
            model_name=model
        )
```

---

## 📊 Current Implementation Status

| Agent | Model | Status | Notes |
|-------|-------|--------|-------|
| Orchestrator | mixtral-8x7b-32768 | ✅ Ready | Routes tasks, standard |
| ContentAnalyzer | mixtral-8x7b-32768 | ✅ Ready | Fast feature extraction |
| RAGAgent | mixtral-8x7b-32768 | ✅ Ready | Vector search, fast |
| ResearchAgent | mixtral-8x7b-32768 | ✅ Ready | API calls, standard |
| BiasDetector | mixtral-8x7b-32768 | ✅ Ready | Pattern detection |
| SentimentAnalyzer | mixtral-8x7b-32768 | ✅ Ready | Fast sentiment |
| NarrativeTracker | mixtral-8x7b-32768 | ✅ Ready | Pattern analysis |
| BotDetector | mixtral-8x7b-32768 | ✅ Ready | Engagement analysis |
| CampaignDetector | mixtral-8x7b-32768 | ✅ Ready | Pattern clustering |
| **ReviewerAgent** | **llama-3.1-70b-versatile** | ✅ **UPDATED** | Quality assurance |
| **SynthesisAgent** | mixtral-8x7b-32768 | 🔄 Consider upgrade | Combines results |

---

## 🎯 Future Optimizations

### Phase 1 (Now): Implemented ✅
- ReviewerAgent uses llama-3.1-70b-versatile
- All others use mixtral-8x7b-32768

### Phase 2 (Optional):
- Upgrade SynthesisAgent to llama-3.1-70b-versatile
- Monitor costs vs quality tradeoff

### Phase 3 (Advanced):
- Dynamic model selection based on:
  - Task complexity
  - User importance level
  - System load
  - Cost budget

---

## 💰 Cost Estimation

**Per 1000 articles analyzed:**

```
Mixtral only (all agents):
  ~10,000 tokens per article
  × 1000 articles = 10M tokens
  × $0.02/1M = $0.20

Mixed (with llama-70b for Reviewer):
  ~10,000 tokens per article × 0.8 = 8,000 (mixtral agents)
  ~5,000 tokens per article × 0.2 = 1,000 (llama reviewer)
  × 1000 articles = 9M tokens
  × $0.02-0.05 = $0.25-0.30 (slight increase for quality)
```

**ROI: Small cost increase for significant quality improvement** ✅

---

## 📝 Configuration File Example

```python
# src/config.py - Add these settings

# LLM Model Strategy
LLM_MODEL_DEFAULT = "mixtral-8x7b-32768"      # Fast, balanced
LLM_MODEL_REVIEWER = "llama-3.1-70b-versatile"  # Best for QA
LLM_MODEL_SYNTHESIS = "mixtral-8x7b-32768"     # Fast aggregation

# Model settings per agent
AGENT_MODELS = {
    "orchestrator": "mixtral-8x7b-32768",
    "content_analyzer": "mixtral-8x7b-32768",
    "rag_agent": "mixtral-8x7b-32768",
    "research_agent": "mixtral-8x7b-32768",
    "bias_detector": "mixtral-8x7b-32768",
    "sentiment_analyzer": "mixtral-8x7b-32768",
    "narrative_tracker": "mixtral-8x7b-32768",
    "bot_detector": "mixtral-8x7b-32768",
    "campaign_detector": "mixtral-8x7b-32768",
    "synthesis_agent": "mixtral-8x7b-32768",
    "reviewer_agent": "llama-3.1-70b-versatile",  # Premium!
}
```

---

## ✅ Summary

**Current Setup:**
- ✅ 8 agents: mixtral-8x7b-32768 (fast, balanced)
- ✅ ReviewerAgent: llama-3.1-70b-versatile (best for quality)
- ✅ Optimal cost-performance tradeoff

**Benefits:**
- ⚡ Fast parallel execution for main agents
- 🧠 Superior quality assurance with Reviewer
- 💰 Minimal cost increase for significant benefit
- 🎯 Best practices for multi-agent systems

---

**This configuration provides excellent balance between speed, quality, and cost!** 🚀

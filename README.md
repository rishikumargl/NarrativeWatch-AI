# 🎯 NarrativeWatch AI - Real News Intelligence Platform

**Advanced Multi-Agent System for Detecting Misinformation, Bias, Emotional Manipulation, and Content Analysis in News Articles**

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [System Architecture](#system-architecture)
4. [Tech Stack](#tech-stack)
5. [Project Structure](#project-structure)
6. [Installation & Setup](#installation--setup)
7. [Usage Guide](#usage-guide)
8. [API Documentation](#api-documentation)
9. [ML Models & Analysis](#ml-models--analysis)
10. [Frontend Architecture](#frontend-architecture)
11. [Reflection Loop & Quality Assurance](#reflection-loop--quality-assurance)
12. [Contributing](#contributing)

---

## 🔍 Overview

NarrativeWatch AI is a comprehensive news intelligence platform that uses multiple specialized AI agents to analyze articles for:

- **Misinformation & Propaganda Detection**
- **Emotional Manipulation & Sensationalism**
- **Political, Gender, Ideological & Socioeconomic Bias**
- **Bot Activity & Authenticity**
- **Entity Extraction & Recognition**
- **Dynamic Trust Scoring (0-100)**

The system implements a **reflection loop** where a Synthesis Agent generates reports, a Reviewer Agent validates quality, and the process iterates (max 3 times) until approval or fallback.

### Key Differentiators
- ✅ **AI API Integration** - Uses HuggingFace & Groq APIs for analysis
- ✅ **Dynamic Scores** - Trust score calculated from actual findings (not static)
- ✅ **Reflection Loop** - Auto-improvement with reviewer validation
- ✅ **Real-time WebSocket** - Live progress updates as agents work
- ✅ **Entity Scoring** - Entities ranked by frequency, position, importance
- ✅ **URL Content Extraction** - Analyzes news articles from live URLs
- ✅ **Natural Language Reports** - Professional, readable summaries

---

## ✨ Features

### 📊 4 Core Analysis Agents

#### 1. **Content Analyzer Agent** 
- **Sentiment Analysis** (POSITIVE/NEGATIVE/NEUTRAL)
  - Model: `distilbert-base-uncased-finetuned-sst-2-english`
- **Toxicity Detection** (0-100)
  - Detects offensive/NSFW language
- **Misinformation Classification** (0-100%)
  - Model: `microsoft/deberta-large-mnli`
- **Propaganda Detection** 
  - Detects 7 techniques: loaded language, bandwagon, false dilemma, appeal to emotion, ad hominem, red herring, glittering generalities
- **Entity Extraction with Scoring**
  - Extracts: Countries, People, Organizations, Locations
  - Scores by frequency + position + importance
  - Deduplicates similar entities (USA = US = United States)

#### 2. **Bias Detector Agent**
- **5 Bias Types** (0-100 scale each):
  1. Political Bias (left-wing vs right-wing keywords)
  2. Gender Bias (male/female reference imbalance)
  3. Religious Bias (positive vs negative religious language)
  4. Ideological Bias (dogmatic language patterns)
  5. Socioeconomic Bias (class-based language)
- **ML Enhancement**: Zero-shot classification via `facebook/bart-large-mnli`
- **Overall Score**: Average of 5 bias types
- **Risk Levels**: LOW (5-30), MEDIUM (30-50), HIGH (50-70), CRITICAL (70+)

#### 3. **Bot Detector Agent**
- **Bot Probability** (0-100%)
  - Base: 5% (prevent false zeros)
  - +0-40% word repetition patterns
  - +15-20% automated language
  - +punctuation anomalies
- **Toxicity Detection** (0-100)
- **Authenticity Score** = 100 - bot_prob - (toxicity/2)

#### 4. **Misinformation Detector Agent**
- **ML Classification** (0-100%)
  - Model: `microsoft/deberta-large-mnli`
- **Propaganda Techniques** (7 types, scored)
- **Unverified Claims Detection**
  - Detects language: "allegedly", "reportedly", "leaked"
  - Risk based on ratio of unverified to significant claims
- **Emotional Manipulation** (0-75)
  - 15+ negative emotional words
  - 10+ positive emotional words
  - Extremist language patterns
- **Final Score (Weighted)**:
  ```
  ML(0.30) + Propaganda(0.25) + Unverified(0.25) + Emotional(0.20)
  ```

### 🔄 Synthesis & Review System

#### **Synthesis Agent**
- Combines all agent findings
- **Calculates Dynamic Trust Score** (10-100):
  ```
  Start: 75
  - Toxicity × 0.5
  - Misinformation × 0.3
  - Negative sentiment: -8
  - Positive sentiment: -5
  - Bias score × 0.3
  - Bot probability × 0.3
  - Misinformation risk × 0.4
  ```
- **Determines Risk Level**:
  - LOW: 75-100
  - MEDIUM: 50-75
  - HIGH: 25-50
  - CRITICAL: 0-25
- Generates natural language summary with recommendations
- LLM: `Groq llama-3.1-8b-instant`

#### **Reviewer Agent**
- Validates synthesis report quality
- Checks: trust_score, risk_level, summary presence
- Semantic validation: consistency checks
- **Stricter thresholds per iteration**:
  - Iteration 1: 0.75 quality score
  - Iteration 2: 0.80
  - Iteration 3: 0.85
- LLM: `Groq llama-3.1-8b-instant`

### 🔁 Reflection Loop

```
User Input → 4 Agents (parallel) → Synthesis Report
                                          ↓
                                    Reviewer Check
                                          ↓
                    Is Quality ≥ Threshold? → YES → Send Report
                                    ↓ NO
                          Try Again (max 3 total)
                                    ↓
                      All 3 rejected? → Fallback Message
```

### 📱 Real-time WebSocket Updates

Frontend receives live updates:
```json
{
  "type": "AGENT_START",
  "agent": "content_analyzer",
  "timestamp": "2026-06-15T10:30:00Z"
}

{
  "type": "AGENT_COMPLETE",
  "agent": "content_analyzer",
  "data": { ... findings ... }
}

{
  "type": "REFLECTION_ITERATION",
  "iteration": 1,
  "message": "Synthesis attempt 1/3..."
}

{
  "type": "ANALYSIS_COMPLETE",
  "trust_score": 72,
  "risk_level": "MEDIUM",
  "summary": "..."
}
```

---

## 🏗 System Architecture

### **Backend Architecture**

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Server (8000)                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  WebSocket Handler: /ws/analyze/{analysis_id}         │
│  ├─ Receives article URL/content                      │
│  ├─ If URL → URLExtractor fetches & parses            │
│  └─ Orchestrates 4 agents in parallel                 │
│                                                         │
├─────────────────────────────────────────────────────────┤
│               4 Core Analysis Agents                    │
│                                                         │
│  ┌─────────────────┐  ┌─────────────────┐             │
│  │ Content         │  │ Bias Detector   │             │
│  │ Analyzer        │  │                 │             │
│  │ - Sentiment     │  │ - 5 bias types  │             │
│  │ - Toxicity      │  │ - ML classify   │             │
│  │ - Propaganda    │  │ - Pattern match │             │
│  │ - Misinformation│  │ - 0-100 scoring │             │
│  │ - Entities      │  └─────────────────┘             │
│  └─────────────────┘                                   │
│                                                         │
│  ┌─────────────────┐  ┌─────────────────┐             │
│  │ Bot Detector    │  │ Misinformation  │             │
│  │                 │  │ Detector        │             │
│  │ - Bot prob (%)  │  │ - ML classify   │             │
│  │ - Toxicity      │  │ - Propaganda    │             │
│  │ - Auth score    │  │ - Unverified    │             │
│  │ - Pattern check │  │ - Emotional     │             │
│  └─────────────────┘  │ - Weighted score│             │
│                       └─────────────────┘             │
│                                                         │
├─────────────────────────────────────────────────────────┤
│            Synthesis & Review Loop (max 3)             │
│                                                         │
│  ┌──────────────────────────────────────────┐         │
│  │ Synthesis Agent (Groq llama-3.1-8b)     │         │
│  │ - Aggregate findings                     │         │
│  │ - Calculate trust score (10-100)         │         │
│  │ - Generate natural summary               │         │
│  └──────────────────────────────────────────┘         │
│                      ↓                                  │
│  ┌──────────────────────────────────────────┐         │
│  │ Reviewer Agent (Groq llama-3.1-8b)      │         │
│  │ - Validate quality                       │         │
│  │ - Check consistency                      │         │
│  │ - Semantic validation                    │         │
│  └──────────────────────────────────────────┘         │
│                      ↓                                  │
│          Approved? → Send | Retry (max 3)            │
│                                                         │
├─────────────────────────────────────────────────────────┤
│            HuggingFace Inference API                   │
│                                                         │
│ • Sentiment: distilbert-base-uncased-finetuned-sst-2  │
│ • Bias/Misinfo: facebook/bart-large-mnli              │
│ • Misinformation: microsoft/deberta-large-mnli         │
│ • Toxicity: unitary/toxic-bert                         │
│                                                         │
├─────────────────────────────────────────────────────────┤
│            Utilities & Helpers                         │
│                                                         │
│ • URLExtractor: Fetches articles from live URLs       │
│ • EntityExtractor: Regex + keyword extraction         │
│ • LocalMLModels: Wrapper for all ML models            │
│ • GroqClient: LLM API wrapper                         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### **Data Flow**

```
User Input (URL or Text)
        ↓
URL Extraction (if URL provided)
        ↓
4 Agents Run in Parallel:
├─ Content Analyzer    → sentiment, toxicity, propaganda, entities
├─ Bias Detector       → 5 bias types scored
├─ Bot Detector        → bot probability, authenticity
└─ Misinformation      → propaganda, claims, emotional, final score
        ↓
Synthesis Agent:
├─ Combines findings
├─ Calculates trust score
├─ Generates summary
└─ Returns initial report
        ↓
Reviewer Agent:
├─ Validates quality
├─ If approved → Send to frontend
├─ If rejected → Retry (max 3)
└─ If all fail → Fallback message
        ↓
WebSocket → Frontend Display
```

---

## 🛠 Tech Stack

### **Backend**
- **Framework**: FastAPI (async Python)
- **LLM API**: Groq (llama-3.1-8b-instant)
- **ML APIs**: HuggingFace Inference API
- **Web Extraction**: newspaper3k + BeautifulSoup4
- **Logging**: Python logging module
- **Database**: Optional PostgreSQL (for future history)

### **Frontend**
- **Framework**: React 18
- **Styling**: Tailwind CSS
- **State**: React hooks (useState, useContext)
- **Real-time**: WebSocket API
- **Charts**: Simple progress bars + status indicators
- **Storage**: localStorage for project persistence

### **ML APIs Used**

| Task | Model | Provider | Endpoint |
|------|-------|----------|----------|
| Sentiment | distilbert-base-uncased-finetuned-sst-2 | HuggingFace | api-inference.huggingface.co |
| Bias/Misinfo | facebook/bart-large-mnli | HuggingFace | api-inference.huggingface.co |
| Misinformation | microsoft/deberta-large-mnli | HuggingFace | api-inference.huggingface.co |
| Toxicity | unitary/toxic-bert | HuggingFace | api-inference.huggingface.co |
| LLM | llama-3.1-8b-instant | Groq | api.groq.com |

All models accessed via REST APIs, no local installation required

---

## 📁 Project Structure

```
NarrativeWatch AI/
├── backend/
│   ├── src/
│   │   ├── app.py                           # Main FastAPI server
│   │   ├── config.py                        # Configuration
│   │   ├── logger.py                        # Logging setup
│   │   │
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── content_analyzer.py          # Sentiment, toxicity, entities
│   │   │   ├── bias_detector.py             # 5 bias types
│   │   │   ├── bot_detector.py              # Bot probability
│   │   │   ├── misinformation_detector.py   # Propaganda, claims, emotion
│   │   │   ├── synthesis_agent.py           # Combines findings, trust score
│   │   │   └── reviewer_agent.py            # Quality validation
│   │   │
│   │   ├── llm/
│   │   │   └── groq_client.py               # Groq API wrapper
│   │   │
│   │   ├── ml_models_local.py               # Transformers wrapper
│   │   │
│   │   ├── utils/
│   │   │   ├── entity_extractor.py          # Entity extraction + scoring
│   │   │   ├── url_extractor.py             # Article fetching
│   │   │   └── __init__.py
│   │   │
│   │   ├── database/
│   │   │   └── connection.py                # DB setup (optional)
│   │   │
│   │   └── api/
│   │       └── __init__.py
│   │
│   ├── requirements.txt
│   ├── .env                                 # API keys (Groq)
│   └── run.py                               # Server launcher
│
├── frontend/
│   ├── public/
│   │   ├── index.html
│   │   └── favicon.ico
│   │
│   ├── src/
│   │   ├── App.jsx                          # Main app component
│   │   ├── index.css                        # Global styles
│   │   ├── index.js                         # Entry point
│   │   │
│   │   ├── pages/
│   │   │   ├── ProjectsPage.jsx             # Project list + create
│   │   │   ├── AnalyzePage.jsx              # Live analysis display
│   │   │   └── ReportPage.jsx               # Final report (future)
│   │   │
│   │   ├── components/
│   │   │   ├── AgentCard.jsx                # Individual agent progress
│   │   │   ├── TrustScoreGauge.jsx          # Trust score display
│   │   │   ├── EntityList.jsx               # Entity display
│   │   │   ├── RiskAssessment.jsx           # Risk breakdown
│   │   │   └── ReflectionLoop.jsx           # Synthesis/review status
│   │   │
│   │   └── utils/
│   │       └── websocket.js                 # WebSocket handler
│   │
│   ├── package.json
│   ├── .env                                 # React app URLs
│   └── tailwind.config.js
│
├── README.md                                # This file
└── .gitignore
```

---

## ⚙️ Installation & Setup

### **Prerequisites**
- Python 3.9+
- Node.js 16+
- 4GB+ RAM (for local ML models)
- Internet (first download of models only)

### **Step 1: Backend Setup**

```bash
# Clone repository
cd "NarrativeWatch AI"

# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows
# OR
source venv/bin/activate      # Mac/Linux

# Install dependencies
cd backend
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
DATABASE_URL=postgresql://user:pass@localhost:5432/narrativewatch
EOF

# Run server
python -m uvicorn src.app:app --host 127.0.0.1 --port 8000
```

**Get API Keys:**
1. **Groq**: https://console.groq.com (free tier available)
2. **HuggingFace**: https://huggingface.co/settings/tokens (free tier available)

### **Step 2: Frontend Setup**

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
cat > .env << EOF
REACT_APP_WS_URL=ws://localhost:8000
REACT_APP_API_URL=http://localhost:8000
EOF

# Start development server
npm start
```

App opens at `http://localhost:3000`

### **Step 3: Verify Installation**

```bash
# Backend health check
curl http://localhost:8000/health

# Expected output:
# {
#   "status": "healthy",
#   "version": "2.0",
#   "ml_models": 4,
#   "agents": 4
# }
```

---

## 📖 Usage Guide

### **Analyzing an Article**

#### **Option 1: Paste URL**
1. Click "Create New Project"
2. Enter article URL (e.g., `https://example.com/news-article`)
3. Click "Create & Analyze"
4. Watch agents process in real-time
5. View full report when complete

#### **Option 2: Paste Content**
1. Click "Create New Project"
2. Paste article text
3. Click "Create & Analyze"
4. Same workflow as above

### **Understanding Results**

#### **Trust Score (0-100)**
- **75-100**: Highly credible, well-sourced
- **50-75**: Generally trustworthy with minor issues
- **25-50**: Significant concerns, verify claims
- **0-25**: Major red flags, likely misinformation

#### **Risk Level**
- **LOW**: Safe to share
- **MEDIUM**: Verify key claims
- **HIGH**: High risk, treat skeptically
- **CRITICAL**: Don't share without verification

#### **Agent Breakdown**
- **Content Analyzer**: Sentiment, toxicity, misinformation likelihood
- **Bias Detector**: Political, gender, religious, ideological bias
- **Bot Detector**: Authenticity and automated patterns
- **Misinformation Detector**: Propaganda techniques, emotional manipulation

#### **Full Report**
Summary explains:
1. Why the trust score was assigned
2. Key findings from all agents
3. Specific recommendations for readers

---

## 📡 API Documentation

### **WebSocket Endpoint**

```
ws://localhost:8000/ws/analyze/{analysis_id}
```

#### **Message Format: Client → Server**

```json
{
  "url": "https://example.com/article",
  "content": "Optional: full article text",
  "title": "Optional: article title"
}
```

#### **Message Format: Server → Client**

```json
// Agent starts
{
  "type": "AGENT_START",
  "agent": "content_analyzer",
  "timestamp": "2026-06-15T10:30:00Z"
}

// Agent completes
{
  "type": "AGENT_COMPLETE",
  "agent": "content_analyzer",
  "data": {
    "agent": "content_analyzer",
    "findings": {
      "analysis": {
        "sentiment": { "label": "NEGATIVE", "score": 0.95 },
        "toxicity": { "toxicity_score": 27 },
        "entities": {
          "total_count": 5,
          "entities": [
            { "name": "USA", "type": "COUNTRY", "frequency": 8, "importance_score": 85.3 }
          ]
        }
      }
    }
  }
}

// Synthesis iteration
{
  "type": "REFLECTION_ITERATION",
  "iteration": 1,
  "max_iterations": 3,
  "message": "Synthesis attempt 1/3..."
}

// Review feedback
{
  "type": "REFLECTION_REVIEW",
  "iteration": 1,
  "approved": false,
  "quality_score": 0.72,
  "feedback": ["Summary too short", "Missing risk assessment"]
}

// Analysis complete
{
  "type": "ANALYSIS_COMPLETE",
  "analysis_id": "123456789",
  "trust_score": 67,
  "risk_level": "MEDIUM",
  "summary": "This article presents...",
  "reflection_loop": {
    "approved": true,
    "iteration": 2,
    "total_iterations": 3
  }
}

// Or fallback if rejected 3x
{
  "type": "ANALYSIS_FALLBACK",
  "message": "After 3 attempts, could not generate satisfactory analysis...",
  "fallback": {
    "trust_score": 45,
    "risk_level": "HIGH",
    "summary": "Best attempt (iteration 3)"
  }
}
```

### **REST Endpoints**

#### **Health Check**
```
GET /health
```

Response:
```json
{
  "status": "healthy",
  "version": "2.0",
  "inference_engine": "Local ML Models",
  "ml_models": 4,
  "agents": 4,
  "timestamp": "2026-06-15T10:30:00Z"
}
```

#### **Models Info**
```
GET /api/v1/models
```

Response:
```json
{
  "models": [
    { "name": "Sentiment Analysis", "model": "distilbert-base-uncased-finetuned-sst-2-english", "accuracy": "95%" },
    { "name": "Bias Detection", "model": "facebook/bart-large-mnli", "accuracy": "93%" },
    ...
  ],
  "total_models": 4,
  "overall_accuracy": "91.5%"
}
```

---

## 🧠 ML Models & Analysis

### **1. Sentiment Analysis**

**API**: HuggingFace Inference API

**Model**: `distilbert-base-uncased-finetuned-sst-2-english`

**Output**: POSITIVE, NEGATIVE, NEUTRAL + confidence score

**Used in**: Trust score calculation (negative = -8, positive = -5 for sensationalism)

### **2. Toxicity Detection**

**API**: HuggingFace Inference API

**Model**: `unitary/toxic-bert`

**Detects**: Offensive, NSFW, profanity, hate speech

**Output**: 0-100 score

**Used in**: Bot authenticity, trust score penalties

### **3. Misinformation Classification**

**API**: HuggingFace Inference API

**Model**: `microsoft/deberta-large-mnli`

**Zero-shot prompt**: "Does this text contain misinformation?"

**Output**: 0-100% likelihood

**Used in**: Misinformation detector agent, trust score

### **4. Bias Detection**

**API**: HuggingFace Inference API

**Model**: `facebook/bart-large-mnli`

**Prompt**: "Is this text biased?"

**Output**: Bias confidence score

**Used with**: Pattern-based detection (keywords, ratios)

**Final score**: Average of 5 bias types (political, gender, religious, ideological, socioeconomic)

### **5. Entity Extraction**

**Method**: Regex patterns + keyword matching + frequency analysis

**Types**: COUNTRY, PERSON, ORGANIZATION, LOCATION

**Scoring**:
- Frequency (0-35): How many times mentioned
- Position (0-35): Earlier mentions weighted higher
- Type (0-30): PERSON > COUNTRY > LOCATION > ORG
- Context (0-10): Geopolitical keywords present

**Output**: Top 25 entities ranked by importance score

### **6. Propaganda Detection**

**Method**: Pattern matching for 7 techniques

1. **Loaded Language**: evil, corrupt, monsters, patriots, heroes
2. **Bandwagon**: everyone, all experts, widely accepted
3. **False Dilemma**: either/or, only option, must choose
4. **Appeal to Emotion**: shocking, devastating, outrageous
5. **Ad Hominem**: fool, idiot, stupid
6. **Red Herring**: anyway, by the way, aside from
7. **Glittering Generalities**: freedom, justice, truth, democracy

**Scoring**: Per-article frequency normalized to 0-100

### **7. Emotional Manipulation**

**Detects**:
- Negative emotional words (15+): war, attack, kill, death, terror
- Positive emotional words (10+): amazing, wonderful, perfect, victory
- Extremist language: always, never, everyone, must, definitely

**Scoring**: (negative×1.0 + positive×0.8 + extremist×0.7) / word_count × 40, capped at 75

### **8. Unverified Claims**

**Detects**:
- Unverified language: allegedly, reportedly, leaked, unconfirmed
- Significant claims: nuclear, weapons, ceasefire, peace deal, treaty

**Risk Calculation**:
```
If unverified_count > 0 AND claim_count > 2:
  risk = (unverified / claim_count) × 50 + claim_count × 5
If claims_present AND no_sources:
  risk += 20
```

---

## 🎨 Frontend Architecture

### **Page Structure**

#### **ProjectsPage.jsx**
- **Purpose**: Create new analysis projects
- **Features**:
  - Input form (URL or text)
  - Project list with status
  - Completed projects section
  - Delete project button
  - localStorage persistence
- **Flow**: Create → immediately navigate to AnalyzePage

#### **AnalyzePage.jsx**
- **Purpose**: Real-time analysis display
- **Features**:
  - 4 agent cards with progress bars
  - Real-time status updates via WebSocket
  - Entity display with scores
  - Risk assessment breakdown
  - Reflection loop status
  - Full report summary
- **WebSocket Integration**:
  - Connects on mount
  - Updates agent progress as data arrives
  - Shows iteration count + quality feedback
  - Displays final summary when approved

### **Component Hierarchy**

```
App.jsx
├── ProjectsPage
│   ├── ProjectForm (input)
│   ├── ProjectList (active)
│   └── CompletedList
│
└── AnalyzePage
    ├── AgentCard (×4)
    │   ├── ProgressBar
    │   ├── StatusText
    │   └── AgentDetails
    ├── ReflectionLoop
    │   ├── IterationCount
    │   ├── ApprovalStatus
    │   └── FeedbackList
    ├── RiskAssessment
    │   ├── TrustScoreGauge
    │   ├── RiskBreakdown
    │   └── EntityList
    └── FullReport
        ├── Summary
        └── RecommendationSection
```

### **Styling**

- **Framework**: Tailwind CSS
- **Theme**: Dark (bg-gray-900, text-white)
- **Accent Colors**:
  - Blue: Content Analyzer
  - Purple: Bias Detector
  - Pink: Bot Detector
  - Red: Misinformation
- **Responsive**: Mobile-first design
- **Animations**: Smooth transitions + progress bars

### **State Management**

```javascript
// AnalyzePage state
const [project, setProject] = useState(null)          // Current project
const [agents, setAgents] = useState({                // Agent data
  content_analyzer: { status: "pending", data: null },
  bias_detector: { status: "pending", data: null },
  bot_detector: { status: "pending", data: null },
  misinformation_detector: { status: "pending", data: null }
})
const [reflection, setReflection] = useState({        // Synthesis/review status
  iteration: 0,
  approved: false,
  quality_score: 0,
  feedback: []
})
const [report, setReport] = useState(null)            // Final report
```

### **WebSocket Handler**

```javascript
useEffect(() => {
  const ws = new WebSocket(`${REACT_APP_WS_URL}/ws/analyze/${projectId}`)
  
  ws.onopen = () => {
    ws.send(JSON.stringify({
      url: project.url,
      content: project.fullContent,
      title: project.title
    }))
  }
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    
    switch(data.type) {
      case "AGENT_START":
        setAgents(prev => ({
          ...prev,
          [data.agent]: { status: "processing", data: null }
        }))
        break
      
      case "AGENT_COMPLETE":
        setAgents(prev => ({
          ...prev,
          [data.agent]: { status: "completed", data: data.data }
        }))
        break
      
      case "REFLECTION_ITERATION":
        setReflection(prev => ({
          ...prev,
          iteration: data.iteration
        }))
        break
      
      case "REFLECTION_REVIEW":
        setReflection(prev => ({
          ...prev,
          approved: data.approved,
          quality_score: data.quality_score,
          feedback: data.feedback
        }))
        break
      
      case "ANALYSIS_COMPLETE":
        setReport({
          trust_score: data.trust_score,
          risk_level: data.risk_level,
          summary: data.summary
        })
        break
      
      case "ANALYSIS_FALLBACK":
        setReport({
          trust_score: data.fallback.trust_score,
          risk_level: data.fallback.risk_level,
          summary: data.message + "\n\n" + data.fallback.summary
        })
        break
    }
  }
  
  return () => ws.close()
}, [projectId])
```

---

## 🔁 Reflection Loop & Quality Assurance

### **How It Works**

```
Synthesis Agent generates report
              ↓
Reviewer validates quality
              ↓
    Quality ≥ Threshold?
      ↙ YES      NO ↘
  Send Report  Retry? (Attempt N of 3)
                      ↓
            (Process repeats)
                      ↓
                  All 3 failed?
                  ↙ YES    NO ↘
            Fallback    Continue
            Message     attempt 4
```

### **Synthesis Agent**

**Inputs**: 4 agent findings + metrics

**Process**:
1. Extract key metrics (toxicity, sentiment, bias, bot prob, etc.)
2. Create LLM prompt with context
3. Request natural language summary
4. LLM generates 4-5 sentence assessment

**Prompt Template**:
```
You are an expert news analyst. Analyze metrics:
- Trust Score: 67/100
- Sentiment: NEGATIVE
- Toxicity: 61/100
- Bias: 15/100
- Propaganda detected: Yes
- Unverified claims: Moderate

Write 4-5 sentences explaining:
1. Overall credibility assessment
2. Key reasons for trust score
3. What article does well (if any)
4. Clear recommendations

Keep tone objective, use simple language, no percentages in main text.
```

### **Reviewer Agent**

**Validates**:
1. **Structure**: trust_score, risk_level, summary present?
2. **Consistency**: Does trust_score match risk_level?
3. **Quality**: Is summary coherent and actionable?
4. **Semantic**: Does explanation match the metrics?

**Scoring**: Returns quality_score (0.0-1.0)

**Thresholds**:
- Iteration 1: quality_score ≥ 0.75 → approve
- Iteration 2: quality_score ≥ 0.80 → approve
- Iteration 3: quality_score ≥ 0.85 → approve
- Iteration 4: Doesn't exist → fallback

**Feedback**: Provides specific issues for synthesis retry

### **Fallback Strategy**

If all 3 iterations rejected:

```json
{
  "type": "ANALYSIS_FALLBACK",
  "message": "After 3 review attempts, the system could not generate a fully satisfactory analysis. Please try with a different article.",
  "fallback": {
    "trust_score": 42,
    "risk_level": "HIGH",
    "summary": "[Best attempt from iteration 3]"
  }
}
```

---

## 🚀 Performance & Optimization

### **Speed**

- **Agent parallelization**: 4 agents run simultaneously (~8-12 sec total)
- **WebSocket streaming**: No waiting for all data, updates as they arrive
- **API-based inference**: Models hosted on HuggingFace servers
- **Groq API**: ~500ms for synthesis (vs 2-5s for OpenAI)

### **Memory**

- **Runtime**: ~150MB baseline, minimal per analysis
- **Optimization**: No local model loading, stateless agents

### **Scalability**

- **Current**: Single-user, tested locally
- **For production**:
  - Run backend on dedicated server
  - Use load balancer for multiple instances
  - Add Redis for session management
  - Database for analysis history
  - API rate limiting & caching
  - CDN for frontend delivery

---

## 🤝 Contributing

### **Adding New Analysis**

1. **Create Agent**:
   ```python
   class NewAnalyzerAgent:
       def __init__(self, llm, ml):
           self.llm = llm
           self.ml = ml
       
       async def analyze(self, text: str) -> dict:
           # Implement analysis
           return {"findings": {...}}
   ```

2. **Register in app.py**:
   ```python
   agents_list = [
       ("new_analyzer", new_analyzer_instance),
       ...
   ]
   ```

3. **Display on frontend**: Update AnalyzePage.jsx to render new agent card

### **Improving Models**

- Replace transformers with better models as needed
- Fine-tune on domain-specific data
- Add custom classifiers for specific tasks

### **Bug Fixes**

1. Identify issue with reproducible steps
2. Add logging to debug
3. Fix in minimal scope
4. Test with multiple articles
5. Submit PR with explanation

---

## 📞 Support

- **Issues**: Found a bug? Open an issue with details
- **Questions**: Check documentation first, then ask
- **Contributions**: Fork, implement, test, submit PR

---

## 📄 License

This project is created for educational and research purposes.

---

## 🙏 Acknowledgments

- **Groq** for free, fast LLM API
- **Hugging Face** for transformers library
- **FastAPI** for excellent web framework
- **React** community for frontend tools

---

**Last Updated**: June 15, 2026
**Version**: 2.0
**Status**: Active Development

---

Made with ❤️ for real news intelligence 🚀

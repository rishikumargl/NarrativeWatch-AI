# End-to-End System Test Guide

## Test Checklist

Complete this checklist to verify the entire NarrativeWatch AI system is working correctly from URL input to final summary.

---

## PHASE 1: System Health Check

### 1.1 Backend Health Check
```bash
# Test command
curl http://localhost:8000/health

# Expected Response:
{
  "status": "healthy",
  "version": "2.0",
  "inference_engine": "HuggingFace Inference API",
  "accuracy": "90.25%",
  "ml_models": 7,
  "agents": 4,
  "timestamp": "2026-06-16T..."
}

Status: [  ] PASS / [  ] FAIL
```

### 1.2 Database Connection
```bash
# Backend should show in logs:
# ✅ Database connected

Status: [  ] PASS / [  ] FAIL
```

### 1.3 Frontend Access
```bash
# Test command
Visit http://localhost:3000

# Expected: Home page loads with dark theme
# Features visible: Projects, Analytics, Upload Docs buttons

Status: [  ] PASS / [  ] FAIL
```

---

## PHASE 2: Document Upload Test

### 2.1 Navigate to Document Upload
```
1. Go to http://localhost:3000/projects
2. Click "Upload Docs" button
3. DocumentUploadPage loads

Status: [  ] PASS / [  ] FAIL
```

### 2.2 Create Test Document
```
1. Create test.txt with sample news content
2. Drag file to upload area
3. File appears in document list
4. Click "Upload Documents"
5. Success message appears

Status: [  ] PASS / [  ] FAIL
```

### 2.3 Verify Document in Database
```bash
# Query database
psql narrativewatch_ai -c "SELECT COUNT(*) as total_documents FROM documents;"

# Expected: At least 1 document
# Should show: total_documents | 1+ (or more)

Status: [  ] PASS / [  ] FAIL
```

### 2.4 Check Document Statistics
```
1. Click "📊 Stats" button on DocumentUploadPage
2. Alert shows statistics
3. Verify: total_documents > 0

Status: [  ] PASS / [  ] FAIL
```

---

## PHASE 3: URL Input Flow Test

### 3.1 Create New Analysis Project
```
1. Go to http://localhost:3000/projects
2. Click "New Project" button
3. Select "URL" type
4. Enter test URL (e.g., https://www.bbc.com/news)
5. Click "Create" or "Analyze"

Status: [  ] PASS / [  ] FAIL
```

### 3.2 Verify WebSocket Connection
```
Browser Console should show:
- WebSocket connection established
- Real-time status messages arriving

Check for stages in order:
[ ] STAGE 1: Extracting article data...
[ ] STAGE 2: Retrieving historical context...
[ ] STAGE 3: Combining context from all sources...
[ ] STAGE 4: Running 4 specialized agents...
[ ] AGENT_START: content_analyzer
[ ] AGENT_START: bias_detector
[ ] AGENT_START: bot_detector
[ ] AGENT_START: misinformation_detector

Status: [  ] PASS / [  ] FAIL
```

---

## PHASE 4: 4-Stage Pipeline Test

### 4.1 Stage 1: URL Data Extraction
```
Backend logs should show:
✅ [OK] URLDataExtractor
✅ Extracted: [title] | [X] chars | [Y] entities | from [domain]

Expected:
- Title extracted
- Content extracted
- Entities identified
- Source domain identified

Status: [  ] PASS / [  ] FAIL
```

### 4.2 Stage 2A: RAG Context Retrieval
```
Backend logs should show:
✅ RAG context retrieved: [X] items
- Entity reputation (90-day lookback)
- Source baseline (180-day lookback)
- Similar articles found

Expected:
- Entity reputation data returned
- Source baseline scores returned
- Similar articles identified or empty list

Status: [  ] PASS / [  ] FAIL
```

### 4.3 Stage 2B: News API Verification
```
Backend logs should show:
✅ News API verification complete: [X] sources found

Expected:
- Verification score calculated
- Matching sources found or empty
- Non-blocking (failure doesn't stop analysis)

Status: [  ] PASS / [  ] FAIL
```

### 4.4 Stage 3: Context Combination
```
Backend logs should show:
✅ Context combined: [X] entities | [Y] corroborating sources | [Z] similar articles

Expected:
- All data sources merged
- Context bundle created
- Enriched context ready for agents

Status: [  ] PASS / [  ] FAIL
```

### 4.5 Stage 4: Agent Execution (Parallel)
```
Frontend shows agents completing:
[ ] content_analyzer - completed
[ ] bias_detector - completed
[ ] bot_detector - completed
[ ] misinformation_detector - completed

Backend logs show:
✅ Agent [name] completed with context

Expected:
- All 4 agents receive context parameter
- All complete successfully
- Results include enriched findings

Status: [  ] PASS / [  ] FAIL
```

---

## PHASE 5: AI Models Test

### 5.1 Content Analyzer (HuggingFace)
```
Result should include:
- sentiment (label + score)
- toxicity (0-100)
- entities (extracted + scored)
- propaganda score

Status: [  ] PASS / [  ] FAIL
```

### 5.2 Bias Detector (HuggingFace)
```
Result should include:
- bias scores for 5 types (0-100 each)
- overall bias percentage
- uses source baseline from context

Status: [  ] PASS / [  ] FAIL
```

### 5.3 Bot Detector (HuggingFace)
```
Result should include:
- bot probability
- authenticity score
- patterns detected

Status: [  ] PASS / [  ] FAIL
```

### 5.4 Misinformation Detector (HuggingFace)
```
Result should include:
- misinformation risk score
- propaganda techniques
- claims analysis
- uses corroboration from context

Status: [  ] PASS / [  ] FAIL
```

---

## PHASE 6: Synthesis & Review Loop

### 6.1 Synthesis Agent (Mistral)
```
Result should include:
- trust_score (10-100)
- validation_score (0-100)
- combined_trust_score (70% model + 30% validation)
- comprehensive summary
- risk_level (LOW/MEDIUM/HIGH/CRITICAL)

Expected:
- Takes all agent findings
- Generates 10-12 sentence summary
- Calculates dynamic trust score
- Uses enriched context

Status: [  ] PASS / [  ] FAIL
```

### 6.2 Reviewer Agent (Llama)
```
Result should include:
- approved (true/false)
- quality_score (0.0-1.0)
- feedback (list of issues if rejected)

Iteration 1: threshold >= 0.55
Iteration 2: threshold >= 0.63
Iteration 3: threshold >= 0.70

Expected:
- Quality validation
- Iteration-aware feedback
- Escalating thresholds

Status: [  ] PASS / [  ] FAIL
```

### 6.3 Reflection Loop
```
Frontend shows:
[ ] REFLECTION_ITERATION 1 - approve or retry
[ ] REFLECTION_ITERATION 2 - approve or retry (if needed)
[ ] REFLECTION_ITERATION 3 - final attempt

Expected:
- Analysis improves on retry
- Gets deeper/more detailed
- Eventually approved (iteration 1-3)

Status: [  ] PASS / [  ] FAIL
```

---

## PHASE 7: Database Integration

### 7.1 Analysis Saved to Database
```bash
# Query command
psql narrativewatch_ai -c "
SELECT COUNT(*) as total_analyses FROM news_article_analyses;
"

Expected:
- total_analyses | 1+ (new analysis added)

Status: [  ] PASS / [  ] FAIL
```

### 7.2 All Fields Populated
```bash
# Query command
psql narrativewatch_ai -c "
SELECT 
  article_title,
  trust_score,
  overall_bias_score,
  risk_level,
  full_report_summary,
  reviewer_approved
FROM news_article_analyses 
ORDER BY analysis_timestamp DESC 
LIMIT 1;
"

Expected:
- article_title: [extracted title]
- trust_score: [10-100]
- overall_bias_score: [0-100]
- risk_level: [LOW/MEDIUM/HIGH/CRITICAL]
- full_report_summary: [non-empty text]
- reviewer_approved: [1 = yes, 0 = no]

Status: [  ] PASS / [  ] FAIL
```

### 7.3 Vector Embeddings Stored
```bash
# Query command
psql narrativewatch_ai -c "
SELECT COUNT(*) as with_embeddings 
FROM news_article_analyses 
WHERE content_embedding IS NOT NULL;
"

Expected:
- with_embeddings: [1+] (embeddings generated)

Status: [  ] PASS / [  ] FAIL
```

---

## PHASE 8: Results Display

### 8.1 Results Page Loads
```
Expected on ResultsPage:
- Trust score gauge displayed
- Risk level badge shown
- Summary text visible
- All metrics displayed
- Sources listed

Status: [  ] PASS / [  ] FAIL
```

### 8.2 Analytics Dashboard Updates
```
1. Go to http://localhost:3000/analytics
2. Check statistics updated

Expected:
- Total articles increased
- Average trust score updated
- Charts showing new data
- Historical trend updated

Status: [  ] PASS / [  ] FAIL
```

### 8.3 History Page Shows New Analysis
```
1. Go to http://localhost:3000/history
2. Look for latest analysis

Expected:
- New analysis appears in history
- Shows title, trust score, risk level
- Clickable to view full results

Status: [  ] PASS / [  ] FAIL
```

---

## PHASE 9: API Endpoint Verification

### 9.1 GET /api/v1/health
```bash
curl http://localhost:8000/health

Expected: 200 OK with system status

Status: [  ] PASS / [  ] FAIL
```

### 9.2 GET /api/v1/history
```bash
curl http://localhost:8000/api/v1/history?limit=10

Expected: 200 OK with recent analyses

Status: [  ] PASS / [  ] FAIL
```

### 9.3 GET /api/v1/analysis/{id}
```bash
curl http://localhost:8000/api/v1/analysis/{last_id}

Expected: 200 OK with full analysis details

Status: [  ] PASS / [  ] FAIL
```

### 9.4 GET /api/v1/analytics/dashboard
```bash
curl http://localhost:8000/api/v1/analytics/dashboard

Expected: 200 OK with summary metrics

Status: [  ] PASS / [  ] FAIL
```

### 9.5 POST /api/v1/documents/upload
```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Doc",
    "content": "Test content",
    "source_url": "test://example",
    "source_domain": "example.com"
  }'

Expected: 200 OK with document_id

Status: [  ] PASS / [  ] FAIL
```

### 9.6 GET /api/v1/documents/stats
```bash
curl http://localhost:8000/api/v1/documents/stats

Expected: 200 OK with document statistics

Status: [  ] PASS / [  ] FAIL
```

---

## PHASE 10: Error Handling & Graceful Degradation

### 10.1 Invalid URL Input
```
Submit: "not-a-valid-url"

Expected:
- Error message displayed
- No crash
- System remains operational

Status: [  ] PASS / [  ] FAIL
```

### 10.2 Missing API Keys
```
With disabled/missing Mistral API:

Expected:
- Fallback to Groq (if enabled)
- Or show graceful error
- Analysis doesn't crash

Status: [  ] PASS / [  ] FAIL
```

### 10.3 Database Unavailable
```
If PostgreSQL down temporarily:

Expected:
- Analysis still runs with in-memory data
- Results displayed to user
- Warning in logs but no crash
- Non-blocking failure

Status: [  ] PASS / [  ] FAIL
```

---

## PHASE 11: Performance Metrics

### 11.1 Total Analysis Time
```
From URL input to results display:
Target: 30-40 seconds for full analysis

Measured time: _____ seconds

Status: [  ] PASS (< 45s) / [  ] FAIL (> 45s)
```

### 11.2 Stage 1: URL Extraction
Target: 2-5 seconds
Measured: _____ seconds
Status: [  ] PASS / [  ] FAIL

### 11.3 Stage 2: Context Retrieval
Target: 2-3 seconds (parallel)
Measured: _____ seconds
Status: [  ] PASS / [  ] FAIL

### 11.4 Stage 4: Agent Execution
Target: 3-5 seconds (parallel)
Measured: _____ seconds
Status: [  ] PASS / [  ] FAIL

### 11.5 Synthesis & Review
Target: 3-8 seconds (1-3 iterations)
Measured: _____ seconds
Status: [  ] PASS / [  ] FAIL

---

## PHASE 12: Data Flow Verification

### 12.1 Context Passed to Agents
```
Check backend logs for:
Agent content_analyzer receiving context=enriched_context
Agent bias_detector receiving context=enriched_context
Agent bot_detector receiving context=enriched_context
Agent misinformation_detector receiving context=enriched_context

Status: [  ] PASS / [  ] FAIL
```

### 12.2 RAG Data Used in Analysis
```
Verify agents improved due to context:
- Entity reputation affected credibility scoring
- Source baseline affected bias thresholds
- Similar articles affected authenticity assessment
- Corroboration affected misinformation scoring

Status: [  ] PASS / [  ] FAIL
```

### 12.3 Complete Data Flow
```
Trace data flow:
URL Input
  ↓ (extracted via URLDataExtractor)
Document Data
  ↓ (enriched via RAGContextService + News APIs)
Enriched Context Bundle
  ↓ (passed to all agents)
Agent Findings
  ↓ (synthesized by Mistral)
Synthesis Report
  ↓ (reviewed by Llama)
Final Results
  ↓ (saved to database)
Analysis Record

Status: [  ] PASS / [  ] FAIL
```

---

## FINAL SUMMARY

### Overall Test Results:
- Phase 1 (Health Check): [  ] PASS / [  ] FAIL
- Phase 2 (Document Upload): [  ] PASS / [  ] FAIL
- Phase 3 (URL Input): [  ] PASS / [  ] FAIL
- Phase 4 (4-Stage Pipeline): [  ] PASS / [  ] FAIL
- Phase 5 (AI Models): [  ] PASS / [  ] FAIL
- Phase 6 (Synthesis & Review): [  ] PASS / [  ] FAIL
- Phase 7 (Database): [  ] PASS / [  ] FAIL
- Phase 8 (Results Display): [  ] PASS / [  ] FAIL
- Phase 9 (APIs): [  ] PASS / [  ] FAIL
- Phase 10 (Error Handling): [  ] PASS / [  ] FAIL
- Phase 11 (Performance): [  ] PASS / [  ] FAIL
- Phase 12 (Data Flow): [  ] PASS / [  ] FAIL

### Total Phases Passed: ___ / 12

### Issues Found:
1. ________________
2. ________________
3. ________________

### Ready for Production: [  ] YES / [  ] NO

---

## Test Run Log

**Date**: ___________
**Tester**: ___________
**Test Duration**: ___________
**System Version**: 2.2 (RAG + Document Upload)

**Notes**:
```
[Insert any observations here]
```

**Sign-off**: ___________

---

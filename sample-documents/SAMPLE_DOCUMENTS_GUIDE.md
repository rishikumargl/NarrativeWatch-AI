# Sample Documents for NarrativeWatch AI Testing

## Overview
This directory contains 5 sample documents covering major trending news topics from June 2026. These documents are designed to test the NarrativeWatch AI RAG system, document upload functionality, and analysis pipeline.

## Sample Documents

### 1. AI-Breakthrough-2026.txt
**Topic:** Healthcare AI and Machine Learning
**Key Themes:** 
- AI diagnosis accuracy (94% cancer detection)
- Healthcare transformation
- Medical professional concerns
- Regulatory framework development
- Economic opportunity ($100B market by 2030)

**Use Case:** Test sentiment analysis, entity extraction (medical organizations, doctors, companies)
**Relevant Entities:** OpenAI, DeepMind, Stanford, Johns Hopkins, WHO, FDA

### 2. Climate-Summit-2026.txt
**Topic:** Global Climate Action and Commitments
**Key Themes:**
- Carbon neutrality targets (195 nations)
- Climate financing ($500B annually)
- Corporate commitments
- Implementation challenges
- Environmental monitoring

**Use Case:** Test bias detection (climate activism vs. industry skepticism), misinformation detection for climate claims
**Relevant Entities:** UN, Greta Thunberg, Microsoft, Apple, Google, developing nations

### 3. Election-2026-Analysis.txt
**Topic:** Political Elections and Voter Priorities
**Key Themes:**
- Economic concerns dominate (38% of voters)
- Healthcare access and costs (27%)
- Election integrity
- Youth voter engagement
- Strategic messaging

**Use Case:** Test for political bias, partisan language analysis, misinformation about election fraud
**Relevant Entities:** Political parties, election officials, demographic groups, countries

### 4. Crypto-Regulation-2026.txt
**Topic:** Cryptocurrency and Financial Regulation
**Key Themes:**
- Global regulatory framework adoption
- Institutional adoption acceleration
- Environmental concerns (mining carbon footprint)
- Market reactions
- Crypto industry responses

**Use Case:** Test entity reputation tracking (crypto exchanges, banks, regulators), sentiment shifts based on regulation news
**Relevant Entities:** Coinbase, Kraken, JPMorgan, Goldman Sachs, G20, ECB, Federal Reserve

### 5. Space-Exploration-2026.txt
**Topic:** Commercial Space Industry Milestone
**Key Themes:**
- First private lunar colony
- Scientific discoveries
- Space governance questions
- Competition among space companies
- Economic opportunities

**Use Case:** Test positive bias toward commercial achievement, balanced coverage of environmental concerns
**Relevant Entities:** SpaceX, NASA, Blue Origin, Axiom Space, Space agencies

### 6. Pandemic-Preparedness-2026.txt
**Topic:** Global Health Emergency Preparedness
**Key Themes:**
- WHO pandemic framework
- Vaccine equity and access
- International cooperation
- Supply chain resilience
- Mental health impacts

**Use Case:** Test analysis of health policy, equity concerns, international coordination complexity
**Relevant Entities:** WHO, CDC, national governments, pharmaceutical companies, developing nations

### 7. Education-Tech-2026.txt
**Topic:** Artificial Intelligence in Education
**Key Themes:**
- AI tutoring systems in 65% of schools
- Learning improvements (18-22% test score gains)
- Teacher role transformation
- Equity and access concerns
- Privacy and data protection

**Use Case:** Test analysis of technology disruption, equity concerns, job displacement discussion
**Relevant Entities:** UNESCO, Stanford, Coursera, Duolingo, Khan Academy, AFT (teachers union)

## How to Use These Documents

### Option 1: Manual Upload via UI
1. Navigate to http://localhost:3000/documents
2. Drag and drop documents or click to select
3. Edit titles if desired
4. Click "Upload Document(s)"
5. View statistics showing ingested documents

### Option 2: Batch API Upload
```bash
curl -X POST http://localhost:8000/api/v1/documents/upload-batch \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      {"title": "AI Breakthrough", "content": "...", "source_domain": "techcrunch.com"},
      {"title": "Climate Summit", "content": "...", "source_domain": "un.org"}
    ]
  }'
```

### Option 3: Single Document Upload
```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -H "Content-Type: application/json" \
  -d '{
    "title": "AI Breakthrough in Healthcare",
    "content": "AI Breakthroughs in 2026...",
    "source_domain": "techcrunch.com",
    "source_url": "https://techcrunch.com/ai-breakthrough"
  }'
```

## Testing RAG System Integration

After uploading documents, test how they enhance analysis:

### Test 1: Analyze Article About AI Healthcare
1. Go to Projects page
2. Submit a URL about AI diagnostics
3. Watch Stage 2: RAG Context Retrieval
4. Verify that entity reputation for "OpenAI", "DeepMind", etc. is retrieved
5. Check ResultsPage to see if RAG context enhanced analysis

### Test 2: Analyze Article About Climate Policy
1. Submit a URL about climate commitments
2. Verify RAG retrieves similar articles from uploaded documents
3. Check if source baseline for climate organizations is used
4. Analyze if bias detection is enhanced by historical context

### Test 3: Batch Analysis With Different Topics
1. Submit 5 different URLs from the sample topics
2. Observe how RAG context retrieves relevant documents
3. Compare analyses—do they reference uploaded document context?
4. Check analytics dashboard for trending topics

## Document Coverage Matrix

| Topic | Agents Tested | Features Tested |
|-------|---------------|-----------------|
| AI Healthcare | All 4 | Entity reputation, sentiment |
| Climate | All 4 | Bias detection, opposing views |
| Elections | All 4 | Political bias, misinformation |
| Crypto | All 4 | Market sentiment, regulation tracking |
| Space | All 4 | Positive bias, entity extraction |
| Health/Pandemic | All 4 | International coordination, equity |
| EdTech | All 4 | Disruption analysis, concerns |

## Expected RAG System Behavior

### Entity Reputation Examples
```
After uploading documents:
- "OpenAI" mention_count: 5, avg_trust: 0.78
- "WHO" mention_count: 8, avg_bias: -0.15
- "Greta Thunberg" mention_count: 2, avg_trust: 0.85
```

### Source Baseline Examples
```
- techcrunch.com: avg_trust_score: 0.72, risk_level: low
- un.org: avg_trust_score: 0.88, risk_level: very_low
- crypto_blog.com: avg_trust_score: 0.45, risk_level: medium
```

### Similar Article Retrieval
```
When analyzing new article about AI:
- Retrieved: AI-Breakthrough-2026.txt (0.87 similarity)
- Retrieved: Education-Tech-2026.txt (0.62 similarity)
- Used for: Entity context, bias baseline
```

## Verification Checklist

After uploading and testing:
- [ ] All 7 documents uploaded successfully
- [ ] Document statistics show 7 documents ingested
- [ ] Vector embeddings generated (pgvector)
- [ ] Entity reputation populated in database
- [ ] Source baseline calculated for domains
- [ ] Semantic search retrieves relevant documents
- [ ] RAG context enhances agent analysis
- [ ] Analyses reference historical data
- [ ] Analytics updated with new documents

## Performance Notes

- First upload: 5-10s per document (embedding generation)
- Subsequent uploads: <1s each (batch)
- RAG context retrieval: 500-1000ms per analysis
- Semantic search: <100ms for similarity matching
- Total analysis time: 30-40s (includes all stages)

## Next Steps

1. Upload all 7 sample documents
2. Analyze 5-10 different news articles
3. Check analytics dashboard
4. Verify RAG context is being used
5. Compare analyses with and without RAG
6. Monitor database for new embeddings
7. Test batch upload performance
8. Validate semantic search accuracy

---

**Document Count:** 7 trending news articles  
**Total Content:** ~8,500 words  
**Topics Covered:** 7 major categories  
**Ready for Testing:** Yes ✅

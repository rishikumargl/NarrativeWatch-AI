# NarrativeWatch AI - API Reference

Complete API documentation for NarrativeWatch AI.

## Base URL

```
http://localhost:8000
http://api.example.com (production)
```

## Authentication

Currently no authentication required. Production deployments should implement JWT or OAuth2.

## Status Codes

- `200 OK` - Successful request
- `400 Bad Request` - Invalid input
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - Temporary maintenance

---

## Endpoints

### 1. Health Check

**Get API Status**

```http
GET /health
```

**Response (200):**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-06-12T10:30:00Z"
}
```

---

### 2. Analyze Instagram Page/Post

**Analyze content for misinformation, bias, and campaigns**

```http
POST /api/v1/analyze
Content-Type: application/json

{
  "instagram_url": "https://www.instagram.com/bbcnews/",
  "analysis_type": "page",
  "include_historical": true,
  "include_bot_analysis": true,
  "include_bias_detection": true,
  "include_campaign_detection": true
}
```

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `instagram_url` | string | Yes | Full Instagram URL (https://instagram.com/username/) |
| `analysis_type` | string | Yes | Type: `page`, `post`, or `account` |
| `include_historical` | boolean | No | Include historical data (default: true) |
| `include_bot_analysis` | boolean | No | Analyze bot activity (default: true) |
| `include_bias_detection` | boolean | No | Detect bias (default: true) |
| `include_campaign_detection` | boolean | No | Detect campaigns (default: true) |

**Response (200):**
```json
{
  "request_id": "req_20260612103000_a1b2c3d4",
  "instagram_url": "https://www.instagram.com/bbcnews/",
  "analysis_type": "page",
  "timestamp": "2026-06-12T10:30:00Z",
  "trust_score": 72.5,
  "risk_level": "medium",
  "findings": [
    {
      "agent_name": "Content Analyzer",
      "category": "emotional_manipulation",
      "severity": "medium",
      "description": "Detected use of emotional language in 35% of posts",
      "evidence": [
        "High exclamation marks (avg 2.3 per post)",
        "Urgency indicators found in 30% of captions"
      ],
      "confidence": 0.87
    }
  ],
  "summary": "Page shows moderate manipulation tactics with some political bias.",
  "recommendations": [
    "Cross-verify major claims with fact-checkers",
    "Monitor for changes in posting frequency"
  ],
  "metadata": {
    "processing_time_seconds": 8.432,
    "agents_executed": 8,
    "data_sources_queried": 12,
    "reflection_loop_iterations": 1
  }
}
```

**Error Response (400):**
```json
{
  "error": "validation_error",
  "detail": "Invalid Instagram URL",
  "timestamp": "2026-06-12T10:30:00Z"
}
```

**Example Requests:**

```bash
# Using cURL
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "instagram_url": "https://www.instagram.com/bbcnews/",
    "analysis_type": "page"
  }'

# Using Python
import requests

response = requests.post(
    'http://localhost:8000/api/v1/analyze',
    json={
        'instagram_url': 'https://www.instagram.com/bbcnews/',
        'analysis_type': 'page'
    }
)
print(response.json())

# Using JavaScript
const response = await fetch('http://localhost:8000/api/v1/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    instagram_url: 'https://www.instagram.com/bbcnews/',
    analysis_type: 'page'
  })
});
const data = await response.json();
```

---

### 3. Get Analysis Result (Cached)

**Retrieve previously completed analysis**

```http
GET /api/v1/results/{request_id}
```

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `request_id` | string | Yes | Request ID from initial analysis |

**Response (200):**
Same as analyze endpoint response.

**Error Response (404):**
```json
{
  "error": "not_found",
  "detail": "Analysis result not found",
  "timestamp": "2026-06-12T10:30:00Z"
}
```

---

## Data Models

### Request Models

#### AnalysisRequest
```python
{
  "instagram_url": string,          # Required
  "analysis_type": enum,             # Required: "page" | "post" | "account"
  "include_historical": boolean,     # Optional, default: true
  "include_bot_analysis": boolean,   # Optional, default: true
  "include_bias_detection": boolean, # Optional, default: true
  "include_campaign_detection": boolean  # Optional, default: true
}
```

### Response Models

#### AnalysisResponse
```python
{
  "request_id": string,              # Unique request identifier
  "instagram_url": string,           # URL analyzed
  "analysis_type": string,           # Type of analysis performed
  "timestamp": datetime,             # When analysis was completed
  "trust_score": float,              # 0-100 score
  "risk_level": enum,                # "low" | "medium" | "high" | "critical"
  "findings": [FindingDetail],       # Array of findings
  "summary": string,                 # Brief summary
  "recommendations": [string],       # Array of recommendations
  "metadata": object                 # Additional analysis metadata
}
```

#### FindingDetail
```python
{
  "agent_name": string,              # Name of agent that found this
  "category": string,                # Finding category
  "severity": enum,                  # "low" | "medium" | "high" | "critical"
  "description": string,             # Detailed description
  "evidence": [string],              # Supporting evidence
  "confidence": float                # 0-1 confidence score
}
```

#### ErrorResponse
```python
{
  "error": string,                   # Error type
  "detail": string,                  # Error message
  "request_id": string | null,       # Associated request ID
  "timestamp": datetime              # When error occurred
}
```

---

## Risk Levels Explained

| Level | Score | Description |
|-------|-------|-------------|
| **Low** | 80-100 | Page appears trustworthy with minimal risk indicators |
| **Medium** | 60-79 | Some manipulation or bias detected, requires verification |
| **High** | 40-59 | Significant risk factors, likely containing misinformation |
| **Critical** | 0-39 | Highly suspicious content, likely coordinated disinformation |

---

## Agent Findings

### Content Analyzer
Detects emotional manipulation, narrative themes, engagement patterns.

**Categories:**
- `emotional_manipulation` - Excessive emotional language
- `urgency_tactics` - Time-pressure tactics
- `fear_mongering` - Fear-based messaging
- `hashtag_manipulation` - Suspicious hashtag patterns
- `frequency_anomaly` - Unusual posting patterns

### Bias Detector
Identifies political, gender, and ideological biases.

**Categories:**
- `political_bias` - Political leaning
- `gender_bias` - Gender representation
- `ideological_bias` - Ideological slant
- `source_credibility` - Source reliability
- `language_toxicity` - Toxic language patterns

### Bot Detector
Analyzes engagement for artificial activity.

**Categories:**
- `bot_activity` - Detected bot engagement
- `like_velocity_anomaly` - Unusual like patterns
- `follower_growth_anomaly` - Suspicious growth
- `comment_authenticity` - Inauthentic comments
- `coordinated_engagement` - Coordinated activity

### Campaign Detector
Identifies organized influence campaigns.

**Categories:**
- `coordinated_campaign` - Coordinated campaign detected
- `cross_page_correlation` - Related pages detected
- `narrative_similarity` - Similar narratives
- `timing_correlation` - Synchronized posting

---

## Rate Limiting

**Production limits (per IP):**
- 100 requests/minute
- 1000 requests/hour
- 10000 requests/day

Contact support for higher limits.

---

## Error Handling

### Common Errors

**400 Bad Request**
```json
{
  "error": "validation_error",
  "detail": "Invalid Instagram URL",
  "timestamp": "2026-06-12T10:30:00Z"
}
```

**500 Internal Server Error**
```json
{
  "error": "internal_server_error",
  "detail": "An unexpected error occurred",
  "request_id": "req_20260612103000_a1b2c3d4",
  "timestamp": "2026-06-12T10:30:00Z"
}
```

### Retry Strategy

For 5xx errors, implement exponential backoff:

```python
import time
import requests

def analyze_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.post(
                'http://localhost:8000/api/v1/analyze',
                json={'instagram_url': url}
            )
            if response.status_code == 200:
                return response.json()
            elif response.status_code >= 500:
                # Retry on server errors
                wait_time = 2 ** attempt
                print(f"Retry attempt {attempt + 1} after {wait_time}s")
                time.sleep(wait_time)
            else:
                # Don't retry on client errors
                response.raise_for_status()
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)
```

---

## Pagination (Future)

When batch analysis is implemented:

```http
GET /api/v1/results?page=1&limit=20&sort=timestamp
```

---

## WebSocket Support (Future)

Real-time analysis updates via WebSocket:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/analyze');
ws.send(JSON.stringify({
  instagram_url: 'https://instagram.com/bbcnews/',
  analysis_type: 'page'
}));
ws.onmessage = (event) => {
  console.log('Update:', event.data);
};
```

---

## Interactive Documentation

- **Swagger UI:** `http://localhost:8000/api/docs`
- **ReDoc:** `http://localhost:8000/redoc` (future)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-06-12 | Initial release with core analysis endpoints |

---

## Support & Issues

- Report bugs: GitHub Issues
- Suggest features: GitHub Discussions
- Documentation: [SETUP_GUIDE.md](./SETUP_GUIDE.md)

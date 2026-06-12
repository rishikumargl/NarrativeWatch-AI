# Twitter API Setup Guide for NarrativeWatch AI

**Platform Changed From Instagram to Twitter** ✅

This guide explains how to set up Twitter API credentials for NarrativeWatch AI.

---

## Why Twitter?

- ✅ No API approval needed (tweepy supports both official and community methods)
- ✅ Rich data: tweets, mentions, hashtags, engagement metrics
- ✅ Better for detecting misinformation, coordination, and bot activity
- ✅ Public data access available
- ✅ Already in your dependencies (`tweepy>=4.14.0`)

---

## Option 1: Twitter API v2 (Recommended) - Bearer Token

### Step 1: Create a Twitter Developer Account

1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Click "Sign up for the free plan"
3. Fill in your details and accept terms
4. Create a project (e.g., "NarrativeWatch AI")
5. Create an application within the project

### Step 2: Get Your Bearer Token

1. In the developer dashboard, go to your app
2. Navigate to "Keys and tokens"
3. Under "Bearer Token", click "Generate"
4. Copy the Bearer Token (starts with `AAAA`)
5. **Keep it safe** - don't share it

### Step 3: Add to .env

```env
# Twitter API v2
TWITTER_BEARER_TOKEN=AAAA...your_bearer_token_here
```

### What You Can Do With v2:

- ✅ Fetch user tweets (recent, limited to last 7 days)
- ✅ Search recent tweets
- ✅ Get user info and metrics
- ✅ Get engagement metrics
- ✅ Extract hashtags and mentions

**Free Tier Limits:**
- 300 requests per 15 minutes
- Search limited to last 7 days
- 15,000 Tweets per month

---

## Option 2: Twitter API v1.1 - OAuth 1.0a (Full Access)

For archived tweets and more features.

### Step 1: Create Twitter App

1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Create app (if not done already)
3. Go to "Keys and tokens" tab

### Step 2: Get OAuth Credentials

You need 4 tokens:

1. **API Key** (also called Consumer Key)
   - Click "Regenerate" next to "API Key"
   - Copy the key

2. **API Secret** (also called Consumer Secret)
   - Click "Regenerate" next to "API Secret"
   - Copy the secret

3. **Access Token**
   - Scroll down to "Authentication Tokens"
   - Click "Generate" under "Access Token & Secret"
   - Copy the Access Token

4. **Access Token Secret**
   - Copy the Access Token Secret from the same section

### Step 3: Add to .env

```env
# Twitter API v1.1 OAuth
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
```

---

## Option 3: Quick Setup (No API Needed) - Instagrapi for Scraping

If you just want to get started without official API:

```bash
pip install instagrapi tweepy
```

Then use instagrapi to fetch Twitter data without credentials. However, **we recommend Option 1 (Bearer Token)** as it's official and sustainable.

---

## Testing Your Setup

### Using Configuration Verification Script

```bash
python backend/verify_config.py
```

Expected output:
```
✅ TWITTER_BEARER_TOKEN....... tvly-dev-b...TpsYM
```

### Test in Python

```python
from src.integrations.twitter_client import TwitterClient

client = TwitterClient()

# Get a user
user = client.get_user_by_username("twitter")
print(f"Username: {user['username']}")
print(f"Followers: {user['followers_count']}")

# Get their tweets
tweets = client.get_user_tweets("twitter", max_results=5)
for tweet in tweets:
    print(f"Tweet: {tweet['text'][:100]}...")
```

---

## Updated API Endpoints

The application now uses Twitter instead of Instagram:

### Old Endpoints (Instagram) ❌
```
POST /analyze/page
POST /analyze/post
```

### New Endpoints (Twitter) ✅
```
POST /analyze/user
POST /analyze/tweet
```

### Example Requests

**Analyze a Twitter User:**
```bash
curl -X POST "http://localhost:8000/analyze/user" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "twitter",
    "include_tweets": true,
    "num_tweets": 20,
    "include_campaigns": true
  }'
```

**Analyze a Single Tweet:**
```bash
curl -X POST "http://localhost:8000/analyze/tweet" \
  -H "Content-Type: application/json" \
  -d '{
    "tweet_id": "1234567890123456789",
    "include_context": true,
    "check_campaigns": true
  }'
```

---

## What Data is Analyzed

For each tweet/user, the system analyzes:

### Text Analysis
- ✅ Emotional language (sentiment, tone, intensity)
- ✅ Narrative themes (conspiracy, propaganda, politics, etc.)
- ✅ Named entities (people, places, organizations)
- ✅ Readability metrics

### Network Analysis
- ✅ Hashtag patterns (frequency, categories)
- ✅ **Mention patterns** (who's being mentioned, influencer targeting)
- ✅ URL patterns and external references
- ✅ Tweet-level engagement

### User Analysis
- ✅ Posting patterns and frequency
- ✅ Engagement rate and quality
- ✅ Network effects and reach

### Detection
- ✅ Bias patterns
- ✅ Bot-like behavior
- ✅ Campaign coordination
- ✅ Misinformation signals

---

## Twitter-Specific Features

The analyzer extracts these from tweets:

### Hashtags
```python
client.extract_hashtags("#WeStandTogether #Democracy #News")
# Returns: ["#westandtogether", "#democracy", "#news"]
```

### Mentions
```python
client.extract_mentions("@twitter hello @POTUS check this")
# Returns: ["@twitter", "@POTUS"]
```

### Engagement Metrics
```
likes: 125
retweets: 43
replies: 12
quotes: 5
engagement_rate: 0.0185 (1.85%)
```

---

## Troubleshooting

### Error: "TWITTER_BEARER_TOKEN not found"
```
Solution: Add to .env file:
TWITTER_BEARER_TOKEN=your_token_here
```

### Error: "401 Unauthorized"
```
Solution: Your token is invalid or expired.
Go to Twitter Developer Portal and regenerate it.
```

### Error: "Rate limit exceeded"
```
Solution: You've hit API rate limits.
Free tier: 300 requests per 15 minutes
Wait 15 minutes or upgrade to higher tier.
```

### Getting "protected" tweets error
```
Solution: You only have access to public tweets.
The tweepy library automatically skips protected accounts.
```

---

## Environment Variable Reference

| Variable | Type | Required | Example |
|----------|------|----------|---------|
| `TWITTER_BEARER_TOKEN` | String | Option 1 | `AAAA...` |
| `TWITTER_API_KEY` | String | Option 2 | `abc123...` |
| `TWITTER_API_SECRET` | String | Option 2 | `xyz789...` |
| `TWITTER_ACCESS_TOKEN` | String | Option 2 | `123-abc...` |
| `TWITTER_ACCESS_TOKEN_SECRET` | String | Option 2 | `secret123...` |

**Choose either Option 1 OR Option 2, not both.**

---

## API Response Format

All Twitter analysis responses include:

```json
{
  "analysis_id": "uuid",
  "status": "completed",
  "trust_score": 65,
  "risk_level": "medium",
  "risk_flags": [
    {
      "flag": "bot_activity",
      "confidence": 0.78,
      "description": "Posting pattern matches bot signatures"
    }
  ],
  "summary": "User shows signs of coordinated activity with 3 similar accounts",
  "user_username": "example_user",
  "tweets_analyzed": 20,
  "detected_patterns": {
    "hashtags": {"#election": 5, "#election2024": 3},
    "mentions": {"@news": 2, "@politics": 1},
    "emotional_language": {"positive": 45, "negative": 25, "neutral": 30}
  }
}
```

---

## Getting Twitter Credentials - Step by Step

### Most Beginner-Friendly: Use Bearer Token

1. Visit https://developer.twitter.com/
2. Click "Create an app"
3. Fill in basic info:
   - App name: "NarrativeWatch"
   - Use case: "Academic research"
   - Description: "Analyzing social media narratives"
4. Check the box for "Yes, I am affiliated with an academic institution"
5. Accept terms
6. Go to "Keys and tokens"
7. Copy the "Bearer Token" starting with `AAAA`
8. Add to `.env`: `TWITTER_BEARER_TOKEN=AAAA...`

Done! ✅

---

## Next Steps

1. **Get Twitter API credentials** (choose Option 1 or 2 above)
2. **Add to `.env` file**
3. **Run verification**: `python backend/verify_config.py`
4. **Start backend**: `python -m uvicorn src.app:app --reload --port 8000`
5. **Test endpoints**:
   ```bash
   curl -X POST "http://localhost:8000/analyze/user" \
     -H "Content-Type: application/json" \
     -d '{"username": "twitter", "include_tweets": true, "num_tweets": 5}'
   ```

---

## Support

If you encounter issues:

1. Check `.env` file has correct token
2. Run `python backend/verify_config.py`
3. Check Twitter Developer Portal for rate limits
4. Review logs: `backend/logs/narrativewatch.log`

---

**Status: Ready to analyze Twitter! 🐦**

Your application is now configured to analyze Twitter users and tweets instead of Instagram.

All 9 agents are ready to detect narratives, coordination, bias, and misinformation on Twitter.

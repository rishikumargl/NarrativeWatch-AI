from src.llm.groq_client import groq_client
from src.services.cross_source_verification import cross_source_verification
import json
import logging
import hashlib

logger = logging.getLogger(__name__)

# In-memory cache for analysis results per URL
_analysis_cache = {}

class SynthesisAgent:
    """Combine all findings into coherent report"""

    def __init__(self, llm):
        self.llm = llm

    def _interpret_trust_score(self, score):
        """Interpret what a trust score means"""
        if score >= 80:
            return "Highly credible and reliable; minimal concerns"
        elif score >= 70:
            return "Credible with minor concerns; generally trustworthy"
        elif score >= 60:
            return "Moderately credible; some factual reporting with notable caveats"
        elif score >= 50:
            return "Mixed credibility; credible elements mixed with concerns"
        elif score >= 40:
            return "Below average credibility; significant concerns that readers should note"
        elif score >= 25:
            return "Low credibility; substantial issues with accuracy, bias, or sourcing"
        else:
            return "Very low credibility; serious red flags present"

    def _interpret_validation_score(self, score):
        """Interpret cross-source validation"""
        if score >= 80:
            return "Widely reported and verified by many reputable sources"
        elif score >= 60:
            return "Corroborated by multiple credible sources"
        elif score >= 40:
            return "Some corroboration from other sources, though not universal"
        elif score >= 20:
            return "Limited coverage elsewhere; mostly unique to this outlet"
        else:
            return "Not corroborated by other major sources; handle with caution"

    def _interpret_sentiment(self, sentiment):
        if sentiment == "NEGATIVE":
            return "The article uses negative language and framing, which may indicate serious/critical reporting or sensationalism depending on context"
        elif sentiment == "POSITIVE":
            return "The article emphasizes positive framing, which may indicate promotional content or bias toward favorable interpretation"
        else:
            return "The article maintains neutral tone without strong emotional language"

    def _interpret_toxicity(self, score, category):
        if category in ["sports", "war"]:
            return f"Toxicity score is {score:.0f}/100. For {category} reporting, some harsh language is normal and doesn't indicate poor journalism"
        elif score > 50:
            return f"Toxicity score is {score:.0f}/100 - contains significant offensive or NSFW language"
        elif score > 30:
            return f"Toxicity score is {score:.0f}/100 - contains some harsh language or strong accusations"
        else:
            return f"Toxicity score is {score:.0f}/100 - minimal offensive language; professionally written"

    def _interpret_bias(self, score):
        if score > 70:
            return "High bias detected - article heavily favors one perspective; reader should seek opposing viewpoints"
        elif score > 50:
            return "Moderate bias present - article shows clear lean but attempts to include other perspectives"
        elif score > 30:
            return "Mild bias detected - overall balanced but with noticeable slant"
        else:
            return "Low bias - article presents multiple viewpoints fairly"

    def _interpret_bot_probability(self, prob):
        if prob > 70:
            return f"High bot probability ({prob:.0f}%) - writing style suggests automated generation or unnatural phrasing"
        elif prob > 40:
            return f"Moderate bot indicators ({prob:.0f}%) - some repetitive patterns or unusual phrasing"
        else:
            return f"Low bot probability ({prob:.0f}%) - appears to be human-written"

    def _interpret_propaganda(self, score):
        if score > 70:
            return "Heavy propaganda techniques detected - article employs multiple manipulation methods"
        elif score > 50:
            return "Moderate propaganda techniques - some manipulative language and framing"
        elif score > 20:
            return "Mild propaganda elements - some persuasive techniques but not overwhelming"
        else:
            return "Minimal propaganda - straightforward reporting without obvious manipulation"

    def _interpret_emotional_manipulation(self, score, category):
        if category in ["entertainment", "sports"]:
            base = f"Emotional manipulation score is {score:.0f}/100. "
            if score > 70:
                return base + "Expected high emotion in this category, though intensity is notable"
            else:
                return base + "Normal emotional expression for this content type"
        else:
            if score > 60:
                return f"Strong emotional manipulation detected ({score:.0f}/100) - reader should be aware of the emotional framing"
            elif score > 30:
                return f"Moderate emotional language ({score:.0f}/100) - article tries to engage readers emotionally"
            else:
                return f"Minimal emotional manipulation ({score:.0f}/100) - factual presentation"

    def _interpret_unverified_risk(self, score):
        if score > 70:
            return "Many unverified claims - verify major assertions independently before accepting"
        elif score > 40:
            return "Some unverified claims present - key claims should be cross-checked"
        else:
            return "Most claims appear well-supported or directly attributed to sources"

    def detect_article_category(self, title: str, content: str, findings: dict) -> str:
        """Detect article category to adjust scoring penalties"""
        text = (title + " " + content).lower()

        # Define category keywords
        sports_keywords = ['sport', 'football', 'cricket', 'baseball', 'nfl', 'nba', 'player', 'team', 'match', 'game', 'injury', 'goal', 'score', 'championship', 'league', 'coach', 'athlete']
        war_keywords = ['war', 'conflict', 'military', 'attack', 'bomb', 'missile', 'army', 'soldier', 'battle', 'combat', 'siege', 'ceasefire', 'invasion', 'troops']
        entertainment_keywords = ['movie', 'celebrity', 'actor', 'singer', 'show', 'entertainment', 'drama', 'album', 'film', 'hollywood', 'bollywood', 'award', 'premiere']
        politics_keywords = ['election', 'politician', 'parliament', 'congress', 'senate', 'policy', 'government', 'minister', 'president', 'campaign', 'vote', 'bill', 'law']
        breaking_news_keywords = ['breaking', 'just in', 'developing', 'urgent', 'alert', 'happening now', 'latest']

        # Count keyword matches
        category_scores = {
            'sports': sum(1 for kw in sports_keywords if kw in text),
            'war': sum(1 for kw in war_keywords if kw in text),
            'entertainment': sum(1 for kw in entertainment_keywords if kw in text),
            'politics': sum(1 for kw in politics_keywords if kw in text),
            'breaking_news': sum(1 for kw in breaking_news_keywords if kw in text),
        }

        detected_category = max(category_scores, key=category_scores.get) if max(category_scores.values()) > 0 else 'general'
        logger.info(f"📁 Article category detected: {detected_category}")
        return detected_category

    def calculate_trust_score(self, findings: dict, article_category: str = 'general') -> int:
        """Calculate dynamic trust score (0-100) from real agent findings - reflects actual content quality"""

        # Higher baseline - good articles naturally score ~85+, bad ones drop linearly
        trust_score = 85  # Good baseline: legitimate news stays HIGH, penalties very light

        logger.info(f"📊 Calculating trust score from findings keys: {list(findings.keys())}")
        logger.info(f"📁 Using category-aware penalties for: {article_category}")

        # Content Analyzer findings with category-aware penalties
        content = findings.get("content_analyzer", {}).get("findings", {}).get("analysis", {})
        if content:
            logger.info(f"✅ Content Analyzer data found: {list(content.keys())}")

            # Penalize toxicity - MINIMAL
            toxicity = content.get("toxicity", {}).get("toxicity_score", 0)
            if toxicity > 0:
                # Adjust toxicity penalty by category - MINIMAL
                if article_category in ['sports', 'war', 'breaking_news']:
                    toxicity_weight = 0.05  # Almost no penalty (expected)
                elif article_category in ['entertainment']:
                    toxicity_weight = 0.06  # Minimal
                else:
                    toxicity_weight = 0.08  # Light for politics

                toxicity_penalty = int(toxicity * toxicity_weight)
                trust_score -= toxicity_penalty
                logger.info(f"   Toxicity penalty: -{toxicity_penalty} (score={toxicity}, weight={toxicity_weight}, category={article_category})")

            # Penalize misinformation - MINIMAL
            misinfo = content.get("misinformation", {}).get("misinformation_likelihood", 0)
            if misinfo > 0:
                misinfo_penalty = int(misinfo * 0.05)  # Minimal penalty
                trust_score -= misinfo_penalty
                logger.info(f"   Misinfo penalty: -{misinfo_penalty} (score={misinfo})")

            # Sentiment penalties - MINIMAL LINEAR
            sentiment = content.get("sentiment", {}).get("label", "NEUTRAL")
            if sentiment == "NEGATIVE":
                # Very light penalty for negative sentiment
                if article_category in ['war', 'breaking_news']:
                    logger.info(f"   Sentiment penalty: 0 (NEGATIVE but expected for {article_category})")
                elif article_category in ['entertainment', 'sports']:
                    trust_score -= 1  # Minimal penalty
                    logger.info(f"   Sentiment penalty: -1 (NEGATIVE in {article_category})")
                else:
                    trust_score -= 2  # Light penalty
                    logger.info(f"   Sentiment penalty: -2 (NEGATIVE in {article_category})")
            elif sentiment == "POSITIVE":
                # No penalty for positive sentiment (good news is OK)
                logger.info(f"   Sentiment penalty: 0 (POSITIVE - acceptable)")
        else:
            logger.warning("⚠️  No Content Analyzer data found in findings")

        # Bias Detector findings - MINIMAL category-aware penalties
        bias = findings.get("bias_detector", {}).get("findings", {}).get("bias_analysis", {})
        if bias:
            logger.info(f"✅ Bias Detector data found: {list(bias.keys())}")
            bias_score = bias.get("overall_bias_score", 0)
            if bias_score > 0:
                # Category-aware bias penalties - minimal
                if article_category in ['sports', 'entertainment']:
                    bias_weight = 0.03  # Almost none (normal for these)
                elif article_category in ['breaking_news']:
                    bias_weight = 0.04   # Minimal
                else:
                    bias_weight = 0.06  # Light for politics/general

                bias_penalty = int(bias_score * bias_weight)
                trust_score -= bias_penalty
                logger.info(f"   Bias penalty: -{bias_penalty} (score={bias_score}, weight={bias_weight})")
        else:
            logger.warning("⚠️  No Bias Detector data found in findings")

        # Bot Detector findings - LIGHT penalty
        bot = findings.get("bot_detector", {}).get("findings", {}).get("bot_analysis", {})
        if bot:
            logger.info(f"✅ Bot Detector data found: {list(bot.keys())}")
            bot_prob = bot.get("bot_probability", 0)
            if bot_prob > 0:
                bot_penalty = int(bot_prob * 0.1)  # Light penalty for bot detection
                trust_score -= bot_penalty
                logger.info(f"   Bot penalty: -{bot_penalty} (prob={bot_prob}%)")
        else:
            logger.warning("⚠️  No Bot Detector data found in findings")

        # Misinformation Detector findings - LIGHT category-aware penalties
        misinfo_det = findings.get("misinformation_detector", {}).get("findings", {}).get("misinformation_analysis", {})
        if misinfo_det:
            logger.info(f"✅ Misinformation Detector data found: {list(misinfo_det.keys())}")
            final_score = misinfo_det.get("final_misinformation_score", 0)
            if final_score > 0:
                # Adjust misinformation penalty by category - light
                if article_category in ['entertainment', 'sports']:
                    misinfo_weight = 0.05  # Very low for these
                elif article_category in ['breaking_news']:
                    misinfo_weight = 0.08   # Very light penalty
                else:
                    misinfo_weight = 0.1   # Light for politics/general

                misinfo_penalty = int(final_score * misinfo_weight)
                trust_score -= misinfo_penalty
                logger.info(f"   Misinformation penalty: -{misinfo_penalty} (score={final_score}, weight={misinfo_weight}, category={article_category})")
        else:
            logger.warning("⚠️  No Misinformation Detector data found in findings")

        final_score = max(10, min(100, int(trust_score)))
        logger.info(f"🎯 FINAL TRUST SCORE: {final_score}/100")

        # Ensure score is within 0-100
        return final_score

    async def synthesize(self, all_findings: dict, article_url: str = None, title: str = None, article_content: str = None, iteration: int = 1) -> dict:
        """Synthesize all agent findings into a comprehensive analysis with cross-source verification

        Args:
            iteration: If > 1, skip cache to force fresh synthesis on retry
        """

        # Check cache for same URL to ensure consistency (ONLY on first iteration)
        # On iterations 2+ during reflection loop, generate FRESH synthesis
        url_hash = None
        if article_url and iteration == 1:
            url_hash = hashlib.md5(article_url.encode()).hexdigest()
            if url_hash in _analysis_cache:
                logger.info(f"📦 Using cached analysis for URL: {article_url}")
                return _analysis_cache[url_hash]
        elif iteration > 1:
            logger.info(f"🔄 Iteration {iteration}: Generating FRESH synthesis (bypassing cache for retry)")

        # Detect article category for smarter scoring
        article_category = self.detect_article_category(
            title or "",
            article_content or "",
            all_findings
        )

        # Get model-only trust score (no external verification) with category awareness
        model_trust_score = self.calculate_trust_score(all_findings, article_category=article_category)

        # Cross-source verification (only with real content)
        verification_result = None
        validation_score = 0
        is_extraction_failed = title and ("Unable to extract" in title or "Error" in title)

        if article_url and title and not is_extraction_failed:
            logger.info("🔍 Running cross-source verification...")
            try:
                # Extract high-quality keywords from title (most topically relevant)
                stop_words = {
                    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'is', 'are', 'was', 'were',
                    'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
                    'might', 'can', 'must', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
                    'what', 'which', 'who', 'when', 'where', 'why', 'how', 'from', 'by', 'with', 'as', 'if', 'into',
                    'just', 'so', 'than', 'then', 'now', 'only', 'too', 'very', 'my', 'your', 'our', 'their', 'his', 'her'
                }

                # Extract main keywords from title (prioritize these as they represent main topic)
                title_words = [w.lower() for w in title.split() if w.lower() not in stop_words and len(w) > 3]

                # Add category-specific keywords for better relevance
                category_keywords = {
                    'war': ['war', 'conflict', 'military', 'attack', 'defense', 'troops', 'battle'],
                    'sports': ['sport', 'game', 'match', 'team', 'player', 'tournament', 'championship'],
                    'entertainment': ['movie', 'film', 'actor', 'celebrity', 'show', 'entertainment'],
                    'politics': ['election', 'political', 'government', 'parliament', 'vote', 'campaign'],
                }

                # Get category-relevant keywords if available
                category_words = category_keywords.get(article_category, [])

                # Combine: prioritize title words + category keywords + entities
                entities = all_findings.get("content_analyzer", {}).get("findings", {}).get("analysis", {}).get("entities", {})
                entity_names = [e.get("name") for e in entities.get("entities", [])[:3]] if isinstance(entities, dict) else []

                # Build final keyword list: title words first (most relevant), then category, then entities
                keywords = title_words[:2] + category_words[:1] + entity_names[:1]
                keywords = list(dict.fromkeys(keywords))[:3]  # Remove duplicates, keep top 3

                logger.info(f"🔑 Using keywords for verification: {keywords} (category: {article_category})")
                verification_result = await cross_source_verification.verify_story(
                    title=title,
                    url=article_url,
                    keywords=keywords,
                    article_content=article_content
                )

                # Extract validation score from verification (0-100)
                if verification_result:
                    validation_score = verification_result.get("confidence_score", 0)
                    logger.info(f"📊 Cross-source validation score: {validation_score}/100")
            except Exception as e:
                logger.error(f"❌ Cross-source verification error: {str(e)}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                verification_result = None
                validation_score = 0
        elif is_extraction_failed:
            logger.warning(f"⚠️ Skipping verification - extraction failed, title: {title}")

        # Calculate combined trust score (70% model, 30% validation)
        combined_trust_score = (model_trust_score * 0.70) + (validation_score * 0.30)
        combined_trust_score = int(combined_trust_score)

        # Risk level based on model score only
        if model_trust_score >= 75:
            risk_level = "LOW"
        elif model_trust_score >= 50:
            risk_level = "MEDIUM"
        elif model_trust_score >= 25:
            risk_level = "HIGH"
        else:
            risk_level = "CRITICAL"

        logger.info(f"📊 Trust Scores Summary:")
        logger.info(f"   Model Trust Score: {model_trust_score}/100")
        logger.info(f"   Cross-Source Validation: {validation_score}/100")
        logger.info(f"   Combined Trust Score: {combined_trust_score}/100")

        # Extract key metrics for context
        content = all_findings.get("content_analyzer", {}).get("findings", {}).get("analysis", {})
        bias = all_findings.get("bias_detector", {}).get("findings", {}).get("bias_analysis", {})
        bot = all_findings.get("bot_detector", {}).get("findings", {}).get("bot_analysis", {})
        misinfo = all_findings.get("misinformation_detector", {}).get("findings", {}).get("misinformation_analysis", {})

        toxicity_score = content.get("toxicity", {}).get("toxicity_score", 0)
        sentiment = content.get("sentiment", {}).get("label", "NEUTRAL")
        bias_score = bias.get("overall_bias_score", 0)
        bot_prob = bot.get("bot_probability", 0)
        propaganda_score = sum(misinfo.get("propaganda_techniques", {}).values()) / max(1, len(misinfo.get("propaganda_techniques", {}))) if misinfo.get("propaganda_techniques") else 0
        emotional_manipulation = misinfo.get("emotional_manipulation", {}).get("manipulation_score", 0)
        unverified_risk = misinfo.get("unverified_claims", {}).get("unverified_risk", 0)

        # Create detailed summary from all findings with category and context awareness

        # Determine source credibility based on URL
        source_credibility = "unknown"
        if article_url:
            url_lower = article_url.lower()
            reputable_sources = ["bbc", "reuters", "ap", "apnews", "nytimes", "guardian", "reuters", "timesofindia", "ndtv", "hindu", "bloomberg", "economist"]
            tabloid_sources = ["dailymail", "mirror", "sun", "express"]

            if any(source in url_lower for source in reputable_sources):
                source_credibility = "reputable"
            elif any(source in url_lower for source in tabloid_sources):
                source_credibility = "tabloid"

        # Context-specific guidance
        category_context = ""
        if article_category == "sports":
            category_context = "This is a SPORTS article. Note: High emotion and dramatic language are expected in sports reporting and shouldn't be viewed negatively."
        elif article_category == "war":
            category_context = "This is a WAR/CONFLICT article. Note: Negative sentiment and serious tone are appropriate for conflict reporting."
        elif article_category == "entertainment":
            category_context = "This is an ENTERTAINMENT article. Note: Sensational language and emotional appeals are typical in entertainment coverage."
        elif article_category == "breaking_news":
            category_context = "This is a BREAKING NEWS article. Note: Urgency and provisional information are normal in breaking news before full details emerge."

        source_context = ""
        if source_credibility == "reputable":
            source_context = "Source is from a reputable, established news organization."
        elif source_credibility == "tabloid":
            source_context = "Source is from a tabloid publication - reader caution advised."

        # Adjust prompt based on iteration - push for more depth on retries
        iteration_instruction = ""
        if iteration == 1:
            iteration_instruction = "This is your FIRST attempt. Write a comprehensive, well-balanced analysis covering all key metrics.\n\n"
        elif iteration == 2:
            iteration_instruction = "This is your SECOND attempt. The previous analysis was rejected for insufficient depth or missing details. THIS TIME: Add MORE specific examples, MORE concrete evidence references, MORE actionable guidance, and DEEPER analysis of what each metric means.\n\n"
        elif iteration >= 3:
            iteration_instruction = "This is your FINAL attempt (iteration 3). Go DEEPER. This must be your most detailed, evidence-rich, insightful analysis yet. Include specific metric interpretations, detailed reasoning, concrete examples of what readers should watch for, and crystal-clear actionable guidance.\n\n"

        summary_prompt = f"""You are a world-class news analyst, investigative journalist, and fact-checker with 20+ years of experience. Your task is to write an EXCEPTIONAL, INSIGHTFUL, and DEEPLY ANALYTICAL assessment of this article that readers will find genuinely valuable.

{iteration_instruction}
═══════════════════════════════════════════════════════════════════════════════
ARTICLE CONTEXT & ANALYSIS PARAMETERS
═══════════════════════════════════════════════════════════════════════════════

Article Type: {article_category.upper().replace('_', ' ')}
{category_context}

Publication Source: {source_context if source_context else "Independent/Unknown source"}
URL Pattern suggests: {source_credibility.upper() if source_credibility != 'unknown' else 'Verify publication independently'}

═══════════════════════════════════════════════════════════════════════════════
TRUST ANALYSIS SCORES & INTERPRETATION
═══════════════════════════════════════════════════════════════════════════════

MODEL TRUST SCORE: {model_trust_score}/100
├─ What this means: {self._interpret_trust_score(model_trust_score)}
└─ Based on: Internal ML analysis of content quality, structure, and claims

CROSS-SOURCE VALIDATION: {validation_score}/100
├─ What this means: {self._interpret_validation_score(validation_score)}
└─ Based on: How many other reputable sources are reporting this story

COMBINED TRUST SCORE: {combined_trust_score}/100 (70% Model + 30% Validation)
RISK LEVEL: {risk_level}

═══════════════════════════════════════════════════════════════════════════════
DETAILED METRIC BREAKDOWN (What Each Means for Readers)
═══════════════════════════════════════════════════════════════════════════════

SENTIMENT: {sentiment}
→ {self._interpret_sentiment(sentiment)}

TOXICITY LEVEL: {toxicity_score}/100
→ {self._interpret_toxicity(toxicity_score, article_category)}

BIAS SCORE: {bias_score}/100
→ {self._interpret_bias(bias_score)}

BOT PROBABILITY: {bot_prob}%
→ {self._interpret_bot_probability(bot_prob)}

PROPAGANDA TECHNIQUES: {propaganda_score:.0f}/100
→ {self._interpret_propaganda(propaganda_score)}

EMOTIONAL MANIPULATION: {emotional_manipulation}/100
→ {self._interpret_emotional_manipulation(emotional_manipulation, article_category)}

UNVERIFIED CLAIMS RISK: {unverified_risk}/100
→ {self._interpret_unverified_risk(unverified_risk)}

═══════════════════════════════════════════════════════════════════════════════
INSTRUCTIONS FOR YOUR ASSESSMENT (READ CAREFULLY)
═══════════════════════════════════════════════════════════════════════════════

Write 10-12 sentences covering ALL of the following:

1. OPENING PARAGRAPH (2-3 sentences):
   - Give an immediate, candid assessment of the article's overall credibility
   - Consider the publication source and article category together
   - Set reader expectations upfront

2. CREDIBILITY DEEP DIVE (2-3 sentences):
   - Explain the ACTUAL REASONS for the trust score (not the numbers, but the substance)
   - What does this article do well? Where are the weaknesses?
   - Be specific about which metrics matter most here

3. CROSS-SOURCE PERSPECTIVE (1-2 sentences):
   - Is this story corroborated by other outlets?
   - What does the validation score tell us about how widely accepted this story is?
   - Are there conflicting narratives elsewhere?

4. CATEGORY-SPECIFIC CONTEXT (1-2 sentences):
   - How does the {article_category.upper()} nature of this story affect interpretation?
   - What's normal for this type? What's concerning?
   - Why shouldn't readers over-penalize or over-trust based on category alone?

5. RISK ASSESSMENT & RED FLAGS (2-3 sentences):
   - What should readers be careful about?
   - Are there unverified claims? Emotional manipulation? Bot-like patterns?
   - What specific claims need independent verification?

6. CLOSING GUIDANCE (1-2 sentences):
   - Give readers a crystal-clear recommendation on how to use this article
   - Should they trust it completely, partially, or view it as preliminary?
   - What's the best way to consume this article responsibly?

═══════════════════════════════════════════════════════════════════════════════
TONE & STYLE REQUIREMENTS
═══════════════════════════════════════════════════════════════════════════════

✓ DO:
  - Write like you're talking to an intelligent, educated reader
  - Be specific and concrete (not vague like "some concerns")
  - Use "The article..." not "It..." to be clearer
  - Mix short and long sentences for readability
  - Show your reasoning, not just conclusions
  - Acknowledge nuance and complexity
  - Be fair to the publication while honest about weaknesses

✗ DON'T:
  - Use percentages or numbers in flowing text (say "most" not "67%")
  - Write generic summaries that could apply to any article
  - Use clichés like "in conclusion" or "to summarize"
  - Be unnecessarily harsh or overly generous
  - Make it sound like a machine wrote it
  - Include bullet points or lists

═══════════════════════════════════════════════════════════════════════════════
QUALITY EXAMPLES OF EXCELLENT ASSESSMENTS
═══════════════════════════════════════════════════════════════════════════════

EXAMPLE 1 (Medium Trust Article):
"The Times of India's reporting on the Neymar injury demonstrates solid journalism with verified facts from official sources, though the dramatic framing 'World Cup Fate Confirmed' oversells the provisional nature of medical timelines. The article excels at gathering player reactions and expert commentary, giving readers a complete picture, but the emotional language around 'showdown' and timeline speculation should be treated as opinion, not fact. Cross-source validation is exceptional—this story appears in ESPN, Reuters, and AP News with consistent core facts, though interpretations differ slightly. As a sports story, heightened emotion is normal and doesn't indicate dishonesty. The main risk is taking recovery timeline predictions as certainties; readers should await official team medical statements. You can trust the event itself happened and the basic facts are accurate, but wait for official confirmation on recovery details before making predictions."

EXAMPLE 2 (Lower Trust Article):
"This article reads more like opinion than investigation, with a title that seems designed to provoke rather than inform. The publication has known sensationalist tendencies, and the analysis here relies heavily on unverified claims without adequate attribution to sources. While some core facts check out when cross-referenced, major claims lack supporting evidence, and the article conflates speculation with fact repeatedly. The emotional manipulation is significant—phrases like 'shocking truth' and 'explosive revelation' appear where evidence is thin. Cross-source validation returns minimal results, which is telling; reputable outlets are either not covering this angle or actively contradicting it. The article doesn't appear to be bot-generated, but the writing style prioritizes emotional impact over clarity. Be extremely cautious; read this as a starting point for investigation, not as established fact, and seek corroboration from major news outlets before relying on any claims."

═══════════════════════════════════════════════════════════════════════════════
NOW WRITE YOUR ASSESSMENT (10-12 sentences of pure insight):
═══════════════════════════════════════════════════════════════════════════════
"""

        summary = self.llm.invoke(summary_prompt)

        result = {
            "agent": "synthesis_agent",
            "status": "completed",
            "findings": {
                # Trust Scores
                "trust_score": model_trust_score,
                "validation_score": validation_score,
                "combined_trust_score": combined_trust_score,
                "risk_level": risk_level,

                # Summary & Analysis
                "summary": summary,
                "article_category": article_category,
                "source_credibility": source_credibility,

                # Key Metrics
                "sentiment": sentiment,
                "toxicity_score": toxicity_score,
                "bias_score": bias_score,
                "bot_probability": bot_prob,
                "propaganda_score": propaganda_score,
                "emotional_manipulation": emotional_manipulation,
                "unverified_risk": unverified_risk,

                # Verification
                "cross_source_verification": verification_result,

                # Full Findings
                "all_agent_findings": all_findings
            },
            "confidence": 0.92
        }

        # Cache result for same URL
        if url_hash:
            _analysis_cache[url_hash] = result
            logger.info(f"✅ Analysis cached for URL: {article_url}")

        return result

# Initialize with HuggingFace Inference API
synthesis_agent = SynthesisAgent(groq_client.get_synthesis_llm())

from src.llm.groq_client import groq_client
import json
import logging
import hashlib

logger = logging.getLogger(__name__)

class SynthesisAgent:
    """Combine all findings into coherent report"""

    def __init__(self, llm):
        self.llm = llm

    def calculate_trust_score(self, findings: dict) -> int:
        """Calculate dynamic trust score (0-100) from real agent findings"""

        trust_score = 75  # Start at neutral

        logger.info(f"📊 Calculating trust score from findings keys: {list(findings.keys())}")

        # Content Analyzer findings
        content = findings.get("content_analyzer", {}).get("findings", {}).get("analysis", {})
        if content:
            logger.info(f"✅ Content Analyzer data found: {list(content.keys())}")
            # Penalize high toxicity
            toxicity = content.get("toxicity", {}).get("toxicity_score", 0)
            if toxicity > 0:
                trust_score -= int(toxicity * 0.5)
                logger.info(f"   Toxicity penalty: -{int(toxicity * 0.5)} (score={toxicity})")

            # Penalize misinfo
            misinfo = content.get("misinformation", {}).get("misinformation_likelihood", 0)
            if misinfo > 0:
                trust_score -= int(misinfo * 0.3)
                logger.info(f"   Misinfo penalty: -{int(misinfo * 0.3)} (score={misinfo})")

            # Sentiment (negative = less trustworthy)
            sentiment = content.get("sentiment", {}).get("label", "NEUTRAL")
            if sentiment == "NEGATIVE":
                trust_score -= 8
                logger.info(f"   Sentiment penalty: -8 (NEGATIVE)")
            elif sentiment == "POSITIVE":
                trust_score -= 5  # Sensationalism
                logger.info(f"   Sentiment penalty: -5 (POSITIVE/sensational)")
        else:
            logger.warning("⚠️  No Content Analyzer data found in findings")

        # Bias Detector findings (now 0-100 scale)
        bias = findings.get("bias_detector", {}).get("findings", {}).get("bias_analysis", {})
        if bias:
            logger.info(f"✅ Bias Detector data found: {list(bias.keys())}")
            bias_score = bias.get("overall_bias_score", 0)
            if bias_score > 0:
                bias_penalty = int(bias_score * 0.3)  # Scale down since now 0-100
                trust_score -= bias_penalty
                logger.info(f"   Bias penalty: -{bias_penalty} (score={bias_score})")
        else:
            logger.warning("⚠️  No Bias Detector data found in findings")

        # Bot Detector findings
        bot = findings.get("bot_detector", {}).get("findings", {}).get("bot_analysis", {})
        if bot:
            logger.info(f"✅ Bot Detector data found: {list(bot.keys())}")
            bot_prob = bot.get("bot_probability", 0)
            if bot_prob > 0:
                trust_score -= int(bot_prob * 0.3)
                logger.info(f"   Bot penalty: -{int(bot_prob * 0.3)} (prob={bot_prob}%)")
        else:
            logger.warning("⚠️  No Bot Detector data found in findings")

        # Misinformation Detector findings
        misinfo_det = findings.get("misinformation_detector", {}).get("findings", {}).get("misinformation_analysis", {})
        if misinfo_det:
            logger.info(f"✅ Misinformation Detector data found: {list(misinfo_det.keys())}")
            final_score = misinfo_det.get("final_misinformation_score", 0)
            if final_score > 0:
                trust_score -= int(final_score * 0.4)
                logger.info(f"   Misinformation penalty: -{int(final_score * 0.4)} (score={final_score})")
        else:
            logger.warning("⚠️  No Misinformation Detector data found in findings")

        final_score = max(10, min(100, int(trust_score)))
        logger.info(f"🎯 FINAL TRUST SCORE: {final_score}/100")

        # Ensure score is within 0-100
        return final_score

    async def synthesize(self, all_findings: dict) -> dict:
        """Synthesize all agent findings into a comprehensive analysis"""

        trust_score = self.calculate_trust_score(all_findings)

        if trust_score >= 75:
            risk_level = "LOW"
        elif trust_score >= 50:
            risk_level = "MEDIUM"
        elif trust_score >= 25:
            risk_level = "HIGH"
        else:
            risk_level = "CRITICAL"

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

        # Create detailed summary from all findings with better prompt
        summary_prompt = f"""You are an expert news analyst and fact-checker. Analyze this article based on the metrics below and provide a natural, professional assessment.

TRUST SCORE: {trust_score}/100 (Lower = Less Trustworthy)
RISK LEVEL: {risk_level}

KEY METRICS:
- Sentiment: {sentiment}
- Toxicity Level: {toxicity_score}/100 (offensive/NSFW content)
- Bias Score: {bias_score}/100
- Bot Probability: {bot_prob}%
- Propaganda Techniques Detected: {propaganda_score:.0f}/100
- Emotional Manipulation: {emotional_manipulation}/100
- Unverified Claims Risk: {unverified_risk}/100

WRITE A PROFESSIONAL ASSESSMENT (4-5 sentences) that:
1. Start with the overall credibility assessment in natural language
2. Explain the KEY REASONS for the trust score (1-3 main factors only)
3. Mention what the article does WELL (if applicable)
4. State clear, actionable recommendations for readers
5. Keep tone objective and balanced

FORMAT:
- Natural, flowing prose (NOT bullet points)
- Professional but accessible language
- NO percentages in the main text (just say "high", "low", "moderate")
- Start with "This article" or "The content"
- End with specific reader guidance

EXAMPLE STYLE:
"This article presents balanced coverage with credible sourcing, though some emotional language is present. The overall trust score of 72/100 reflects reliable factual reporting mixed with moderate opinion elements. Readers should verify recent claims independently but can generally rely on the established facts presented."

NOW WRITE THE ASSESSMENT:"""

        summary = self.llm.invoke(summary_prompt)

        return {
            "agent": "synthesis_agent",
            "status": "completed",
            "findings": {
                "trust_score": trust_score,
                "risk_level": risk_level,
                "summary": summary,
                "all_agent_findings": all_findings
            },
            "confidence": 0.92
        }

# Initialize with HuggingFace Inference API
synthesis_agent = SynthesisAgent(groq_client.get_synthesis_llm())

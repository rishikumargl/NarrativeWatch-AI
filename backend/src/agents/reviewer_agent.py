from src.llm.groq_client import groq_client
import logging

logger = logging.getLogger(__name__)

class ReviewerAgent:
    """Quality assurance - BALANCED validation (not too harsh, not too lenient)"""

    def __init__(self, llm):
        self.llm = llm

    async def review(self, report: dict, iteration: int = 1) -> dict:
        """Review and validate report with reasonable quality checks"""

        is_approved = True
        feedback = []
        quality_score = 0.80  # Start with good baseline

        logger.info(f"📋 Reviewer iteration {iteration}...")

        # ===== CORE STRUCTURAL CHECKS =====

        # Check 1: Trust score exists and valid
        trust_score = report.get("findings", {}).get("trust_score")
        if trust_score is None:
            feedback.append("❌ Trust score missing")
            is_approved = False
            quality_score -= 0.15
        elif not isinstance(trust_score, (int, float)):
            feedback.append(f"❌ Trust score not a number")
            is_approved = False
            quality_score -= 0.10
        elif not (10 <= trust_score <= 100):
            feedback.append(f"⚠️ Trust score out of range: {trust_score}")
            quality_score -= 0.08

        # Check 2: Summary exists and has reasonable content
        summary = report.get("findings", {}).get("summary", "")
        if not summary:
            feedback.append("❌ Summary missing or empty")
            is_approved = False
            quality_score -= 0.25
        else:
            # Summary quality based on length
            if len(summary) < 100:
                feedback.append(f"⚠️ Summary quite short ({len(summary)} chars) - could be more detailed")
                quality_score -= 0.10
            elif len(summary) < 200:
                feedback.append(f"⚠️ Summary could be more comprehensive ({len(summary)} chars)")
                quality_score -= 0.05

        # Check 3: Risk level is valid
        risk_level = report.get("findings", {}).get("risk_level")
        valid_risk_levels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        if risk_level not in valid_risk_levels:
            feedback.append(f"⚠️ Invalid risk level: {risk_level}")
            quality_score -= 0.08

        # Check 4: Basic consistency (trust & risk alignment)
        try:
            ts = trust_score or 50
            if ts >= 75 and risk_level == "CRITICAL":
                feedback.append(f"⚠️ Inconsistency: High trust but CRITICAL risk")
                quality_score -= 0.05
            elif ts <= 30 and risk_level == "LOW":
                feedback.append(f"⚠️ Inconsistency: Low trust but LOW risk")
                quality_score -= 0.05
        except:
            pass

        # Clamp score between 0 and 1
        quality_score = max(0, min(1.0, quality_score))

        # ===== BALANCED APPROVAL THRESHOLDS =====
        # Iteration 1: 0.55 (accept decent summaries, reject very poor ones)
        # Iteration 2: 0.63 (push for improvement)
        # Iteration 3: 0.70 (final attempt)
        approval_thresholds = {
            1: 0.55,
            2: 0.63,
            3: 0.70
        }
        approval_threshold = approval_thresholds.get(iteration, 0.70)

        # Final decision
        if quality_score >= approval_threshold and is_approved:
            recommendation = "✅ APPROVED"
            logger.info(f"✅ Iteration {iteration}: APPROVED (score: {quality_score:.3f} >= {approval_threshold})")
        else:
            recommendation = "❌ REVISION_NEEDED"
            if not feedback:
                feedback.append(f"Quality score {quality_score:.3f} below {approval_threshold}")
            logger.warning(f"❌ Iteration {iteration}: REJECTED (score: {quality_score:.3f} < {approval_threshold})")
            is_approved = False

        return {
            "agent": "reviewer_agent",
            "status": "completed",
            "findings": {
                "approved": is_approved,
                "iteration": iteration,
                "feedback": feedback if feedback else ["✅ All checks passed"],
                "quality_score": round(quality_score, 3),
                "approval_threshold": approval_threshold,
                "recommendation": recommendation
            },
            "confidence": 0.92
        }

# Initialize with Groq LLM for validation
reviewer_agent = ReviewerAgent(groq_client.get_reviewer_llm())

from src.llm.groq_client import groq_client
import json
import logging

logger = logging.getLogger(__name__)

class ReviewerAgent:
    """Quality assurance and reflection loop - DYNAMIC validation"""

    def __init__(self, llm):
        self.llm = llm

    async def review(self, report: dict, iteration: int = 1) -> dict:
        """Review and validate report quality with dynamic thresholds"""

        is_approved = True
        feedback = []
        quality_score = 0.90

        # 1. STRUCTURAL VALIDATION
        if report.get("findings", {}).get("trust_score") is None:
            feedback.append("❌ Trust score missing")
            is_approved = False
            quality_score -= 0.25

        if not report.get("findings", {}).get("summary"):
            feedback.append("❌ Summary missing or empty")
            is_approved = False
            quality_score -= 0.25

        # 2. SEMANTIC VALIDATION
        try:
            trust_score = report.get("findings", {}).get("trust_score")
            if trust_score is not None:
                if not isinstance(trust_score, (int, float)):
                    feedback.append(f"❌ Trust score must be number, got {type(trust_score)}")
                    is_approved = False
                    quality_score -= 0.15
                elif not (10 <= trust_score <= 100):
                    feedback.append(f"⚠️  Trust score out of valid range: {trust_score}")
                    is_approved = False
                    quality_score -= 0.10
        except Exception as e:
            feedback.append(f"❌ Error validating trust score: {str(e)}")
            is_approved = False
            quality_score -= 0.25

        # 3. RISK LEVEL VALIDATION
        risk_level = report.get("findings", {}).get("risk_level")
        valid_risk_levels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        if risk_level not in valid_risk_levels:
            feedback.append(f"❌ Invalid risk level: {risk_level}")
            is_approved = False
            quality_score -= 0.15

        # 4. SUMMARY QUALITY CHECK
        summary = report.get("findings", {}).get("summary", "")
        if summary and len(summary) < 50:
            feedback.append(f"⚠️  Summary too short ({len(summary)} chars) - lacks detail")
            quality_score -= 0.10
            if iteration >= 2:
                is_approved = False

        # 5. CONSISTENCY CHECK
        # Trust score and risk level should be consistent
        try:
            ts = report.get("findings", {}).get("trust_score", 50)
            rl = report.get("findings", {}).get("risk_level", "MEDIUM")

            if ts >= 75 and rl != "LOW":
                feedback.append(f"⚠️  Inconsistency: High trust score ({ts}) but {rl} risk level")
                quality_score -= 0.05

            if ts <= 25 and rl != "CRITICAL":
                feedback.append(f"⚠️  Inconsistency: Low trust score ({ts}) but {rl} risk level")
                quality_score -= 0.05
        except:
            pass

        # 6. DYNAMIC APPROVAL LOGIC
        # Stricter on later iterations
        approval_threshold = 0.75 if iteration <= 1 else 0.80 if iteration == 2 else 0.85

        if quality_score >= approval_threshold and is_approved:
            recommendation = "✅ APPROVED"
            logger.info(f"✅ Iteration {iteration}: APPROVED (quality: {quality_score:.2f})")
        else:
            recommendation = "❌ REVISION_NEEDED"
            if not feedback:
                feedback.append("Quality score below threshold")
            logger.warning(f"❌ Iteration {iteration}: REJECTED (quality: {quality_score:.2f})")
            is_approved = False

        return {
            "agent": "reviewer_agent",
            "status": "completed",
            "findings": {
                "approved": is_approved,
                "iteration": iteration,
                "feedback": feedback if feedback else ["✅ All validation checks passed"],
                "quality_score": round(quality_score, 2),
                "approval_threshold": approval_threshold,
                "recommendation": recommendation
            },
            "confidence": 0.92
        }

# Initialize with Groq LLM for validation
reviewer_agent = ReviewerAgent(groq_client.get_reviewer_llm())

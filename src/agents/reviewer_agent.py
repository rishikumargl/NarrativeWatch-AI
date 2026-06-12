"""Reviewer Agent - Quality assurance and feedback generation."""

from typing import Any, Dict, List
from dataclasses import dataclass


@dataclass
class ReviewFeedback:
    status: str
    completeness_score: float
    accuracy_score: float
    clarity_score: float
    relevance_score: float
    issues: List[str]
    suggestions: List[str]
    confidence: float


class ReviewerAgent:
    """Quality assurance agent that reviews synthesis output."""

    def __init__(self, name: str = "Reviewer Agent"):
        self.name = name
        self.description = "Quality assurance agent that evaluates synthesis output"

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Review synthesis result.

        Args:
            input_data: Dict with 'synthesis_result' and 'agent_results'

        Returns:
            Dict with status, feedback, issues, suggestions
        """
        synthesis_result = input_data.get("synthesis_result", {})
        agent_results = input_data.get("agent_results", {})

        feedback = self.evaluate_synthesis(synthesis_result, agent_results)

        return {
            "status": feedback.status,
            "completeness_score": feedback.completeness_score,
            "accuracy_score": feedback.accuracy_score,
            "clarity_score": feedback.clarity_score,
            "relevance_score": feedback.relevance_score,
            "issues": feedback.issues,
            "suggestions": feedback.suggestions,
            "confidence": feedback.confidence,
            "approved": feedback.status == "APPROVED"
        }

    def evaluate_synthesis(
        self,
        synthesis_result: Dict[str, Any],
        agent_results: Dict[str, Any]
    ) -> ReviewFeedback:
        """Evaluate synthesis quality across multiple dimensions."""
        issues = []
        suggestions = []

        completeness_score = self._check_completeness(synthesis_result, agent_results, issues, suggestions)
        accuracy_score = self._check_accuracy(synthesis_result, agent_results, issues, suggestions)
        clarity_score = self._check_clarity(synthesis_result, issues, suggestions)
        relevance_score = self._check_relevance(synthesis_result, issues, suggestions)

        overall_score = (completeness_score + accuracy_score + clarity_score + relevance_score) / 4
        confidence = min(1.0, completeness_score * accuracy_score)

        status = "APPROVED" if overall_score >= 0.75 else "NEEDS_REVISION"

        return ReviewFeedback(
            status=status,
            completeness_score=completeness_score,
            accuracy_score=accuracy_score,
            clarity_score=clarity_score,
            relevance_score=relevance_score,
            issues=issues,
            suggestions=suggestions,
            confidence=confidence
        )

    def _check_completeness(
        self,
        synthesis_result: Dict[str, Any],
        agent_results: Dict[str, Any],
        issues: List[str],
        suggestions: List[str]
    ) -> float:
        """Check if all agent results are covered."""
        required_fields = ["report", "key_findings", "evidence", "recommendation"]
        missing_fields = [f for f in required_fields if not synthesis_result.get(f)]

        if missing_fields:
            issues.append(f"Missing fields: {', '.join(missing_fields)}")
            suggestions.append("Ensure all output fields are populated")
            return 0.5

        key_findings = synthesis_result.get("key_findings", [])
        if len(key_findings) < 3:
            issues.append(f"Only {len(key_findings)} key findings identified (recommend 5-10)")
            suggestions.append("Increase depth of analysis or extract more insights")
            return 0.7

        evidence = synthesis_result.get("evidence", [])
        if len(evidence) < 3:
            issues.append(f"Only {len(evidence)} evidence items cited (recommend 5+)")
            suggestions.append("Gather more supporting evidence from agent results")
            return 0.7

        agents_used = sum(1 for key in [
            "content_analyzer", "rag_agent", "research_agent",
            "bias_detector", "bot_detector", "campaign_detector"
        ] if agent_results.get(key))

        if agents_used < 4:
            issues.append(f"Only {agents_used} agents utilized (recommend 6)")
            suggestions.append("Ensure all specialized agents contribute to analysis")
            return 0.8

        return 0.95

    def _check_accuracy(
        self,
        synthesis_result: Dict[str, Any],
        agent_results: Dict[str, Any],
        issues: List[str],
        suggestions: List[str]
    ) -> float:
        """Check accuracy of synthesis against agent outputs."""
        report = synthesis_result.get("report", "")
        evidence = synthesis_result.get("evidence", [])

        if not report or len(report) < 500:
            issues.append("Report too brief (minimum 500 characters recommended)")
            suggestions.append("Expand report with more detailed analysis")
            return 0.6

        if not evidence:
            issues.append("No evidence cited in synthesis")
            suggestions.append("Support findings with evidence from agent results")
            return 0.5

        campaign_detector = agent_results.get("campaign_detector", {})
        if campaign_detector and campaign_detector.get("campaigns"):
            campaign_mentions = report.count("campaign") + report.count("coordinated")
            if campaign_mentions == 0:
                issues.append("Campaign detection results not mentioned in report")
                suggestions.append("Include campaign findings in narrative")
                return 0.7

        bot_detector = agent_results.get("bot_detector", {})
        if bot_detector and bot_detector.get("bot_probability", 0) > 0.5:
            bot_mentions = report.count("bot") + report.count("inauthentic")
            if bot_mentions == 0:
                issues.append("Bot detection findings not adequately represented")
                suggestions.append("Highlight bot activity in analysis")
                return 0.75

        return 0.9

    def _check_clarity(
        self,
        synthesis_result: Dict[str, Any],
        issues: List[str],
        suggestions: List[str]
    ) -> float:
        """Check report clarity and structure."""
        report = synthesis_result.get("report", "")
        recommendation = synthesis_result.get("recommendation", "")
        key_findings = synthesis_result.get("key_findings", [])

        if not report or len(report) < 200:
            issues.append("Report lacks sufficient detail")
            suggestions.append("Provide more comprehensive analysis")
            return 0.5

        has_sections = sum(1 for section in [
            "Summary", "Findings", "Evidence", "Category"
        ] if section.lower() in report.lower())

        if has_sections < 2:
            issues.append("Report lacks clear section organization")
            suggestions.append("Structure report with clear sections and headers")
            return 0.6

        if not recommendation or len(recommendation) < 20:
            issues.append("Recommendation missing or too brief")
            suggestions.append("Provide clear, actionable recommendation")
            return 0.7

        if not key_findings or len(key_findings) < 3:
            issues.append("Key findings not clearly highlighted")
            suggestions.append("Extract and list 5-10 main findings")
            return 0.7

        return 0.9

    def _check_relevance(
        self,
        synthesis_result: Dict[str, Any],
        issues: List[str],
        suggestions: List[str]
    ) -> float:
        """Check relevance to original query."""
        report = synthesis_result.get("report", "")
        original_query = synthesis_result.get("original_query", "")
        recommendation = synthesis_result.get("recommendation", "")

        if not original_query:
            return 0.85

        query_terms = original_query.lower().split()
        matched_terms = sum(1 for term in query_terms if term in report.lower())
        term_coverage = matched_terms / len(query_terms) if query_terms else 0

        if term_coverage < 0.3:
            issues.append(f"Report only addresses {term_coverage:.1%} of query terms")
            suggestions.append("Ensure report directly answers the original query")
            return 0.6

        if not recommendation:
            issues.append("No actionable recommendation provided")
            suggestions.append("Generate clear recommendation based on findings")
            return 0.7

        return 0.9

    def generate_feedback_prompt(self, feedback: ReviewFeedback) -> str:
        """Generate detailed feedback for synthesis regeneration."""
        lines = []

        lines.append(f"Review Status: {feedback.status}")
        lines.append("")

        lines.append("Evaluation Scores:")
        lines.append(f"- Completeness: {feedback.completeness_score:.1%}")
        lines.append(f"- Accuracy: {feedback.accuracy_score:.1%}")
        lines.append(f"- Clarity: {feedback.clarity_score:.1%}")
        lines.append(f"- Relevance: {feedback.relevance_score:.1%}")
        lines.append("")

        if feedback.issues:
            lines.append("Issues Identified:")
            for issue in feedback.issues:
                lines.append(f"- {issue}")
            lines.append("")

        if feedback.suggestions:
            lines.append("Suggestions for Improvement:")
            for suggestion in feedback.suggestions:
                lines.append(f"- {suggestion}")
            lines.append("")

        lines.append("Please regenerate the synthesis addressing these issues.")

        return "\n".join(lines)

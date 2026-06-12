"""Synthesis Agent - Combines findings from all agents into final report."""

from typing import Any, Dict, List
from dataclasses import dataclass


@dataclass
class Evidence:
    type: str
    description: str
    confidence: float
    source: str


class SynthesisAgent:
    """Synthesizes findings from all agents into coherent final report."""

    def __init__(self, name: str = "Synthesis Agent"):
        self.name = name
        self.description = "Combines findings from all agents into comprehensive report"

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesize agent results into final report.

        Args:
            input_data: Dict with 'agent_results' and 'original_query'

        Returns:
            Dict with synthesized report, findings, evidence, recommendation
        """
        agent_results = input_data.get("agent_results", {})
        original_query = input_data.get("original_query", "")

        key_findings = self._extract_key_findings(agent_results)
        evidence_list = self._build_evidence_list(agent_results)
        evidence_list = self._rank_evidence(evidence_list)

        report = self._generate_report(agent_results, key_findings, evidence_list, original_query)
        recommendation = self._generate_recommendation(key_findings, agent_results)
        trust_components = self._extract_trust_components(agent_results)

        return {
            "report": report,
            "key_findings": key_findings,
            "evidence": [
                {
                    "type": e.type,
                    "description": e.description,
                    "confidence": e.confidence,
                    "source": e.source
                }
                for e in evidence_list
            ],
            "recommendation": recommendation,
            "trust_score_components": trust_components,
            "completeness_score": self._calculate_completeness(agent_results),
            "original_query": original_query
        }

    def _extract_key_findings(self, agent_results: Dict[str, Any]) -> List[str]:
        """Extract 5-10 most important findings."""
        findings = []

        campaigns = agent_results.get("campaign_detector", {})
        if campaigns:
            campaign_count = campaigns.get("campaign_count", 0)
            if campaign_count > 0:
                findings.append(f"Coordinated campaign activity detected across {campaign_count} page(s)")

        bot_detector = agent_results.get("bot_detector", {})
        if bot_detector:
            bot_prob = bot_detector.get("bot_probability", 0)
            if bot_prob > 0.7:
                findings.append(f"High bot activity detected ({bot_prob*100:.0f}% probability)")

        research = agent_results.get("research_agent", {})
        if research:
            fact_checks = research.get("fact_checks", [])
            false_count = sum(1 for fc in fact_checks if "FALSE" in str(fc).upper())
            if fact_checks:
                false_rate = (false_count / len(fact_checks)) * 100
                findings.append(f"Fact-checking reveals {false_rate:.0f}% false claims")

        bias_detector = agent_results.get("bias_detector", {})
        if bias_detector:
            bias = bias_detector.get("political_bias", 0)
            if bias > 0.7:
                findings.append(f"Strong political bias detected ({bias*100:.0f})")

        content = agent_results.get("content_analyzer", {})
        if content:
            emotional_score = content.get("emotional_score", 0)
            if emotional_score > 0.7:
                findings.append(f"High emotional manipulation detected")

        rag = agent_results.get("rag_agent", {})
        if rag:
            similar_count = len(rag.get("similar_campaigns", []))
            if similar_count > 0:
                findings.append(f"Matches {similar_count} known manipulation patterns")

        return findings[:10]

    def _build_evidence_list(self, agent_results: Dict[str, Any]) -> List[Evidence]:
        """Build list of evidence from all sources."""
        evidence = []

        if "campaign_detector" in agent_results and agent_results["campaign_detector"]:
            camp = agent_results["campaign_detector"]
            campaigns = camp.get("campaigns", [])
            for c in campaigns:
                evidence.append(Evidence(
                    type="campaign_coordination",
                    description=f"Campaign '{c.get('narrative_theme')}' with confidence {c.get('confidence', 0):.2f}",
                    confidence=c.get("confidence", 0),
                    source="campaign_detector"
                ))

        if "bot_detector" in agent_results and agent_results["bot_detector"]:
            bot = agent_results["bot_detector"]
            if bot.get("suspicious_engagement"):
                evidence.append(Evidence(
                    type="bot_activity",
                    description="Inauthentic engagement patterns detected",
                    confidence=bot.get("bot_probability", 0),
                    source="bot_detector"
                ))

        if "bias_detector" in agent_results and agent_results["bias_detector"]:
            bias = agent_results["bias_detector"]
            if bias.get("political_bias", 0) > 0.5:
                evidence.append(Evidence(
                    type="bias",
                    description=f"Political bias: {bias.get('bias_types', [])}",
                    confidence=bias.get("political_bias", 0),
                    source="bias_detector"
                ))

        if "research_agent" in agent_results and agent_results["research_agent"]:
            research = agent_results["research_agent"]
            fact_checks = research.get("fact_checks", [])
            if fact_checks:
                false_count = sum(1 for fc in fact_checks if "FALSE" in str(fc).upper())
                evidence.append(Evidence(
                    type="fact_check",
                    description=f"{false_count} of {len(fact_checks)} claims are false",
                    confidence=false_count / len(fact_checks) if fact_checks else 0,
                    source="research_agent"
                ))

        if "content_analyzer" in agent_results and agent_results["content_analyzer"]:
            content = agent_results["content_analyzer"]
            if content.get("emotional_score", 0) > 0.5:
                evidence.append(Evidence(
                    type="manipulation",
                    description="Emotional manipulation tactics identified",
                    confidence=content.get("emotional_score", 0),
                    source="content_analyzer"
                ))

        if "rag_agent" in agent_results and agent_results["rag_agent"]:
            rag = agent_results["rag_agent"]
            similar = rag.get("similar_campaigns", [])
            if similar:
                evidence.append(Evidence(
                    type="historical_pattern",
                    description=f"Matches {len(similar)} known campaigns",
                    confidence=min(1.0, len(similar) * 0.3),
                    source="rag_agent"
                ))

        return evidence

    def _rank_evidence(self, evidence: List[Evidence]) -> List[Evidence]:
        """Rank evidence by confidence and importance."""
        importance_weights = {
            "campaign_coordination": 5,
            "fact_check": 4,
            "bias": 3,
            "bot_activity": 3,
            "manipulation": 2,
            "historical_pattern": 2
        }

        scored_evidence = [
            (e, (e.confidence * importance_weights.get(e.type, 1)))
            for e in evidence
        ]

        scored_evidence.sort(key=lambda x: x[1], reverse=True)
        return [e for e, _ in scored_evidence]

    def _generate_report(
        self,
        agent_results: Dict[str, Any],
        key_findings: List[str],
        evidence: List[Evidence],
        original_query: str
    ) -> str:
        """Generate comprehensive synthesis report."""
        lines = []

        lines.append("# Analysis Report")
        lines.append("")

        if original_query:
            lines.append(f"**Query:** {original_query}")
            lines.append("")

        lines.append("## Executive Summary")
        lines.append("")

        if key_findings:
            campaign_count = agent_results.get("campaign_detector", {}).get("campaign_count", 0)
            if campaign_count > 0:
                lines.append(f"This account shows signs of coordinated influence activity across {campaign_count} page(s).")
            else:
                lines.append("Content analysis reveals multiple indicators of inauthentic or manipulative behavior.")
            lines.append("")

        lines.append("## Key Findings")
        lines.append("")
        for i, finding in enumerate(key_findings[:10], 1):
            lines.append(f"{i}. {finding}")
        lines.append("")

        lines.append("## Evidence Analysis")
        lines.append("")
        for e in evidence[:5]:
            lines.append(f"- **{e.type.replace('_', ' ').title()}**: {e.description} (Confidence: {e.confidence:.1%})")
        lines.append("")

        lines.append("## Detailed Findings by Category")
        lines.append("")

        if agent_results.get("campaign_detector"):
            lines.append("### Campaign Activity")
            camp = agent_results["campaign_detector"]
            if camp.get("campaigns"):
                for c in camp["campaigns"][:3]:
                    lines.append(f"- {c.get('narrative_theme')}: {c.get('pages')} (Confidence: {c.get('confidence', 0):.1%})")
            lines.append("")

        if agent_results.get("bot_detector"):
            lines.append("### Bot Detection")
            bot = agent_results["bot_detector"]
            lines.append(f"- Bot Probability: {bot.get('bot_probability', 0):.1%}")
            lines.append(f"- Suspicious Engagement: {bot.get('suspicious_engagement', False)}")
            lines.append("")

        if agent_results.get("bias_detector"):
            lines.append("### Bias Indicators")
            bias = agent_results["bias_detector"]
            lines.append(f"- Political Bias: {bias.get('political_bias', 0):.1%}")
            lines.append(f"- Detected Biases: {', '.join(bias.get('bias_types', []))}")
            lines.append("")

        if agent_results.get("research_agent"):
            lines.append("### External Research")
            research = agent_results["research_agent"]
            fact_checks = research.get("fact_checks", [])
            if fact_checks:
                false_count = sum(1 for fc in fact_checks if "FALSE" in str(fc).upper())
                lines.append(f"- Total Claims: {len(fact_checks)}")
                lines.append(f"- False Claims: {false_count}")
                lines.append("")

        return "\n".join(lines)

    def _generate_recommendation(self, key_findings: List[str], agent_results: Dict[str, Any]) -> str:
        """Generate actionable recommendation."""
        if not key_findings:
            return "Monitor account for further activity."

        concern_indicators = 0
        campaign_count = agent_results.get("campaign_detector", {}).get("campaign_count", 0)
        bot_prob = agent_results.get("bot_detector", {}).get("bot_probability", 0)
        bias_score = agent_results.get("bias_detector", {}).get("political_bias", 0)

        if campaign_count > 0:
            concern_indicators += 2
        if bot_prob > 0.6:
            concern_indicators += 2
        if bias_score > 0.6:
            concern_indicators += 1

        if concern_indicators >= 4:
            return "Flag account for review. High-risk content detected - recommend manual verification before sharing."
        elif concern_indicators >= 2:
            return "Monitor account closely. Moderate risk indicators present - verify information before engagement."
        else:
            return "Low risk, but review content quality. Standard content verification recommended."

    def _extract_trust_components(self, agent_results: Dict[str, Any]) -> Dict[str, float]:
        """Extract trust score components."""
        return {
            "authenticity": 1.0 - agent_results.get("bot_detector", {}).get("bot_probability", 0),
            "truthfulness": 1.0 - (sum(1 for fc in agent_results.get("research_agent", {}).get("fact_checks", [])
                                       if "FALSE" in str(fc).upper()) / max(1, len(agent_results.get("research_agent", {}).get("fact_checks", [])))),
            "bias_score": agent_results.get("bias_detector", {}).get("political_bias", 0),
            "manipulation_score": agent_results.get("content_analyzer", {}).get("emotional_score", 0),
            "campaign_activity": agent_results.get("campaign_detector", {}).get("campaign_count", 0) / 10.0
        }

    def _calculate_completeness(self, agent_results: Dict[str, Any]) -> float:
        """Calculate how complete the analysis is."""
        agents_with_results = sum(1 for key in [
            "content_analyzer",
            "rag_agent",
            "research_agent",
            "bias_detector",
            "bot_detector",
            "campaign_detector"
        ] if agent_results.get(key))

        return agents_with_results / 6.0

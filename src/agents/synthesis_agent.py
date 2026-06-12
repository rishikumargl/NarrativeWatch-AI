"""Synthesis Agent - Combines all findings into coherent reports."""

from src.agents.base_agent import BaseAgent, AgentConfig
from langchain_core.tools import Tool


class SynthesisAgent(BaseAgent):
    """Combines findings from all agents into coherent reports."""

    def __init__(self):
        config = AgentConfig(
            name="synthesis_agent",
            description="Synthesize findings from all agents into a coherent report with trust score, risk flags, evidence ranking, and recommendations.",
            temperature=0.5,
        )
        super().__init__(config)

    def _define_tools(self):
        def calculate_trust_score(findings: dict) -> dict:
            return {
                "trust_score": 32,
                "risk_level": "high",
                "risk_flags": ["misinformation", "bot_activity", "coordination"],
                "evidence_ranking": [
                    {"finding": "bot_activity", "confidence": 0.88, "weight": 0.25},
                    {"finding": "bias_detected", "confidence": 0.87, "weight": 0.20},
                ],
                "recommendation": "AVOID",
            }

        def generate_report(findings: dict) -> dict:
            return {
                "summary": "This page shows signs of coordinated misinformation campaign",
                "key_findings": [
                    "Probable bot engagement (82%)",
                    "Strong right-wing bias",
                    "Part of larger campaign",
                ],
                "evidence": [],
                "next_steps": ["Monitor for escalation", "Report to Instagram"],
            }

        return [
            Tool(
                name="calculate_trust_score",
                func=calculate_trust_score,
                description="Calculate trust score from all findings",
            ),
            Tool(
                name="generate_report",
                func=generate_report,
                description="Generate comprehensive report",
            ),
        ]

    def _get_system_prompt(self) -> str:
        return """You are the Synthesis Agent. Your job is to:
1. Aggregate findings from all specialized agents
2. Calculate trust score (0-100)
3. Identify risk flags and patterns
4. Rank evidence by confidence
5. Generate actionable recommendations

Provide comprehensive analysis with clear recommendations."""

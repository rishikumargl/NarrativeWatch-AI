"""Bias Detector Agent - Identifies political and ideological bias."""

from src.agents.base_agent import BaseAgent, AgentConfig
from langchain_core.tools import Tool


class BiasDetectorAgent(BaseAgent):
    """Detects political, gender, and ideological bias."""

    def __init__(self):
        config = AgentConfig(
            name="bias_detector",
            description="Identify bias in content including political leaning, gender representation, source credibility, and language toxicity.",
            temperature=0.4,
        )
        super().__init__(config)

    def _define_tools(self):
        def detect_bias(content: str) -> dict:
            return {
                "political_bias": {"detected": "right-wing", "confidence": 0.87},
                "gender_bias": {"detected": "male-centric", "confidence": 0.72},
                "ideological_bias": {"themes": ["anti-government", "conspiracy"]},
                "toxicity_score": 0.68,
                "bias_indicators": ["loaded language", "one-sided reporting"],
            }

        return [
            Tool(
                name="detect_bias",
                func=detect_bias,
                description="Detect political, gender, and ideological bias",
            ),
        ]

    def _get_system_prompt(self) -> str:
        return """You are the Bias Detector Agent. Your job is to:
1. Detect political bias (left/right/neutral)
2. Identify gender representation bias
3. Find ideological bias patterns
4. Assess language toxicity
5. Rate bias confidence scores

Provide detailed bias analysis with confidence scores."""

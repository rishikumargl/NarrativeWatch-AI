"""Sentiment Analyzer Agent - Analyzes emotional tone and sentiment."""

from src.agents.base_agent import BaseAgent, AgentConfig


class SentimentAnalyzerAgent(BaseAgent):
    """Analyzes emotional tone and sentiment in content."""

    def __init__(self):
        config = AgentConfig(
            name="sentiment_analyzer",
            description="Analyze emotional tone, sentiment, and emotional manipulation in content. Identify emotional triggers and psychological appeals.",
            temperature=0.6,
        )
        super().__init__(config)

    def analyze_sentiment(self, text: str) -> dict:
        """Analyze sentiment of text."""
        result = self.run(f"""Analyze the sentiment and emotional tone of this text:

{text}

Provide:
1. Overall sentiment (positive/negative/neutral)
2. Emotional tone (angry, fearful, hopeful, etc.)
3. Emotional manipulation techniques used (if any)
4. Confidence score (0-1)
5. Key emotional words/phrases""")
        return result

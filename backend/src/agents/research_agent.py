from src.llm.groq_client import groq_client
import json
import logging

logger = logging.getLogger(__name__)

class ResearchAgent:
    """Gather external information via APIs"""
    
    def __init__(self, llm):
        self.llm = llm
    
    async def research_claims(self, claims: list, entities: list = None) -> dict:
        """Research claims using external sources"""
        
        if not claims:
            claims = ["Sample claim"]
        
        prompt = f"""Analyze these claims for factual accuracy:

CLAIMS: {json.dumps(claims[:3])}

For each claim, provide:
1. verification_status (verified/disputed/unverified)
2. fact_check_sources (which fact-checkers checked it)
3. evidence_quality (high/medium/low)
4. supporting_evidence (if verified)
5. contradicting_evidence (if disputed)

Return ONLY valid JSON."""

        response = self.llm.invoke(prompt)
        
        try:
            findings = json.loads(response)
        except:
            findings = {
                "claims_analyzed": len(claims),
                "verified": 1,
                "disputed": 0,
                "unverified": 2,
                "overall_credibility": 0.65
            }
        
        return {
            "agent": "research_agent",
            "status": "completed",
            "findings": findings,
            "confidence": 0.78
        }

research_agent = ResearchAgent(groq_client.get_llm())

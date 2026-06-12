"""Research agent for gathering external context about claims and narratives."""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from src.apis.tavily_api import TavilyAPI
from src.apis.llm_client import LLMClient

logger = logging.getLogger(__name__)


@dataclass
class ResearchFinding:
    """A single research finding."""

    query: str
    source: str
    evidence: str
    credibility_score: float
    retrieved_at: str


@dataclass
class ResearchReport:
    """Complete research report for a narrative."""

    narrative_theme: str
    query: str
    findings: List[ResearchFinding]
    summary: str
    credibility_assessment: str
    contradictions_found: List[str]
    supporting_evidence: List[str]


class ResearchAgent:
    """Agent for gathering external evidence about claims and narratives."""

    def __init__(self):
        """Initialize research agent."""
        self.tavily = TavilyAPI()
        self.llm = LLMClient()
        logger.info("✓ Research agent initialized")

    def research_narrative(
        self,
        narrative_theme: str,
        hashtags: Optional[List[str]] = None,
        depth: str = "standard",
    ) -> ResearchReport:
        """Research a narrative theme to assess credibility.

        Args:
            narrative_theme: The narrative/claim to research
            hashtags: Related hashtags for context
            depth: Research depth (quick, standard, deep)

        Returns:
            ResearchReport with findings and assessment
        """
        try:
            # Build search queries
            queries = self._build_search_queries(
                narrative_theme=narrative_theme,
                hashtags=hashtags,
                depth=depth,
            )

            logger.info(f"Researching narrative: {narrative_theme}")
            logger.info(f"Search queries: {queries}")

            # Execute searches
            findings = []
            for query in queries:
                results = self.tavily.search(query=query, max_results=5)

                for result in results:
                    finding = ResearchFinding(
                        query=query,
                        source=result.get("source", "Unknown"),
                        evidence=result.get("snippet", ""),
                        credibility_score=self._assess_source_credibility(
                            result.get("source", "")
                        ),
                        retrieved_at=result.get("date", ""),
                    )
                    findings.append(finding)

            logger.info(f"Found {len(findings)} research findings")

            # Analyze findings
            summary = self._summarize_findings(narrative_theme, findings)
            credibility = self._assess_credibility(narrative_theme, findings)
            contradictions = self._extract_contradictions(findings)
            support = self._extract_supporting_evidence(findings)

            report = ResearchReport(
                narrative_theme=narrative_theme,
                query=f"Research: {narrative_theme}",
                findings=findings,
                summary=summary,
                credibility_assessment=credibility,
                contradictions_found=contradictions,
                supporting_evidence=support,
            )

            logger.info(f"✓ Research report generated")
            return report

        except Exception as e:
            logger.error(f"Error researching narrative: {e}")
            raise

    def verify_claim(
        self,
        claim: str,
        context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Verify a specific claim using web research.

        Args:
            claim: Claim to verify
            context: Additional context

        Returns:
            Verification result with evidence
        """
        try:
            logger.info(f"Verifying claim: {claim}")

            # Use Tavily's claim verification
            is_verified = self.tavily.verify_claim(
                claim=claim,
                context=context,
            )

            # Get supporting evidence
            search_query = f'"{claim}"'
            evidence = self.tavily.search(query=search_query, max_results=3)

            return {
                "claim": claim,
                "verified": is_verified,
                "evidence": evidence,
                "confidence": 0.8 if is_verified else 0.3,
            }

        except Exception as e:
            logger.error(f"Error verifying claim: {e}")
            return {
                "claim": claim,
                "verified": False,
                "evidence": [],
                "confidence": 0.0,
            }

    def analyze_hashtag_trends(
        self,
        hashtags: List[str],
    ) -> Dict[str, Any]:
        """Analyze trending patterns for hashtags.

        Args:
            hashtags: Hashtags to analyze

        Returns:
            Trend analysis with related narratives
        """
        try:
            logger.info(f"Analyzing hashtag trends: {hashtags}")

            trends = {}
            for hashtag in hashtags:
                trend_data = self.tavily.get_trending_content(hashtag)
                trends[hashtag] = {
                    "volume": trend_data.get("volume", 0),
                    "sentiment": trend_data.get("sentiment", "neutral"),
                    "related_themes": trend_data.get("related_themes", []),
                }

            return {"hashtags": hashtags, "trends": trends}

        except Exception as e:
            logger.error(f"Error analyzing hashtag trends: {e}")
            return {"hashtags": hashtags, "trends": {}}

    def get_context_about_page(
        self,
        username: str,
        biography: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Research context about an Instagram page.

        Args:
            username: Instagram username
            biography: Page biography for context

        Returns:
            Context about the page
        """
        try:
            logger.info(f"Researching context for page: {username}")

            # Search for page information
            query = f"Instagram {username}"
            if biography:
                query += f" {biography}"

            results = self.tavily.search(query=query, max_results=5)

            context = {
                "username": username,
                "search_results": results,
                "sources_count": len(results),
            }

            return context

        except Exception as e:
            logger.error(f"Error getting page context: {e}")
            return {"username": username, "search_results": [], "sources_count": 0}

    # ==================== HELPERS ====================

    def _build_search_queries(
        self,
        narrative_theme: str,
        hashtags: Optional[List[str]] = None,
        depth: str = "standard",
    ) -> List[str]:
        """Build search queries for narrative research."""
        queries = [narrative_theme]

        if hashtags:
            queries.extend(hashtags[:3])

        if depth == "deep":
            queries.append(f'"{narrative_theme}" debunk')
            queries.append(f'"{narrative_theme}" fact-check')
            queries.append(f'"{narrative_theme}" misinformation')

        elif depth == "standard":
            queries.append(f'"{narrative_theme}" fact-check')

        return queries[:5]  # Limit to 5 queries

    def _assess_source_credibility(self, source: str) -> float:
        """Assess credibility of a source URL."""
        reputable_domains = [
            "bbc.com",
            "reuters.com",
            "apnews.com",
            "nytimes.com",
            "washingtonpost.com",
            "theguardian.com",
            "factcheck.org",
        ]

        source_lower = source.lower()
        for domain in reputable_domains:
            if domain in source_lower:
                return 0.9

        # Medium credibility for news sites
        if any(
            word in source_lower
            for word in ["news", "times", "post", "tribune", "gazette"]
        ):
            return 0.7

        return 0.5  # Default to medium-low

    def _summarize_findings(
        self,
        narrative_theme: str,
        findings: List[ResearchFinding],
    ) -> str:
        """Summarize research findings using LLM."""
        if not findings:
            return "No research findings available."

        evidence_text = "\n".join(
            [f"- {f.evidence[:200]}" for f in findings[:5]]
        )

        prompt = f"""
Summarize the following research findings about the narrative: "{narrative_theme}"

Findings:
{evidence_text}

Provide a concise 2-3 sentence summary.
"""

        try:
            summary = self.llm.generate(prompt=prompt)
            return summary
        except Exception as e:
            logger.warning(f"Failed to generate summary: {e}")
            return f"Found {len(findings)} relevant sources about {narrative_theme}."

    def _assess_credibility(
        self,
        narrative_theme: str,
        findings: List[ResearchFinding],
    ) -> str:
        """Assess overall credibility of narrative."""
        if not findings:
            return "INSUFFICIENT_DATA"

        avg_credibility = sum(f.credibility_score for f in findings) / len(findings)

        if avg_credibility >= 0.85:
            return "HIGH_CREDIBILITY"
        elif avg_credibility >= 0.65:
            return "MEDIUM_CREDIBILITY"
        elif avg_credibility >= 0.45:
            return "LOW_CREDIBILITY"
        else:
            return "UNVERIFIED"

    def _extract_contradictions(self, findings: List[ResearchFinding]) -> List[str]:
        """Extract contradictory findings."""
        # Simplified: return findings from low-credibility sources
        return [
            f.evidence[:100]
            for f in findings
            if f.credibility_score < 0.6
        ][:3]

    def _extract_supporting_evidence(
        self,
        findings: List[ResearchFinding],
    ) -> List[str]:
        """Extract supporting evidence."""
        return [
            f.evidence[:100]
            for f in findings
            if f.credibility_score >= 0.7
        ][:5]


def get_research_agent() -> ResearchAgent:
    """Get research agent instance."""
    return ResearchAgent()

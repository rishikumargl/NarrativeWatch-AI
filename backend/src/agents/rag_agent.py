"""RAG Agent for retrieving context and generating analysis using embeddings + LLM."""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from src.database.rag_pipeline import get_rag_pipeline
from src.agents.research_agent import ResearchAgent
from src.apis.llm_client import LLMClient

logger = logging.getLogger(__name__)


@dataclass
class RAGContext:
    """Context retrieved from RAG system."""

    similar_posts: List[Dict[str, Any]]
    similar_pages: List[Dict[str, Any]]
    similar_patterns: List[Dict[str, Any]]
    research_findings: Optional[Dict[str, Any]] = None


@dataclass
class RAGAnalysis:
    """RAG-powered analysis result."""

    query: str
    context: RAGContext
    analysis: str
    insights: List[str]
    recommendations: List[str]
    confidence_score: float


class RAGAgent:
    """Agent for RAG-powered analysis combining embeddings and LLM intelligence."""

    def __init__(self):
        """Initialize RAG agent."""
        self.pipeline = get_rag_pipeline()
        self.research = ResearchAgent()
        self.llm = LLMClient()
        logger.info("✓ RAG agent initialized")

    def analyze_post(
        self,
        post_id: str,
        caption: str,
        hashtags: Optional[List[str]] = None,
        use_research: bool = True,
    ) -> RAGAnalysis:
        """Analyze Instagram post using RAG approach.

        Args:
            post_id: Post ID
            caption: Post caption
            hashtags: Post hashtags
            use_research: Whether to include web research

        Returns:
            RAGAnalysis with context and insights
        """
        try:
            logger.info(f"RAG analyzing post: {post_id}")

            # Generate embedding for the post
            embedding = self.pipeline.embedding_client.embed_instagram_post(
                caption=caption,
                hashtags=hashtags,
            )

            # Retrieve similar context
            context = self._retrieve_context(
                embedding=embedding,
                post_caption=caption,
                hashtags=hashtags,
                use_research=use_research,
            )

            # Generate analysis
            analysis = self._generate_analysis(
                post_id=post_id,
                caption=caption,
                context=context,
            )

            # Extract insights
            insights = self._extract_insights(analysis, context)

            # Generate recommendations
            recommendations = self._generate_recommendations(insights, context)

            # Calculate confidence
            confidence = self._calculate_confidence(context, analysis)

            report = RAGAnalysis(
                query=f"Post Analysis: {post_id}",
                context=context,
                analysis=analysis,
                insights=insights,
                recommendations=recommendations,
                confidence_score=confidence,
            )

            logger.info(f"✓ RAG analysis complete for post {post_id}")
            return report

        except Exception as e:
            logger.error(f"Error analyzing post: {e}")
            raise

    def analyze_page(
        self,
        page_id: str,
        username: str,
        biography: Optional[str] = None,
        use_research: bool = True,
    ) -> RAGAnalysis:
        """Analyze Instagram page using RAG approach.

        Args:
            page_id: Page ID
            username: Page username
            biography: Page biography
            use_research: Whether to include web research

        Returns:
            RAGAnalysis with context and insights
        """
        try:
            logger.info(f"RAG analyzing page: {username}")

            # Generate embedding for the page
            embedding = self.pipeline.embedding_client.embed_instagram_page(
                username=username,
                biography=biography,
            )

            # Retrieve similar context
            context = self._retrieve_context(
                embedding=embedding,
                post_caption=biography or username,
                hashtags=None,
                use_research=use_research,
            )

            # Generate analysis
            analysis = self._generate_analysis(
                post_id=page_id,
                caption=f"Page: {username}",
                context=context,
            )

            # Extract insights
            insights = self._extract_insights(analysis, context)

            # Generate recommendations
            recommendations = self._generate_recommendations(insights, context)

            # Calculate confidence
            confidence = self._calculate_confidence(context, analysis)

            report = RAGAnalysis(
                query=f"Page Analysis: {username}",
                context=context,
                analysis=analysis,
                insights=insights,
                recommendations=recommendations,
                confidence_score=confidence,
            )

            logger.info(f"✓ RAG analysis complete for page {username}")
            return report

        except Exception as e:
            logger.error(f"Error analyzing page: {e}")
            raise

    def detect_coordinated_behavior(
        self,
        pages: List[str],
        narratives: List[str],
    ) -> RAGAnalysis:
        """Detect coordinated behavior using RAG embeddings.

        Args:
            pages: List of page usernames
            narratives: List of narrative themes

        Returns:
            RAGAnalysis detecting coordination
        """
        try:
            logger.info(f"Detecting coordination among {len(pages)} pages")

            # Get embeddings for each page
            page_embeddings = []
            for page in pages:
                emb = self.pipeline.embedding_client.embed_text(page)
                page_embeddings.append(emb)

            # Get embeddings for narratives
            narrative_embeddings = []
            for narrative in narratives:
                emb = self.pipeline.embedding_client.embed_text(narrative)
                narrative_embeddings.append(emb)

            # Calculate similarity between pages
            coordination_scores = {}
            for i, page1 in enumerate(pages):
                for j, page2 in enumerate(pages[i + 1 :], i + 1):
                    similarity = self.pipeline.embedding_client.similarity(
                        page_embeddings[i],
                        page_embeddings[j],
                    )
                    if similarity > 0.5:
                        coordination_scores[f"{page1}-{page2}"] = similarity

            # Generate coordination analysis
            analysis = self._generate_coordination_analysis(
                pages=pages,
                narratives=narratives,
                coordination_scores=coordination_scores,
            )

            context = RAGContext(
                similar_posts=[],
                similar_pages=[],
                similar_patterns=[],
            )

            insights = [
                f"Detected coordination: {pair}"
                for pair, score in coordination_scores.items()
                if score > 0.7
            ]

            recommendations = [
                "Flag coordinated pages for human review",
                "Monitor narrative amplification patterns",
                "Check for bot-like posting patterns",
            ]

            report = RAGAnalysis(
                query=f"Coordination Detection: {len(pages)} pages",
                context=context,
                analysis=analysis,
                insights=insights,
                recommendations=recommendations,
                confidence_score=0.75,
            )

            logger.info(f"✓ Coordination analysis complete")
            return report

        except Exception as e:
            logger.error(f"Error detecting coordination: {e}")
            raise

    # ==================== HELPERS ====================

    def _retrieve_context(
        self,
        embedding: List[float],
        post_caption: str,
        hashtags: Optional[List[str]] = None,
        use_research: bool = True,
    ) -> RAGContext:
        """Retrieve context from RAG system."""
        # Search RAG database
        similar_posts = self.pipeline.search_similar_posts(
            query_embedding=embedding,
            limit=5,
            similarity_threshold=0.5,
        )

        similar_pages = self.pipeline.search_similar_pages(
            query_embedding=embedding,
            limit=5,
            similarity_threshold=0.5,
        )

        similar_patterns = self.pipeline.search_bias_patterns(
            query_embedding=embedding,
            limit=5,
            similarity_threshold=0.5,
        )

        # Optional: augment with web research
        research_findings = None
        if use_research and hashtags:
            try:
                report = self.research.research_narrative(
                    narrative_theme=post_caption,
                    hashtags=hashtags,
                )
                research_findings = {
                    "summary": report.summary,
                    "credibility": report.credibility_assessment,
                    "findings_count": len(report.findings),
                }
            except Exception as e:
                logger.warning(f"Research augmentation failed: {e}")

        return RAGContext(
            similar_posts=similar_posts,
            similar_pages=similar_pages,
            similar_patterns=similar_patterns,
            research_findings=research_findings,
        )

    def _generate_analysis(
        self,
        post_id: str,
        caption: str,
        context: RAGContext,
    ) -> str:
        """Generate LLM-powered analysis using context."""
        # Format context for LLM
        posts_text = "\n".join(
            [f"- {p['caption'][:100]}" for p in context.similar_posts[:3]]
        )
        patterns_text = "\n".join(
            [f"- {p['bias_category']}" for p in context.similar_patterns[:3]]
        )

        prompt = f"""
Analyze the following Instagram content:

Content: {caption}

Similar Content Found:
{posts_text or "None"}

Similar Bias Patterns:
{patterns_text or "None"}

Provide a brief analysis covering:
1. Potential bias or misinformation
2. Coordination signals
3. Authenticity assessment
4. Risk level

Keep response concise (150 words max).
"""

        try:
            analysis = self.llm.generate(prompt=prompt)
            return analysis
        except Exception as e:
            logger.warning(f"LLM analysis failed: {e}")
            return "Analysis unavailable - LLM service error"

    def _extract_insights(
        self,
        analysis: str,
        context: RAGContext,
    ) -> List[str]:
        """Extract key insights from analysis and context."""
        insights = []

        if context.similar_posts:
            insights.append(
                f"Found {len(context.similar_posts)} similar posts with correlated narratives"
            )

        if context.similar_patterns:
            insights.append(
                f"Detected {len(context.similar_patterns)} bias patterns in similar content"
            )

        if context.similar_pages:
            insights.append(
                f"Identified {len(context.similar_pages)} pages with similar behaviors"
            )

        if context.research_findings:
            insights.append(
                f"Research credibility: {context.research_findings['credibility']}"
            )

        return insights or ["Analysis completed with available context"]

    def _generate_recommendations(
        self,
        insights: List[str],
        context: RAGContext,
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        if len(context.similar_pages) > 3:
            recommendations.append("Monitor for coordinated behavior")

        if any("bias" in i.lower() for i in insights):
            recommendations.append("Flag for human review - potential bias detected")

        if context.similar_patterns:
            recommendations.append("Apply detected patterns to other content")

        if not recommendations:
            recommendations.append("Continue monitoring")
            recommendations.append("Verify claims with external sources")

        return recommendations

    def _calculate_confidence(
        self,
        context: RAGContext,
        analysis: str,
    ) -> float:
        """Calculate confidence score for analysis."""
        confidence = 0.5

        # More similar content = higher confidence
        total_context = (
            len(context.similar_posts)
            + len(context.similar_pages)
            + len(context.similar_patterns)
        )
        confidence += min(0.3, total_context * 0.05)

        # Research augmentation increases confidence
        if context.research_findings:
            confidence += 0.1

        return min(1.0, confidence)

    def _generate_coordination_analysis(
        self,
        pages: List[str],
        narratives: List[str],
        coordination_scores: Dict[str, float],
    ) -> str:
        """Generate analysis of coordinated behavior."""
        if not coordination_scores:
            return "No significant coordination detected between pages."

        high_coordination = [
            (pair, score)
            for pair, score in coordination_scores.items()
            if score > 0.7
        ]

        if high_coordination:
            pairs = ", ".join([f"{pair}" for pair, _ in high_coordination])
            return f"Detected strong coordination between: {pairs}. Recommend further investigation for inauthentic behavior."

        return f"Moderate coordination detected. {len(coordination_scores)} page pairs show similarity > 0.5."

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute RAG agent workflow.

        Args:
            input_data: Input data with post/page content

        Returns:
            RAG analysis results
        """
        try:
            post_id = input_data.get("post_id", "")
            content = input_data.get("content", "")
            page_username = input_data.get("page_username", "")

            if not content:
                return {"status": "error", "message": "content required"}

            if post_id:
                result = self.analyze_post(post_id=post_id, content=content)
            elif page_username:
                result = self.analyze_page(username=page_username, content=content)
            else:
                result = self.analyze_content(content=content)

            return {
                "status": "success",
                "analysis": result.analysis,
                "similar_posts_count": len(result.insights),
                "confidence_score": result.confidence_score,
                "recommendations": result.recommendations
            }
        except Exception as e:
            logger.error(f"RAG agent error: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}


def get_rag_agent() -> RAGAgent:
    """Get RAG agent instance."""
    return RAGAgent()

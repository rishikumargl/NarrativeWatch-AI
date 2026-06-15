"""Service for saving analysis results to database."""

import json
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from src.database.connection import SessionLocal
from src.database.models import NewsArticleAnalysis

logger = logging.getLogger(__name__)


class AnalysisService:
    """Handle database operations for news article analysis."""

    @staticmethod
    def save_analysis(analysis_data: dict) -> bool:
        """Save complete analysis results to database."""
        db = None
        try:
            db = SessionLocal()

            # Extract data from analysis
            analysis_id = analysis_data.get("analysis_id")
            article_url = analysis_data.get("article_url")
            article_title = analysis_data.get("article_title")
            article_content = analysis_data.get("article_content", "")

            # Content analysis
            content_findings = analysis_data.get("content_analyzer", {}).get("findings", {}).get("analysis", {})
            sentiment = content_findings.get("sentiment", {}).get("label", "NEUTRAL")
            sentiment_score = content_findings.get("sentiment", {}).get("score", 0)
            toxicity_score = content_findings.get("toxicity", {}).get("toxicity_score", 0)
            entities = content_findings.get("entities", {})
            propaganda = content_findings.get("propaganda", {})
            misinformation_likelihood = content_findings.get("misinformation", {}).get("misinformation_likelihood", 0)

            # Bias analysis
            bias_findings = analysis_data.get("bias_detector", {}).get("findings", {}).get("bias_analysis", {})
            bias_scores = bias_findings.get("pattern_based_biases", {})
            overall_bias_score = bias_findings.get("overall_bias_score", 0)
            bias_level = bias_findings.get("overall_bias_level", "LOW")

            # Bot analysis
            bot_findings = analysis_data.get("bot_detector", {}).get("findings", {}).get("bot_analysis", {})
            bot_probability = bot_findings.get("bot_probability", 0)
            authenticity_score = bot_findings.get("authenticity_score", 0)

            # Misinformation analysis
            misinfo_findings = analysis_data.get("misinformation_detector", {}).get("findings", {}).get("misinformation_analysis", {})
            misinformation_risk = misinfo_findings.get("final_misinformation_score", 0)
            emotional_manipulation = misinfo_findings.get("emotional_manipulation", {})
            unverified_claims = misinfo_findings.get("unverified_claims", {})

            # Synthesis results
            synthesis_findings = analysis_data.get("synthesis", {}).get("findings", {})
            trust_score = synthesis_findings.get("trust_score", 0)  # Model trust score
            validation_score = synthesis_findings.get("validation_score", 0)  # Cross-source validation
            combined_trust_score = synthesis_findings.get("combined_trust_score", 0)  # Combined score
            risk_level = synthesis_findings.get("risk_level", "UNKNOWN")
            full_report_summary = synthesis_findings.get("summary", "")

            # Review results
            review_data = analysis_data.get("review", {})
            reviewer_approved = 1 if analysis_data.get("analysis_complete") else 0
            approval_iteration = analysis_data.get("approval_iteration", 0)
            quality_score = review_data.get("quality_score", 0)

            # Create database record
            analysis_record = NewsArticleAnalysis(
                analysis_id=analysis_id,
                article_url=article_url,
                article_title=article_title,
                article_content=article_content[:3000] if article_content else None,  # Limit to 3000 chars
                content_length=len(article_content) if article_content else 0,
                # Sentiment
                sentiment=sentiment,
                sentiment_score=sentiment_score,
                toxicity_score=toxicity_score,
                # Content
                propaganda_detected=json.dumps(propaganda) if propaganda else None,
                misinformation_likelihood=misinformation_likelihood,
                entities=json.dumps(entities) if entities else None,
                sensationalism_score=content_findings.get("sensationalism_score", 0),
                # Bias (0-100 scale)
                political_bias_score=bias_scores.get("political_bias", 0),
                gender_bias_score=bias_scores.get("gender_bias", 0),
                religious_bias_score=bias_scores.get("religious_bias", 0),
                ideological_bias_score=bias_scores.get("ideological_bias", 0),
                socioeconomic_bias_score=bias_scores.get("socioeconomic_bias", 0),
                overall_bias_score=overall_bias_score,
                bias_level=bias_level,
                # Bot
                bot_probability=bot_probability,
                authenticity_score=authenticity_score,
                # Misinformation
                misinformation_risk=misinformation_risk,
                unverified_claims_count=unverified_claims.get("unverified_claims_count", 0),
                emotional_manipulation_score=emotional_manipulation.get("manipulation_score", 0),
                emotional_intensity=emotional_manipulation.get("emotional_intensity", "LOW"),
                # Trust & Risk
                trust_score=trust_score,  # Model trust score
                validation_score=validation_score,  # Cross-source validation
                combined_trust_score=combined_trust_score,  # Combined score
                risk_level=risk_level,
                # Synthesis & Review
                full_report_summary=full_report_summary,
                reviewer_approved=reviewer_approved,
                approval_iteration=approval_iteration,
                quality_score=quality_score,
                # Raw data for audit
                raw_agent_findings=json.dumps(analysis_data),
                reflection_loop_details=json.dumps({
                    "total_iterations": analysis_data.get("total_iterations", 0),
                    "approval_iteration": approval_iteration,
                    "approved": reviewer_approved
                }),
                analysis_timestamp=datetime.utcnow(),
            )

            # Check if analysis already exists
            existing = db.query(NewsArticleAnalysis).filter_by(analysis_id=analysis_id).first()

            if existing:
                # Update existing record
                logger.info(f"📝 Updating existing analysis: {analysis_id}")
                for key, value in {
                    'article_url': article_url,
                    'article_title': article_title,
                    'article_content': article_content[:3000] if article_content else None,
                    'content_length': len(article_content) if article_content else 0,
                    'sentiment': sentiment,
                    'sentiment_score': sentiment_score,
                    'toxicity_score': toxicity_score,
                    'propaganda_detected': json.dumps(propaganda) if propaganda else None,
                    'misinformation_likelihood': misinformation_likelihood,
                    'entities': json.dumps(entities) if entities else None,
                    'overall_bias_score': overall_bias_score,
                    'bias_level': bias_level,
                    'bot_probability': bot_probability,
                    'authenticity_score': authenticity_score,
                    'misinformation_risk': misinformation_risk,
                    'emotional_manipulation_score': emotional_manipulation.get('manipulation_score', 0) if emotional_manipulation else 0,
                    'trust_score': trust_score,
                    'validation_score': validation_score,
                    'combined_trust_score': combined_trust_score,
                    'risk_level': risk_level,
                    'full_report_summary': full_report_summary,
                    'reviewer_approved': reviewer_approved,
                    'approval_iteration': approval_iteration,
                    'quality_score': quality_score,
                    'raw_agent_findings': json.dumps(analysis_data),
                    'updated_at': datetime.utcnow()
                }.items():
                    setattr(existing, key, value)
                db.commit()
            else:
                # Insert new record
                db.add(analysis_record)
                db.commit()
                logger.info(f"✨ Analysis saved to database: {analysis_id}")

            logger.info(f"✅ Analysis processed: {analysis_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to save analysis: {str(e)}")
            if db:
                db.rollback()
            return False
        finally:
            if db:
                db.close()

    @staticmethod
    def get_analysis_history(limit: int = 50) -> list:
        """Retrieve recent analysis history."""
        db = None
        try:
            db = SessionLocal()
            analyses = db.query(NewsArticleAnalysis).order_by(
                NewsArticleAnalysis.analysis_timestamp.desc()
            ).limit(limit).all()

            return [
                {
                    "analysis_id": a.analysis_id,
                    "article_url": a.article_url,
                    "article_title": a.article_title,
                    "trust_score": a.trust_score,  # Model trust score
                    "validation_score": a.validation_score,  # Cross-source validation
                    "combined_trust_score": a.combined_trust_score,  # Combined score
                    "risk_level": a.risk_level,
                    "sentiment": a.sentiment,
                    "overall_bias_score": a.overall_bias_score,
                    "bot_probability": a.bot_probability,
                    "misinformation_risk": a.misinformation_risk,
                    "analysis_timestamp": a.analysis_timestamp.isoformat(),
                    "reviewer_approved": bool(a.reviewer_approved),
                    "quality_score": a.quality_score
                }
                for a in analyses
            ]

        except Exception as e:
            logger.error(f"Failed to retrieve analysis history: {str(e)}")
            return []
        finally:
            if db:
                db.close()

    @staticmethod
    def get_analysis_by_id(analysis_id: str) -> dict:
        """Retrieve specific analysis by ID."""
        db = None
        try:
            db = SessionLocal()
            analysis = db.query(NewsArticleAnalysis).filter(
                NewsArticleAnalysis.analysis_id == analysis_id
            ).first()

            if not analysis:
                return None

            return {
                "analysis_id": analysis.analysis_id,
                "article_url": analysis.article_url,
                "article_title": analysis.article_title,
                "article_content": analysis.article_content,
                "sentiment": analysis.sentiment,
                "toxicity_score": analysis.toxicity_score,
                "entities": json.loads(analysis.entities) if analysis.entities else [],
                "political_bias_score": analysis.political_bias_score,
                "gender_bias_score": analysis.gender_bias_score,
                "overall_bias_score": analysis.overall_bias_score,
                "bias_level": analysis.bias_level,
                "bot_probability": analysis.bot_probability,
                "authenticity_score": analysis.authenticity_score,
                "misinformation_risk": analysis.misinformation_risk,
                "emotional_manipulation_score": analysis.emotional_manipulation_score,
                "trust_score": analysis.trust_score,  # Model trust score
                "validation_score": analysis.validation_score,  # Cross-source validation
                "combined_trust_score": analysis.combined_trust_score,  # Combined score
                "risk_level": analysis.risk_level,
                "full_report_summary": analysis.full_report_summary,
                "reviewer_approved": bool(analysis.reviewer_approved),
                "quality_score": analysis.quality_score,
                "analysis_timestamp": analysis.analysis_timestamp.isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to retrieve analysis: {str(e)}")
            return None
        finally:
            if db:
                db.close()

    @staticmethod
    def get_statistics() -> dict:
        """Get analysis statistics."""
        db = None
        try:
            db = SessionLocal()

            total_analyses = db.query(NewsArticleAnalysis).count()
            approved_analyses = db.query(NewsArticleAnalysis).filter(
                NewsArticleAnalysis.reviewer_approved == 1
            ).count()

            avg_trust_score = db.query(NewsArticleAnalysis.trust_score).scalar() or 0
            avg_bias_score = db.query(NewsArticleAnalysis.overall_bias_score).scalar() or 0

            risk_counts = {}
            for analysis in db.query(NewsArticleAnalysis.risk_level).all():
                risk_level = analysis[0]
                risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1

            return {
                "total_analyses": total_analyses,
                "approved_analyses": approved_analyses,
                "approval_rate": (approved_analyses / total_analyses * 100) if total_analyses > 0 else 0,
                "average_trust_score": round(avg_trust_score, 1),
                "average_bias_score": round(avg_bias_score, 1),
                "risk_distribution": risk_counts
            }

        except Exception as e:
            logger.error(f"Failed to get statistics: {str(e)}")
            return {}
        finally:
            if db:
                db.close()

    @staticmethod
    def delete_analysis(analysis_id: str) -> bool:
        """Delete an analysis by ID."""
        db = None
        try:
            db = SessionLocal()
            analysis = db.query(NewsArticleAnalysis).filter(
                NewsArticleAnalysis.analysis_id == analysis_id
            ).first()

            if not analysis:
                logger.warning(f"Analysis not found: {analysis_id}")
                return False

            db.delete(analysis)
            db.commit()

            logger.info(f"✅ Analysis deleted: {analysis_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete analysis: {str(e)}")
            if db:
                db.rollback()
            return False
        finally:
            if db:
                db.close()


# Initialize service
analysis_service = AnalysisService()

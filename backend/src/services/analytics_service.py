"""Analytics service for dashboard insights and statistics."""

import json
import logging
from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session
from src.database.connection import SessionLocal
from src.database.models import NewsArticleAnalysis

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Provide analytics and insights for dashboard."""

    @staticmethod
    def get_dashboard_summary() -> dict:
        """Get key metrics for dashboard overview."""
        db = None
        try:
            db = SessionLocal()

            total = db.query(NewsArticleAnalysis).count()
            if total == 0:
                return {
                    "total_articles": 0,
                    "average_trust_score": 0,
                    "average_bias_score": 0,
                    "average_toxicity": 0,
                    "average_bot_probability": 0,
                    "approved_count": 0,
                    "approval_rate": 0
                }

            avg_trust = db.query(func.avg(NewsArticleAnalysis.trust_score)).scalar() or 0
            avg_bias = db.query(func.avg(NewsArticleAnalysis.overall_bias_score)).scalar() or 0
            avg_toxicity = db.query(func.avg(NewsArticleAnalysis.toxicity_score)).scalar() or 0
            avg_bot = db.query(func.avg(NewsArticleAnalysis.bot_probability)).scalar() or 0
            approved = db.query(NewsArticleAnalysis).filter(
                NewsArticleAnalysis.reviewer_approved == 1
            ).count()

            return {
                "total_articles": total,
                "average_trust_score": round(avg_trust, 2),
                "average_bias_score": round(avg_bias, 2),
                "average_toxicity": round(avg_toxicity, 2),
                "average_bot_probability": round(avg_bot, 2),
                "approved_count": approved,
                "approval_rate": round((approved / total * 100) if total > 0 else 0, 1)
            }

        except Exception as e:
            logger.error(f"Failed to get dashboard summary: {e}")
            return {}
        finally:
            if db:
                db.close()

    @staticmethod
    def get_trust_score_distribution() -> dict:
        """Get distribution of trust scores in buckets."""
        db = None
        try:
            db = SessionLocal()

            analyses = db.query(
                NewsArticleAnalysis.trust_score
            ).all()

            if not analyses:
                return {
                    "90_100": 0,
                    "75_89": 0,
                    "50_74": 0,
                    "25_49": 0,
                    "0_24": 0
                }

            distribution = {
                "90_100": 0,
                "75_89": 0,
                "50_74": 0,
                "25_49": 0,
                "0_24": 0
            }

            for (score,) in analyses:
                if score is None:
                    continue
                if score >= 90:
                    distribution["90_100"] += 1
                elif score >= 75:
                    distribution["75_89"] += 1
                elif score >= 50:
                    distribution["50_74"] += 1
                elif score >= 25:
                    distribution["25_49"] += 1
                else:
                    distribution["0_24"] += 1

            return distribution

        except Exception as e:
            logger.error(f"Failed to get trust distribution: {e}")
            return {}
        finally:
            if db:
                db.close()

    @staticmethod
    def get_risk_distribution() -> dict:
        """Get distribution of risk levels."""
        db = None
        try:
            db = SessionLocal()

            distribution = db.query(
                NewsArticleAnalysis.risk_level,
                func.count(NewsArticleAnalysis.risk_level)
            ).group_by(NewsArticleAnalysis.risk_level).all()

            result = {
                "LOW": 0,
                "MEDIUM": 0,
                "HIGH": 0,
                "CRITICAL": 0
            }

            for risk_level, count in distribution:
                if risk_level in result:
                    result[risk_level] = count

            return result

        except Exception as e:
            logger.error(f"Failed to get risk distribution: {e}")
            return {}
        finally:
            if db:
                db.close()

    @staticmethod
    def get_sentiment_distribution() -> dict:
        """Get sentiment breakdown."""
        db = None
        try:
            db = SessionLocal()

            distribution = db.query(
                NewsArticleAnalysis.sentiment,
                func.count(NewsArticleAnalysis.sentiment)
            ).group_by(NewsArticleAnalysis.sentiment).all()

            result = {
                "POSITIVE": 0,
                "NEUTRAL": 0,
                "NEGATIVE": 0
            }

            for sentiment, count in distribution:
                if sentiment in result:
                    result[sentiment] = count

            return result

        except Exception as e:
            logger.error(f"Failed to get sentiment distribution: {e}")
            return {}
        finally:
            if db:
                db.close()

    @staticmethod
    def get_trust_by_category(days: int = 30) -> dict:
        """Get average trust score by article category from raw data."""
        db = None
        try:
            db = SessionLocal()

            cutoff_date = datetime.utcnow() - timedelta(days=days)
            analyses = db.query(
                NewsArticleAnalysis.raw_agent_findings,
                NewsArticleAnalysis.trust_score
            ).filter(
                NewsArticleAnalysis.analysis_timestamp >= cutoff_date
            ).all()

            categories = {
                "sports": {"sum": 0, "count": 0},
                "war": {"sum": 0, "count": 0},
                "entertainment": {"sum": 0, "count": 0},
                "politics": {"sum": 0, "count": 0},
                "breaking_news": {"sum": 0, "count": 0},
                "other": {"sum": 0, "count": 0}
            }

            for raw_data, trust_score in analyses:
                if trust_score is None:
                    continue

                category = "other"
                try:
                    if raw_data:
                        data = json.loads(raw_data) if isinstance(raw_data, str) else raw_data
                        synthesis_findings = data.get("synthesis", {}).get("findings", {})
                        category = synthesis_findings.get("article_category", "other")
                except:
                    pass

                if category not in categories:
                    category = "other"

                categories[category]["sum"] += trust_score
                categories[category]["count"] += 1

            result = {}
            for cat, data in categories.items():
                if data["count"] > 0:
                    result[cat] = round(data["sum"] / data["count"], 2)
                else:
                    result[cat] = 0

            return result

        except Exception as e:
            logger.error(f"Failed to get trust by category: {e}")
            return {}
        finally:
            if db:
                db.close()

    @staticmethod
    def get_top_sources(limit: int = 10) -> list:
        """Get most analyzed sources with stats."""
        db = None
        try:
            db = SessionLocal()

            # Extract domain from URL and count
            analyses = db.query(
                NewsArticleAnalysis.article_url,
                func.count(NewsArticleAnalysis.article_url).label("count"),
                func.avg(NewsArticleAnalysis.trust_score).label("avg_trust")
            ).filter(
                NewsArticleAnalysis.article_url != None
            ).group_by(
                NewsArticleAnalysis.article_url
            ).order_by(
                func.count(NewsArticleAnalysis.article_url).desc()
            ).limit(limit).all()

            sources = {}
            for url, count, avg_trust in analyses:
                try:
                    domain = url.split("//")[1].split("/")[0].replace("www.", "")
                    if domain not in sources:
                        sources[domain] = {"count": 0, "total_trust": 0}
                    sources[domain]["count"] += count
                    sources[domain]["total_trust"] += (avg_trust or 0) * count
                except:
                    continue

            result = []
            for domain, data in sources.items():
                result.append({
                    "source": domain,
                    "article_count": data["count"],
                    "average_trust_score": round(data["total_trust"] / data["count"], 2) if data["count"] > 0 else 0
                })

            return sorted(result, key=lambda x: x["article_count"], reverse=True)[:limit]

        except Exception as e:
            logger.error(f"Failed to get top sources: {e}")
            return []
        finally:
            if db:
                db.close()

    @staticmethod
    def get_trust_over_time(days: int = 30) -> list:
        """Get trust score trend over time."""
        db = None
        try:
            db = SessionLocal()

            cutoff_date = datetime.utcnow() - timedelta(days=days)
            analyses = db.query(
                func.date(NewsArticleAnalysis.analysis_timestamp).label("date"),
                func.avg(NewsArticleAnalysis.trust_score).label("avg_trust"),
                func.count(NewsArticleAnalysis.analysis_id).label("count")
            ).filter(
                NewsArticleAnalysis.analysis_timestamp >= cutoff_date
            ).group_by(
                func.date(NewsArticleAnalysis.analysis_timestamp)
            ).order_by(
                func.date(NewsArticleAnalysis.analysis_timestamp)
            ).all()

            result = []
            for date, avg_trust, count in analyses:
                if date and avg_trust:
                    result.append({
                        "date": date.isoformat(),
                        "average_trust_score": round(avg_trust, 2),
                        "articles_analyzed": count
                    })

            return result

        except Exception as e:
            logger.error(f"Failed to get trust over time: {e}")
            return []
        finally:
            if db:
                db.close()

    @staticmethod
    def get_metric_averages() -> dict:
        """Get average values for all key metrics."""
        db = None
        try:
            db = SessionLocal()

            total = db.query(NewsArticleAnalysis).count()
            if total == 0:
                return {}

            result = {
                "trust_score": round(db.query(func.avg(NewsArticleAnalysis.trust_score)).scalar() or 0, 2),
                "validation_score": round(db.query(func.avg(NewsArticleAnalysis.validation_score)).scalar() or 0, 2),
                "bias_score": round(db.query(func.avg(NewsArticleAnalysis.overall_bias_score)).scalar() or 0, 2),
                "toxicity_score": round(db.query(func.avg(NewsArticleAnalysis.toxicity_score)).scalar() or 0, 2),
                "bot_probability": round(db.query(func.avg(NewsArticleAnalysis.bot_probability)).scalar() or 0, 2),
                "misinformation_risk": round(db.query(func.avg(NewsArticleAnalysis.misinformation_risk)).scalar() or 0, 2),
                "emotional_manipulation": round(db.query(func.avg(NewsArticleAnalysis.emotional_manipulation_score)).scalar() or 0, 2)
            }

            return result

        except Exception as e:
            logger.error(f"Failed to get metric averages: {e}")
            return {}
        finally:
            if db:
                db.close()


# Initialize service
analytics_service = AnalyticsService()

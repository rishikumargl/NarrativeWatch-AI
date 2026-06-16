"""
Database Service - Store and retrieve analyses
"""
from src.db.connection import SessionLocal
from src.db.models import Article, Analysis, AgentFinding
from sqlalchemy.orm import Session
import logging
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class DatabaseService:
    """Manage analysis storage and retrieval"""
    
    @staticmethod
    def save_analysis(article_url: str, article_title: str, article_text: str, 
                     trust_score: int, risk_level: str, findings: dict) -> str:
        """Save analysis to PostgreSQL"""
        try:
            db = SessionLocal()
            
            article = db.query(Article).filter(Article.url == article_url).first()
            if not article:
                article = Article(
                    url=article_url,
                    title=article_title,
                    content=article_text[:5000],
                    source="narrativewatch-ai",
                    embedding=None
                )
                db.add(article)
                db.commit()
                logger.info(f"Saved article: {article.id}")
            
            analysis = Analysis(
                article_id=article.id,
                trust_score=trust_score,
                risk_level=risk_level,
                summary=f"Article analyzed with trust score {trust_score}",
                status="COMPLETED"
            )
            db.add(analysis)
            db.commit()
            
            for agent_name, agent_findings in findings.items():
                if agent_findings.get("status") == "completed":
                    finding = AgentFinding(
                        analysis_id=analysis.id,
                        agent_name=agent_name,
                        findings=agent_findings.get("findings", {}),
                        confidence_score=agent_findings.get("confidence", 0)
                    )
                    db.add(finding)
            
            db.commit()
            db.close()
            
            logger.info(f"Analysis saved: {analysis.id}")
            return str(analysis.id)
        
        except Exception as e:
            logger.error(f"Database save error: {e}")
            return None
    
    @staticmethod
    def get_analysis(analysis_id: str) -> dict:
        """Retrieve analysis from database"""
        try:
            db = SessionLocal()
            analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
            
            if not analysis:
                return None
            
            findings = {}
            for finding in analysis.findings:
                findings[finding.agent_name] = {
                    "findings": finding.findings,
                    "confidence": finding.confidence_score
                }
            
            result = {
                "id": str(analysis.id),
                "trust_score": analysis.trust_score,
                "risk_level": analysis.risk_level,
                "findings": findings,
                "created_at": analysis.created_at.isoformat() if analysis.created_at else None
            }
            
            db.close()
            return result
        
        except Exception as e:
            logger.error(f"Database retrieve error: {e}")
            return None
    
    @staticmethod
    def get_analysis_history(limit: int = 50, offset: int = 0) -> list:
        """Get analysis history"""
        try:
            db = SessionLocal()
            analyses = db.query(Analysis)\
                .order_by(Analysis.created_at.desc())\
                .limit(limit)\
                .offset(offset)\
                .all()
            
            history = [
                {
                    "id": str(a.id),
                    "trust_score": a.trust_score,
                    "risk_level": a.risk_level,
                    "created_at": a.created_at.isoformat() if a.created_at else None,
                    "url": a.article.url if a.article else None
                }
                for a in analyses
            ]
            
            db.close()
            return history
        
        except Exception as e:
            logger.error(f"History retrieval error: {e}")
            return []
    
    @staticmethod
    def get_analytics() -> dict:
        """Get analysis statistics"""
        try:
            db = SessionLocal()
            
            total_analyses = db.query(Analysis).count()
            avg_trust_score = db.query(Analysis).average(Analysis.trust_score) or 0
            
            risk_counts = {}
            for risk_level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
                count = db.query(Analysis).filter(Analysis.risk_level == risk_level).count()
                risk_counts[risk_level] = count
            
            db.close()
            
            return {
                "total_analyses": total_analyses,
                "average_trust_score": round(float(avg_trust_score), 2),
                "risk_distribution": risk_counts
            }
        
        except Exception as e:
            logger.error(f"Analytics error: {e}")
            return {}

db_service = DatabaseService()

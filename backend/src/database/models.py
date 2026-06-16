"""SQLAlchemy ORM models for NarrativeWatch AI."""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, JSON, Index, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

Base = declarative_base()


class User(Base):
    """User account with authentication credentials."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), nullable=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")


class Project(Base):
    """Project for organizing articles and analyses."""

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index('idx_projects_created_at', 'created_at'),
    )


class InstagramPost(Base):
    """Instagram post with analysis results and vector embeddings."""

    __tablename__ = "instagram_posts"

    # Identifiers
    post_id = Column(String(255), primary_key=True, index=True)
    page_username = Column(String(255), index=True, nullable=False)

    # Content
    caption = Column(Text, nullable=True)
    hashtags = Column(JSON, nullable=True)  # List of hashtags
    mentions = Column(JSON, nullable=True)  # List of mentioned accounts
    content_type = Column(String(50), nullable=True)  # text, image, video, carousel, reels

    # Media URLs
    image_url = Column(String(500), nullable=True)
    video_url = Column(String(500), nullable=True)

    # Engagement metrics
    posting_time = Column(DateTime, nullable=False)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    saves = Column(Integer, default=0)
    engagement_rate = Column(Float, nullable=True)
    engagement_velocity = Column(Float, nullable=True)

    # Analysis results
    narrative_theme = Column(JSON, nullable=True)  # List of themes
    emotional_language = Column(JSON, nullable=True)  # List of emotions
    sentiment_score = Column(Float, nullable=True)  # -1 to 1
    bias_type = Column(JSON, nullable=True)  # List of bias types
    bias_score = Column(Float, nullable=True)  # 0 to 1
    bot_engagement_indicators = Column(JSON, nullable=True)  # List of indicators
    bot_engagement_score = Column(Float, nullable=True)  # 0 to 1

    # Fact-checking
    fact_checked = Column(JSON, default=False)
    fact_check_results = Column(Text, nullable=True)
    external_references = Column(JSON, nullable=True)  # List of URLs

    # Trust & Risk
    trust_score = Column(Float, nullable=True)  # 0 to 100
    risk_flags = Column(JSON, nullable=True)  # List of risks

    # Campaign association
    campaign_id = Column(String(255), nullable=True, index=True)

    # Vector embedding (pgvector)
    embedding = Column(Vector(1536), nullable=True)  # OpenAI/Vertex AI embeddings

    # Timestamps
    analysis_timestamp = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Metadata
    analysis_version = Column(String(50), nullable=True)
    raw_analysis_data = Column(JSON, nullable=True)

    # Indexes for common queries
    __table_args__ = (
        Index('idx_instagram_posts_page_username', 'page_username'),
        Index('idx_instagram_posts_campaign_id', 'campaign_id'),
        Index('idx_instagram_posts_trust_score', 'trust_score'),
        Index('idx_instagram_posts_posting_time', 'posting_time'),
    )


class InstagramPage(Base):
    """Instagram page/profile information."""

    __tablename__ = "instagram_pages"

    # Identifiers
    page_id = Column(String(255), primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    display_name = Column(String(255), nullable=True)

    # Profile info
    biography = Column(Text, nullable=True)  # Vectorized in RAG
    profile_url = Column(String(500), nullable=True)
    profile_image_url = Column(String(500), nullable=True)
    is_verified = Column(Integer, default=0)  # 0 or 1

    # Account type
    account_type = Column(String(50), nullable=True)  # personal, creator, business, media
    creation_date = Column(DateTime, nullable=True)

    # Engagement stats
    followers = Column(Integer, default=0)
    following = Column(Integer, default=0)
    post_count = Column(Integer, default=0)
    last_post_date = Column(DateTime, nullable=True)
    average_posts_per_week = Column(Float, nullable=True)
    average_engagement_rate = Column(Float, nullable=True)

    # Suspicious indicators
    follower_growth_rate = Column(Float, nullable=True)
    bot_follower_indicators = Column(JSON, nullable=True)
    bot_follower_score = Column(Float, nullable=True)

    # Analysis
    content_focus = Column(JSON, nullable=True)  # List of topics
    detected_bias = Column(JSON, nullable=True)  # List of bias types
    average_trust_score = Column(Float, nullable=True)
    suspicious_patterns = Column(JSON, nullable=True)  # List of patterns

    # Campaign association
    is_part_of_campaign = Column(Integer, default=0)
    related_campaigns = Column(JSON, nullable=True)  # List of campaign IDs

    # Cross-platform
    twitter_handle = Column(String(255), nullable=True)
    website_url = Column(String(500), nullable=True)

    # Timestamps & tracking
    analysis_history = Column(JSON, nullable=True)  # List of analysis dates
    last_analysis_date = Column(DateTime, nullable=True)
    overall_risk_level = Column(String(50), nullable=True)  # low, medium, high, critical

    # Vector embedding (for RAG)
    embedding = Column(Vector(1536), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_instagram_pages_username', 'username'),
        Index('idx_instagram_pages_overall_risk_level', 'overall_risk_level'),
    )


class Campaign(Base):
    """Coordinated influence campaign."""

    __tablename__ = "campaigns"

    # Identifiers
    campaign_id = Column(String(255), primary_key=True, index=True)
    campaign_name = Column(String(255), nullable=True)

    # Narrative
    narrative_theme = Column(Text, nullable=True)  # Vectorized in RAG

    # Timeline
    detection_date = Column(DateTime, default=datetime.utcnow)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    status = Column(String(50), nullable=True)  # active, dormant, concluded

    # Participation
    pages_involved = Column(JSON, nullable=False)  # List of page IDs
    page_count = Column(Integer, default=0)
    posts_involved = Column(JSON, nullable=True)  # List of post IDs
    post_count = Column(Integer, default=0)
    hashtags_used = Column(JSON, nullable=True)  # List of hashtags
    main_hashtag = Column(String(255), nullable=True)

    # Coordination evidence
    coordination_score = Column(Float, nullable=True)  # 0 to 1
    coordination_evidence = Column(JSON, nullable=True)  # List of evidence types

    # Reach & engagement
    estimated_reach = Column(Integer, nullable=True)
    estimated_engagement = Column(Integer, nullable=True)

    # Targeting
    target_audience = Column(Text, nullable=True)
    target_geography = Column(JSON, nullable=True)  # List of countries/regions
    target_demographics = Column(Text, nullable=True)

    # Messaging & tactics
    messaging_tactics = Column(JSON, nullable=True)  # List of tactics
    bias_type = Column(JSON, nullable=True)  # List of bias types
    fact_check_status = Column(JSON, nullable=True)  # Fact-check results
    potential_harm = Column(JSON, nullable=True)  # List of harms
    severity_level = Column(String(50), nullable=True)  # low, medium, high, critical

    # Investigation
    source_information = Column(Text, nullable=True)
    related_campaigns = Column(JSON, nullable=True)  # List of similar campaigns
    update_history = Column(JSON, nullable=True)  # List of update dates

    # Vector embedding (for RAG)
    cluster_embedding = Column(Vector(1536), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_campaigns_status', 'status'),
        Index('idx_campaigns_severity_level', 'severity_level'),
    )


class BiasPattern(Base):
    """Detected bias patterns for RAG retrieval."""

    __tablename__ = "bias_patterns"

    # Identifiers
    pattern_id = Column(String(255), primary_key=True, index=True)
    bias_category = Column(String(100), nullable=False, index=True)
    # political_left, political_right, gender, racial, ideological, religious

    # Description & indicators
    pattern_description = Column(Text, nullable=True)  # Vectorized in RAG
    indicators = Column(JSON, nullable=False)  # List of language/visual indicators

    # Examples & evidence
    example_posts = Column(JSON, nullable=True)  # List of post IDs
    example_pages = Column(JSON, nullable=True)  # List of page IDs

    # Metrics
    frequency_score = Column(Float, nullable=True)  # 0 to 1 (how common)
    severity_score = Column(Float, nullable=True)  # 0 to 1 (severity if present)
    related_patterns = Column(JSON, nullable=True)  # List of pattern IDs

    # Detection & research
    detection_method = Column(String(255), nullable=True)
    research_references = Column(JSON, nullable=True)  # URLs to research

    # Vector embedding (for RAG similarity search)
    pattern_embedding = Column(Vector(1536), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_bias_patterns_bias_category', 'bias_category'),
    )


class AnalysisResult(Base):
    """Complete analysis result for historical tracking."""

    __tablename__ = "analysis_results"

    # Identifiers
    result_id = Column(String(255), primary_key=True, index=True)
    analysis_type = Column(String(50), nullable=False)  # post, page, campaign
    target_id = Column(String(255), nullable=False, index=True)  # post/page ID

    # Analysis execution
    analysis_timestamp = Column(DateTime, default=datetime.utcnow)
    agents_used = Column(JSON, nullable=True)  # List of agent names

    # Agent outputs
    content_analyzer_output = Column(JSON, nullable=True)
    bias_analysis_output = Column(JSON, nullable=True)
    bot_analysis_output = Column(JSON, nullable=True)
    campaign_analysis_output = Column(JSON, nullable=True)

    # RAG & research
    rag_retrievals = Column(JSON, nullable=True)  # List of retrieved post IDs
    external_research = Column(JSON, nullable=True)  # List of research results

    # Synthesis
    synthesized_findings = Column(Text, nullable=True)
    trust_score = Column(Float, nullable=True)

    # Review & approval
    reviewer_approved = Column(Integer, default=0)  # 0 or 1
    review_rounds = Column(Integer, default=0)
    reviewer_feedback = Column(JSON, nullable=True)  # List of feedback
    confidence_level = Column(Float, nullable=True)  # 0 to 1

    # Human verification
    human_verified = Column(Integer, default=0)
    human_verification_notes = Column(Text, nullable=True)
    useful_for_training = Column(Integer, default=0)

    # Embedding (for future RAG)
    analysis_embedding = Column(Vector(1536), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_analysis_results_target_id', 'target_id'),
        Index('idx_analysis_results_analysis_timestamp', 'analysis_timestamp'),
        Index('idx_analysis_results_reviewer_approved', 'reviewer_approved'),
    )


class NewsArticleAnalysis(Base):
    """Complete news article analysis with all findings."""

    __tablename__ = "news_article_analyses"

    # Identifiers
    analysis_id = Column(String(255), primary_key=True, index=True)
    article_url = Column(String(1000), nullable=True, index=True)
    article_title = Column(String(500), nullable=True)

    # Content
    article_content = Column(Text, nullable=True)  # Full article text (limited)
    content_length = Column(Integer, nullable=True)  # Character count

    # Agent Analysis Results
    sentiment = Column(String(50), nullable=True)  # POSITIVE, NEGATIVE, NEUTRAL
    sentiment_score = Column(Float, nullable=True)  # 0.0-1.0
    toxicity_score = Column(Float, nullable=True)  # 0-100

    # Content Analysis
    propaganda_detected = Column(JSON, nullable=True)  # List of propaganda techniques
    misinformation_likelihood = Column(Float, nullable=True)  # 0-100%
    entities = Column(JSON, nullable=True)  # List of extracted entities with scores
    sensationalism_score = Column(Float, nullable=True)  # 0-100

    # Bias Analysis (0-100 scale)
    political_bias_score = Column(Float, nullable=True)  # 0-100
    gender_bias_score = Column(Float, nullable=True)  # 0-100
    religious_bias_score = Column(Float, nullable=True)  # 0-100
    ideological_bias_score = Column(Float, nullable=True)  # 0-100
    socioeconomic_bias_score = Column(Float, nullable=True)  # 0-100
    overall_bias_score = Column(Float, nullable=True)  # 0-100
    bias_level = Column(String(50), nullable=True)  # LOW, MEDIUM, HIGH, CRITICAL

    # Bot Analysis
    bot_probability = Column(Float, nullable=True)  # 0-100%
    authenticity_score = Column(Float, nullable=True)  # 0-100%

    # Misinformation Analysis
    misinformation_risk = Column(Float, nullable=True)  # 0-100
    unverified_claims_count = Column(Integer, nullable=True)
    emotional_manipulation_score = Column(Float, nullable=True)  # 0-100
    emotional_intensity = Column(String(50), nullable=True)  # LOW, MEDIUM, HIGH, CRITICAL

    # Trust & Risk Assessment
    trust_score = Column(Float, nullable=True)  # 0-100 (Model analysis only)
    validation_score = Column(Float, nullable=True)  # 0-100 (Cross-source verification)
    combined_trust_score = Column(Float, nullable=True)  # 0-100 (70% model + 30% validation)
    risk_level = Column(String(50), nullable=True)  # LOW, MEDIUM, HIGH, CRITICAL

    # Synthesis & Review
    full_report_summary = Column(Text, nullable=True)  # Natural language summary
    reviewer_approved = Column(Integer, default=0)  # 0 or 1
    approval_iteration = Column(Integer, nullable=True)  # Which iteration approved
    quality_score = Column(Float, nullable=True)  # 0.0-1.0 from reviewer

    # Raw Analysis Data (for audit trail)
    raw_agent_findings = Column(JSON, nullable=True)  # All agent outputs
    reflection_loop_details = Column(JSON, nullable=True)  # Iteration history

    # Timestamps
    analysis_timestamp = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Vector embedding (for future similarity search)
    content_embedding = Column(Vector(1536), nullable=True)

    # Relationship
    user = relationship("User", back_populates="analyses")

    __table_args__ = (
        Index('idx_news_analyses_url', 'article_url'),
        Index('idx_news_analyses_trust_score', 'trust_score'),
        Index('idx_news_analyses_risk_level', 'risk_level'),
        Index('idx_news_analyses_analysis_timestamp', 'analysis_timestamp'),
        Index('idx_news_analyses_user_id', 'user_id'),
    )


class Document(Base):
    """News documents ingested for RAG system."""

    __tablename__ = "documents"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)

    # Document metadata
    title = Column(String(500), nullable=False, index=True)
    content = Column(Text, nullable=False)
    source_url = Column(String(1000), nullable=False, index=True)
    source_domain = Column(String(255), nullable=False, index=True)

    # Article metadata
    author = Column(String(255), nullable=True)
    publish_date = Column(String(50), nullable=True)
    category = Column(String(100), nullable=True, index=True)  # politics, sports, war, etc.
    tags = Column(JSON, nullable=True)  # List of tags

    # Deduplication
    document_hash = Column(String(64), nullable=False, unique=True, index=True)

    # Vector embedding for semantic search
    content_embedding = Column(Vector(1536), nullable=True)

    # Timestamps
    ingestion_timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="documents")

    __table_args__ = (
        Index('idx_documents_source_domain', 'source_domain'),
        Index('idx_documents_category', 'category'),
        Index('idx_documents_ingestion_timestamp', 'ingestion_timestamp'),
        Index('idx_documents_user_id', 'user_id'),
    )

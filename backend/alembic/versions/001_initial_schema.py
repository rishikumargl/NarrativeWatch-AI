"""Initial schema creation for NarrativeWatch AI.

Revision ID: 001
Create Date: 2026-06-12
"""

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# Revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial database schema."""

    # Create pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')

    # InstagramPost table
    op.create_table(
        'instagram_posts',
        sa.Column('post_id', sa.String(), nullable=False),
        sa.Column('page_username', sa.String(), nullable=True, index=True),
        sa.Column('caption', sa.Text(), nullable=True),
        sa.Column('hashtags', sa.JSON(), nullable=True),
        sa.Column('engagement_metrics', sa.JSON(), nullable=True),
        sa.Column('posting_time', sa.DateTime(), nullable=True),
        sa.Column('embedding', Vector(1536), nullable=True),
        sa.Column('campaign_cluster', sa.String(), nullable=True, index=True),
        sa.Column('trust_score', sa.Float(), nullable=True, index=True),
        sa.Column('analysis_results', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('post_id')
    )
    op.create_index('idx_instagram_posts_posting_time', 'instagram_posts', ['posting_time'])

    # InstagramPage table
    op.create_table(
        'instagram_pages',
        sa.Column('page_id', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=True, unique=True, index=True),
        sa.Column('display_name', sa.String(), nullable=True),
        sa.Column('followers', sa.Integer(), nullable=True),
        sa.Column('engagement_metrics', sa.JSON(), nullable=True),
        sa.Column('profile_data', sa.JSON(), nullable=True),
        sa.Column('embedding', Vector(1536), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('last_updated', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('page_id')
    )

    # Campaign table
    op.create_table(
        'campaigns',
        sa.Column('campaign_id', sa.String(), nullable=False),
        sa.Column('pages_involved', sa.JSON(), nullable=True),
        sa.Column('hashtags', sa.JSON(), nullable=True),
        sa.Column('narrative_theme', sa.Text(), nullable=True),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('evidence_count', sa.Integer(), nullable=True),
        sa.Column('cluster_embedding', Vector(1536), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('campaign_id')
    )

    # BiasPattern table
    op.create_table(
        'bias_patterns',
        sa.Column('pattern_id', sa.String(), nullable=False),
        sa.Column('bias_type', sa.String(), nullable=True, index=True),
        sa.Column('indicators', sa.JSON(), nullable=True),
        sa.Column('frequency', sa.Integer(), nullable=True),
        sa.Column('similar_posts', sa.JSON(), nullable=True),
        sa.Column('pattern_embedding', Vector(1536), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('pattern_id')
    )

    # AnalysisResult table
    op.create_table(
        'analysis_results',
        sa.Column('result_id', sa.String(), nullable=False),
        sa.Column('post_id', sa.String(), nullable=True, index=True),
        sa.Column('page_id', sa.String(), nullable=True),
        sa.Column('agent_results', sa.JSON(), nullable=True),
        sa.Column('trust_score', sa.Float(), nullable=True),
        sa.Column('recommendations', sa.JSON(), nullable=True),
        sa.Column('analysis_embedding', Vector(1536), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('result_id')
    )


def downgrade() -> None:
    """Drop all tables."""
    op.drop_table('analysis_results')
    op.drop_table('bias_patterns')
    op.drop_table('campaigns')
    op.drop_table('instagram_pages')
    op.drop_table('instagram_posts')
    op.execute('DROP EXTENSION IF EXISTS vector')

"""Initial tables: articles and chunks

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'articles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('pmid', sa.String(), nullable=False, unique=True),
        sa.Column('pmcid', sa.String(), nullable=True),
        sa.Column('doi', sa.String(), nullable=True),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('abstract', sa.Text(), nullable=True),
        sa.Column('authors', postgresql.JSON(), nullable=True),
        sa.Column('journal', sa.String(), nullable=True),
        sa.Column('pub_date', sa.Date(), nullable=True),
        sa.Column('article_types', postgresql.JSON(), nullable=True),
        sa.Column('keywords', postgresql.JSON(), nullable=True),
        sa.Column('full_text_available', sa.Boolean(), default=False),
        sa.Column('indexed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_articles_pmid', 'articles', ['pmid'])
    op.create_index('ix_articles_pmcid', 'articles', ['pmcid'])

    op.create_table(
        'chunks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('article_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('articles.id'), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('chunk_type', sa.String(50), nullable=False),
        sa.Column('chroma_id', sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('chunks')
    op.drop_table('articles')

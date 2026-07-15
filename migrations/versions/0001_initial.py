"""Create source, raw-item, and insight tables with pgvector support."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "sources",
        sa.Column("id", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("repo", sa.String(length=255), nullable=False),
        sa.Column("feed_url", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("enabled", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("feed_url"),
    )
    op.create_table(
        "raw_items",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("source_id", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("raw_content", sa.Text(), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("url"),
    )
    op.create_index("ix_raw_items_source_id", "raw_items", ["source_id"], unique=False)
    op.create_index("ix_raw_items_published_at", "raw_items", ["published_at"], unique=False)
    op.create_table(
        "insights",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("raw_item_ids", JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("why_it_matters", sa.Text(), nullable=False),
        sa.Column("what_to_check", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("affected_libraries", JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("source_citations", JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("model_used", sa.String(length=255), nullable=False),
        sa.Column("embedding", Vector(dim=1536), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "confidence >= 0 AND confidence <= 1", name="ck_insights_confidence_range"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_insights_severity", "insights", ["severity"], unique=False)
    op.create_index("ix_insights_created_at", "insights", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_insights_created_at", table_name="insights")
    op.drop_index("ix_insights_severity", table_name="insights")
    op.drop_table("insights")
    op.drop_index("ix_raw_items_published_at", table_name="raw_items")
    op.drop_index("ix_raw_items_source_id", table_name="raw_items")
    op.drop_table("raw_items")
    op.drop_table("sources")

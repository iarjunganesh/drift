"""Add durable source hashes, model-run audits, and review metadata."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002_capture_provenance"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("raw_items", sa.Column("content_sha256", sa.String(length=64), nullable=True))
    op.create_table(
        "model_runs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("operation", sa.String(length=100), nullable=False),
        sa.Column("model_used", sa.String(length=255), nullable=False),
        sa.Column("evidence_sha256", sa.String(length=64), nullable=False),
        sa.Column("output_sha256", sa.String(length=64), nullable=False),
        sa.Column("input_tokens", sa.Integer(), nullable=True),
        sa.Column("output_tokens", sa.Integer(), nullable=True),
        sa.Column("settled_usd", sa.Float(), nullable=False),
        sa.Column("provider_attempts", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column("insights", sa.Column("model_run_id", sa.Integer(), nullable=True))
    op.add_column("insights", sa.Column("human_review_notes", sa.Text(), nullable=True))
    op.add_column("insights", sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_insights_model_run_id", "insights", ["model_run_id"], unique=False)
    op.create_foreign_key(
        "fk_insights_model_run_id_model_runs",
        "insights",
        "model_runs",
        ["model_run_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_insights_model_run_id_model_runs", "insights", type_="foreignkey")
    op.drop_index("ix_insights_model_run_id", table_name="insights")
    op.drop_column("insights", "reviewed_at")
    op.drop_column("insights", "human_review_notes")
    op.drop_column("insights", "model_run_id")
    op.drop_table("model_runs")
    op.drop_column("raw_items", "content_sha256")

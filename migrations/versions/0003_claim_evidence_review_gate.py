"""Add claim-level evidence, verifier provenance, and review-first publication."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "0003_claim_evidence_review_gate"
down_revision: Union[str, None] = "0002_capture_provenance"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "insights",
        sa.Column("verification_model_run_id", sa.Integer(), nullable=True),
    )
    op.add_column(
        "insights",
        sa.Column("claims", JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
    )
    op.add_column(
        "insights",
        sa.Column("upstream_release_type", sa.String(length=20), nullable=False, server_default="unknown"),
    )
    op.add_column(
        "insights",
        sa.Column("operator_risks", JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
    )
    op.add_column(
        "insights",
        sa.Column(
            "applicability_conditions",
            JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
    )
    op.add_column(
        "insights",
        sa.Column("publication_status", sa.String(length=20), nullable=False, server_default="draft"),
    )
    op.add_column(
        "insights",
        sa.Column(
            "verification_status",
            sa.String(length=30),
            nullable=False,
            server_default="legacy_unverified",
        ),
    )
    op.add_column("insights", sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index(
        "ix_insights_verification_model_run_id",
        "insights",
        ["verification_model_run_id"],
        unique=False,
    )
    op.create_index(
        "ix_insights_publication_status",
        "insights",
        ["publication_status"],
        unique=False,
    )
    op.create_foreign_key(
        "fk_insights_verification_model_run_id_model_runs",
        "insights",
        "model_runs",
        ["verification_model_run_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_insights_verification_model_run_id_model_runs", "insights", type_="foreignkey"
    )
    op.drop_index("ix_insights_publication_status", table_name="insights")
    op.drop_index("ix_insights_verification_model_run_id", table_name="insights")
    op.drop_column("insights", "verified_at")
    op.drop_column("insights", "verification_status")
    op.drop_column("insights", "publication_status")
    op.drop_column("insights", "applicability_conditions")
    op.drop_column("insights", "operator_risks")
    op.drop_column("insights", "upstream_release_type")
    op.drop_column("insights", "claims")
    op.drop_column("insights", "verification_model_run_id")

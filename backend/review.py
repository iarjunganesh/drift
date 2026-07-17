"""Explicit human publication gate for verifier-passed DRIFT drafts."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.schema import InsightRow, PublicationStatus, VerificationStatus


async def publish_verified_insights(
    session: AsyncSession,
    insight_ids: list[int],
    *,
    review_notes: str,
) -> list[int]:
    """Publish selected drafts only after a human records meaningful review notes."""
    normalized_ids = sorted(set(insight_ids))
    normalized_notes = review_notes.strip()
    if not normalized_ids:
        raise ValueError("Select at least one draft Insight to review.")
    if not normalized_notes:
        raise ValueError("Human review notes are required before publication.")

    rows = (
        await session.scalars(
            select(InsightRow).where(InsightRow.id.in_(normalized_ids)).with_for_update()
        )
    ).all()
    rows_by_id = {row.id: row for row in rows}
    missing_ids = [identifier for identifier in normalized_ids if identifier not in rows_by_id]
    if missing_ids:
        raise ValueError(f"Insight IDs were not found: {missing_ids}.")

    for row in rows:
        if row.publication_status != PublicationStatus.DRAFT.value:
            raise ValueError(f"Insight {row.id} is not an unpublished draft.")
        if row.verification_status != VerificationStatus.PASSED.value:
            raise ValueError(f"Insight {row.id} has not passed claim verification.")

    reviewed_at = datetime.now(UTC)
    for row in rows:
        row.publication_status = PublicationStatus.REVIEWED.value
        row.human_review_notes = normalized_notes
        row.reviewed_at = reviewed_at
    await session.commit()
    return normalized_ids


async def retract_reviewed_insights(
    session: AsyncSession,
    insight_ids: list[int],
    *,
    reason: str,
) -> list[int]:
    """Return reviewed Insights to draft status with an auditable reason."""
    normalized_ids = sorted(set(insight_ids))
    normalized_reason = reason.strip()
    if not normalized_ids:
        raise ValueError("Select at least one reviewed Insight to retract.")
    if not normalized_reason:
        raise ValueError("A retraction reason is required.")

    rows = (
        await session.scalars(
            select(InsightRow).where(InsightRow.id.in_(normalized_ids)).with_for_update()
        )
    ).all()
    rows_by_id = {row.id: row for row in rows}
    missing_ids = [identifier for identifier in normalized_ids if identifier not in rows_by_id]
    if missing_ids:
        raise ValueError(f"Insight IDs were not found: {missing_ids}.")

    for row in rows:
        if row.publication_status != PublicationStatus.REVIEWED.value:
            raise ValueError(f"Insight {row.id} is not a reviewed Insight.")

    for row in rows:
        prior_notes = (row.human_review_notes or "").strip()
        audit_note = f"Retraction: {normalized_reason}"
        row.human_review_notes = f"{prior_notes}\n{audit_note}".strip()
        row.publication_status = PublicationStatus.DRAFT.value
    await session.commit()
    return normalized_ids

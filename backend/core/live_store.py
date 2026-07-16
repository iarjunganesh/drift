"""Async PostgreSQL/pgvector retrieval for the live Insight store."""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.model_router import create_async_embedding_response
from backend.models.schema import (
    Insight,
    InsightRow,
    PublicationStatus,
    VerificationStatus,
)


def _row_to_insight(row: InsightRow) -> Insight:
    """Convert a durable row into the public, citation-bearing contract."""
    return Insight.model_validate(
        {
            "id": row.id,
            "raw_item_ids": row.raw_item_ids,
            "title": row.title,
            "summary": row.summary,
            "why_it_matters": row.why_it_matters,
            "what_to_check": row.what_to_check,
            "severity": row.severity,
            "affected_libraries": row.affected_libraries,
            "source_citations": row.source_citations,
            "confidence": row.confidence,
            "model_used": row.model_used,
            "claims": row.claims,
            "upstream_release_type": row.upstream_release_type,
            "operator_risks": row.operator_risks,
            "applicability_conditions": row.applicability_conditions,
            "publication_status": row.publication_status,
            "verification_status": row.verification_status,
            # human_review_notes is intentionally not carried into the public
            # contract; it is database-only audit data (see Insight.human_review_notes).
            "reviewed_at": row.reviewed_at,
            "verified_at": row.verified_at,
            "created_at": row.created_at,
        }
    )


def _publicly_eligible(statement):
    """Restrict live reads to human-reviewed, verifier-passed captures."""
    return statement.where(
        InsightRow.publication_status == PublicationStatus.REVIEWED.value,
        InsightRow.verification_status == VerificationStatus.PASSED.value,
    )


async def search_live_insights(
    session: AsyncSession,
    query_embedding: list[float],
    *,
    limit: int = 5,
) -> list[Insight]:
    """Retrieve the nearest cited Insights using pgvector cosine distance."""
    if not query_embedding:
        raise ValueError("A non-empty query embedding is required.")
    if limit < 1:
        raise ValueError("Retrieval limit must be at least 1.")

    statement = _publicly_eligible(
        select(InsightRow)
        .where(InsightRow.embedding.is_not(None))
        .order_by(InsightRow.embedding.cosine_distance(query_embedding))
        .limit(limit)
    )
    rows = (await session.scalars(statement)).all()
    return [_row_to_insight(row) for row in rows]


async def retrieve_live_insights(
    session: AsyncSession,
    query: str,
    *,
    client: Any,
    limit: int = 5,
) -> list[Insight]:
    """Embed a query through the router, then search the durable Insight store."""
    response = await create_async_embedding_response(client, [query])
    data = sorted(response.data, key=lambda embedding: getattr(embedding, "index", 0))
    if not data:
        raise RuntimeError("Embedding provider returned no query vector.")
    query_embedding = [float(value) for value in data[0].embedding]
    return await search_live_insights(session, query_embedding, limit=limit)


async def latest_live_insights(
    session: AsyncSession,
    *,
    limit: int = 5,
) -> list[Insight]:
    """Return the most recent cited Insights for a live-store briefing."""
    if limit < 1:
        raise ValueError("Briefing limit must be at least 1.")
    statement = _publicly_eligible(
        select(InsightRow).order_by(InsightRow.created_at.desc()).limit(limit)
    )
    rows = (await session.scalars(statement)).all()
    return [_row_to_insight(row) for row in rows]

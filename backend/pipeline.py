"""One-shot, bounded capture pipeline for draft DRIFT Insights.

This is deliberately a CLI/job boundary, not a scheduler. It makes one
inspectable Scout → Synthesizer → Insight → persisted-live-store run possible
without representing the fixture path as fresh release analysis.
"""

import argparse
import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from backend.agents.insight import GeneratedInsight, generate_insight_with_audit
from backend.agents.scout import load_persisted_raw_items, load_sources, run_scout, store_raw_items
from backend.agents.synthesizer import embed_texts, run_synthesizer
from backend.core.budget import SpendGuard
from backend.core.config import settings
from backend.core.model_router import Tier, create_client, create_sync_resilience
from backend.models.schema import (
    InsightRow,
    ModelRunRow,
    PublicationStatus,
    RawItem,
    VerificationStatus,
    session_factory,
)

log = structlog.get_logger(__name__)


@dataclass(frozen=True)
class CaptureResult:
    """Counts and durable draft Insight IDs produced by one capture run."""

    fetched_count: int
    selected_count: int
    persisted_raw_count: int
    insight_ids: list[int]


def select_recent_items(
    items: list[RawItem],
    *,
    per_source_limit: int,
    max_items: int,
) -> list[RawItem]:
    """Choose a bounded, recent cross-source capture set deterministically."""
    if per_source_limit < 1 or max_items < 1:
        raise ValueError("Capture limits must be at least 1.")
    grouped: dict[str, list[RawItem]] = {}
    for item in items:
        grouped.setdefault(item.source_id, []).append(item)
    selected: list[RawItem] = []
    for source_id in sorted(grouped):
        recent = sorted(grouped[source_id], key=lambda item: item.published_at, reverse=True)
        selected.extend(recent[:per_source_limit])
    return sorted(selected, key=lambda item: item.published_at, reverse=True)[:max_items]


async def _persist_generated_insights(
    session: AsyncSession,
    generated: list[GeneratedInsight],
    embeddings: list[list[float]],
) -> list[int]:
    """Write verifier-passed draft output plus both source-linked model audits."""
    if len(generated) != len(embeddings):
        raise ValueError("Every generated Insight must have one embedding.")
    verified_at = datetime.now(UTC)
    rows: list[InsightRow] = []
    for generated_insight, embedding in zip(generated, embeddings, strict=True):
        insight = generated_insight.insight
        audit = generated_insight.audit
        model_run = ModelRunRow(
            operation="insight.generate",
            model_used=audit.model_used,
            evidence_sha256=audit.evidence_sha256,
            output_sha256=audit.output_sha256,
            input_tokens=audit.input_tokens,
            output_tokens=audit.output_tokens,
            settled_usd=audit.settled_usd,
            provider_attempts=audit.attempts,
        )
        session.add(model_run)
        await session.flush()
        verification_audit = generated_insight.verification_audit
        verification_model_run = ModelRunRow(
            operation="insight.verify",
            model_used=verification_audit.model_used,
            evidence_sha256=verification_audit.evidence_sha256,
            output_sha256=verification_audit.output_sha256,
            input_tokens=verification_audit.input_tokens,
            output_tokens=verification_audit.output_tokens,
            settled_usd=verification_audit.settled_usd,
            provider_attempts=verification_audit.attempts,
        )
        session.add(verification_model_run)
        await session.flush()
        row = InsightRow(
            raw_item_ids=insight.raw_item_ids,
            title=insight.title,
            summary=insight.summary,
            why_it_matters=insight.why_it_matters,
            what_to_check=insight.what_to_check,
            severity=insight.severity.value,
            affected_libraries=insight.affected_libraries,
            source_citations=insight.source_citations,
            confidence=insight.confidence,
            model_used=insight.model_used,
            model_run_id=model_run.id,
            verification_model_run_id=verification_model_run.id,
            claims=[claim.model_dump(mode="json") for claim in insight.claims],
            upstream_release_type=insight.upstream_release_type.value,
            operator_risks=[risk.value for risk in insight.operator_risks],
            applicability_conditions=insight.applicability_conditions,
            publication_status=PublicationStatus.DRAFT.value,
            verification_status=VerificationStatus.PASSED.value,
            verified_at=verified_at,
            human_review_notes=None,
            reviewed_at=None,
            embedding=embedding,
        )
        session.add(row)
        rows.append(row)
    await session.flush()
    insight_ids = [row.id for row in rows]
    await session.commit()
    return insight_ids


async def run_capture(
    *,
    source_ids: set[str] | None = None,
    per_source_limit: int = 1,
    max_items: int = 3,
    tier: Tier = Tier.DEV,
    client: Any | None = None,
) -> CaptureResult:
    """Fetch, persist, generate, embed, and save a small review-required capture."""
    settings.validate()
    if settings.mode != "live":
        raise RuntimeError("DRIFT_MODE=live is required for a model-backed capture.")

    configured_sources = load_sources()
    selected_sources = [
        source for source in configured_sources if source_ids is None or source["id"] in source_ids
    ]
    if not selected_sources:
        raise ValueError("No configured sources matched the requested capture source IDs.")

    fetched = run_scout(selected_sources)
    selected = select_recent_items(
        fetched,
        per_source_limit=per_source_limit,
        max_items=max_items,
    )
    if not selected:
        raise RuntimeError("The configured sources returned no capture candidates.")

    async with session_factory() as session:
        persisted_raw_count = await store_raw_items(session, selected, sources=selected_sources)
        persisted_items = await load_persisted_raw_items(session, [item.url for item in selected])

    owned_client = client is None
    active_client = client or create_client(settings.openai_api_key, settings.model_timeout_seconds)
    spend_guard = SpendGuard(
        settings.spend_ledger_path,
        settings.max_spend_usd,
        settings.spend_alert_usd,
    )
    resilience = create_sync_resilience()
    try:
        clusters = run_synthesizer(
            persisted_items,
            client=active_client,
            spend_guard=spend_guard,
            resilience=resilience,
        )
        generated: list[GeneratedInsight] = []
        skipped_clusters = 0
        for cluster, severity in clusters:
            try:
                generated.append(
                    generate_insight_with_audit(
                        cluster,
                        severity,
                        tier,
                        client=active_client,
                        spend_guard=spend_guard,
                        resilience=resilience,
                    )
                )
            except ValueError as exc:
                # One cluster whose draft fails grounding or is rejected by the
                # separate verifier must not discard the whole capture. Log it
                # and keep the drafts that passed; a budget error (not a
                # ValueError) still stops the run.
                skipped_clusters += 1
                log.warning(
                    "insight.generate.skipped",
                    error=str(exc),
                    source_urls=[item.url for item in cluster],
                )
        if not generated:
            raise RuntimeError(
                "No insight drafts survived generation and verification; "
                f"{skipped_clusters} cluster(s) were skipped."
            )
        embeddings = embed_texts(
            [
                "\n".join(
                    [
                        generated_insight.insight.title,
                        generated_insight.insight.summary,
                        generated_insight.insight.why_it_matters,
                        generated_insight.insight.what_to_check,
                    ]
                )
                for generated_insight in generated
            ],
            client=active_client,
            spend_guard=spend_guard,
            resilience=resilience,
            operation_name="insight.embed",
        )
    finally:
        if owned_client:
            active_client.close()

    async with session_factory() as session:
        insight_ids = await _persist_generated_insights(
            session,
            generated,
            embeddings,
        )
    return CaptureResult(
        fetched_count=len(fetched),
        selected_count=len(selected),
        persisted_raw_count=persisted_raw_count,
        insight_ids=insight_ids,
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture cited DRIFT Insights from configured feeds.")
    parser.add_argument(
        "--source",
        action="append",
        dest="source_ids",
        help="Configured source ID to include. Repeat to select several sources.",
    )
    parser.add_argument("--per-source-limit", type=int, default=1)
    parser.add_argument("--max-items", type=int, default=3)
    parser.add_argument("--tier", choices=[tier.value for tier in Tier], default=Tier.DEV.value)
    return parser.parse_args()


def main() -> None:
    """Run the bounded capture CLI and print only durable record identifiers."""
    args = _parse_args()
    result = asyncio.run(
        run_capture(
            source_ids=set(args.source_ids) if args.source_ids else None,
            per_source_limit=args.per_source_limit,
            max_items=args.max_items,
            tier=Tier(args.tier),
        )
    )
    print(
        "Capture complete: "
        f"fetched={result.fetched_count} selected={result.selected_count} "
        f"new_raw_items={result.persisted_raw_count} draft_insight_ids={result.insight_ids}"
    )


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    main()

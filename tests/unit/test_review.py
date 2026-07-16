from datetime import UTC, datetime
from types import SimpleNamespace

import pytest

from backend import review
from backend.models.schema import (
    ChangeSeverity,
    InsightRow,
    PublicationStatus,
    UpstreamReleaseType,
    VerificationStatus,
)


def make_row(
    identifier: int,
    *,
    publication_status: PublicationStatus = PublicationStatus.DRAFT,
    verification_status: VerificationStatus = VerificationStatus.PASSED,
) -> InsightRow:
    return InsightRow(
        id=identifier,
        raw_item_ids=[identifier],
        title="Release",
        summary="Fact",
        why_it_matters="Interpretation",
        what_to_check="Check it.",
        severity=ChangeSeverity.MINOR.value,
        affected_libraries=["vllm"],
        source_citations=["https://example.com"],
        confidence=0.9,
        model_used="gpt-5.6-luna",
        claims=[],
        upstream_release_type=UpstreamReleaseType.UNKNOWN.value,
        operator_risks=[],
        applicability_conditions=[],
        publication_status=publication_status.value,
        verification_status=verification_status.value,
        created_at=datetime(2026, 7, 15, tzinfo=UTC),
    )


class FakeSession:
    def __init__(self, rows: list[InsightRow]) -> None:
        self.rows = rows
        self.statement = None
        self.committed = False

    async def scalars(self, statement):
        self.statement = statement
        return SimpleNamespace(all=lambda: self.rows)

    async def commit(self) -> None:
        self.committed = True


@pytest.mark.asyncio
async def test_publish_verified_insights_requires_and_records_human_review() -> None:
    row = make_row(4)
    session = FakeSession([row])

    published = await review.publish_verified_insights(
        session,
        [4, 4],
        review_notes="Checked claim excerpts and the operator interpretation.",
    )

    assert published == [4]
    assert row.publication_status == PublicationStatus.REVIEWED.value
    assert row.human_review_notes.startswith("Checked")
    assert row.reviewed_at is not None
    assert session.committed is True


@pytest.mark.asyncio
async def test_publish_verified_insights_rejects_invalid_selection_or_notes() -> None:
    session = FakeSession([])
    with pytest.raises(ValueError, match="at least one"):
        await review.publish_verified_insights(session, [], review_notes="Reviewed")
    with pytest.raises(ValueError, match="notes are required"):
        await review.publish_verified_insights(session, [1], review_notes="  ")
    with pytest.raises(ValueError, match="not found"):
        await review.publish_verified_insights(session, [1], review_notes="Reviewed")


@pytest.mark.asyncio
async def test_publish_verified_insights_rejects_non_draft_or_unverified_rows() -> None:
    with pytest.raises(ValueError, match="not an unpublished draft"):
        await review.publish_verified_insights(
            FakeSession([make_row(1, publication_status=PublicationStatus.REVIEWED)]),
            [1],
            review_notes="Reviewed",
        )
    with pytest.raises(ValueError, match="has not passed"):
        await review.publish_verified_insights(
            FakeSession([make_row(1, verification_status=VerificationStatus.LEGACY_UNVERIFIED)]),
            [1],
            review_notes="Reviewed",
        )

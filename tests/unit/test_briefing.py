from datetime import UTC, datetime

from backend.agents.briefing import answer_question, build_daily_briefing
from backend.models.schema import ChangeSeverity, Insight


def make_insight(identifier: int, severity: ChangeSeverity, confidence: float) -> Insight:
    return Insight(
        id=identifier,
        raw_item_ids=[identifier],
        title=f"Insight {identifier}",
        summary="summary",
        why_it_matters="reason",
        what_to_check="check",
        severity=severity,
        affected_libraries=["vllm"],
        source_citations=["https://example.com/release"],
        confidence=confidence,
        model_used="fixture-curated",
        created_at=datetime(2026, 7, 14, tzinfo=UTC),
    )


def test_briefing_ranks_security_then_breaking() -> None:
    result = build_daily_briefing([
        make_insight(1, ChangeSeverity.MINOR, 0.99),
        make_insight(2, ChangeSeverity.BREAKING, 0.2),
        make_insight(3, ChangeSeverity.SECURITY, 0.1),
    ])

    assert [item.insight.id for item in result] == [3, 2, 1]
    assert [item.rank for item in result] == [1, 2, 3]


def test_chat_explains_when_no_insight_matches() -> None:
    assert "could not find" in answer_question("unknown", [])

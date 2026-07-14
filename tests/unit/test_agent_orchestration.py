from dataclasses import replace
from datetime import UTC, datetime

from backend.agents import insight, scout, synthesizer
from backend.core.config import settings
from backend.models.schema import ChangeSeverity, Insight, RawItem


def make_raw_item(identifier: int) -> RawItem:
    return RawItem(
        id=identifier,
        source_id="vllm",
        title=f"Release {identifier}",
        url=f"https://example.com/{identifier}",
        published_at=datetime(2026, 7, 15, tzinfo=UTC),
        raw_content="Release notes",
    )


def make_insight(identifier: int) -> Insight:
    return Insight(
        id=identifier,
        raw_item_ids=[identifier],
        title=f"Insight {identifier}",
        summary="Summary",
        why_it_matters="Reason",
        what_to_check="Check it",
        severity=ChangeSeverity.MINOR,
        affected_libraries=["vllm"],
        source_citations=[f"https://example.com/{identifier}"],
        confidence=0.9,
        model_used="test-model",
        created_at=datetime(2026, 7, 15, tzinfo=UTC),
    )


def test_scout_loads_configured_sources_and_aggregates_items(monkeypatch, tmp_path) -> None:
    sources_file = tmp_path / "sources.yaml"
    sources_file.write_text("sources:\n  - id: first\n  - id: second\n", encoding="utf-8")
    monkeypatch.setattr(scout, "settings", replace(settings, sources_config_path=str(sources_file)))
    monkeypatch.setattr(scout, "fetch_source", lambda source: [make_raw_item(len(source["id"]))])

    assert [source["id"] for source in scout.load_sources()] == ["first", "second"]
    assert [item.id for item in scout.run_scout()] == [5, 6]


def test_synthesizer_orchestrates_embeddings_clusters_and_classification(monkeypatch) -> None:
    items = [make_raw_item(1), make_raw_item(2)]
    monkeypatch.setattr(synthesizer, "embed_items", lambda received: [[float(item.id)] for item in received])
    monkeypatch.setattr(synthesizer, "cluster_items", lambda received, _: [[received[0]], [received[1]]])
    monkeypatch.setattr(synthesizer, "classify_change", lambda _: ChangeSeverity.BREAKING)

    assert synthesizer.run_synthesizer(items) == [
        ([items[0]], ChangeSeverity.BREAKING),
        ([items[1]], ChangeSeverity.BREAKING),
    ]


def test_insight_batch_forwards_cluster_severity_and_tier(monkeypatch) -> None:
    cluster = [make_raw_item(1)]
    calls: list[tuple[list[RawItem], ChangeSeverity, object]] = []

    def fake_generate(
        received_cluster: list[RawItem], severity: ChangeSeverity, tier: object
    ) -> Insight:
        calls.append((received_cluster, severity, tier))
        return make_insight(len(calls))

    monkeypatch.setattr(insight, "generate_insight", fake_generate)

    result = insight.run_insight_batch([(cluster, ChangeSeverity.SECURITY)], tier="final")

    assert [item.id for item in result] == [1]
    assert calls == [(cluster, ChangeSeverity.SECURITY, "final")]

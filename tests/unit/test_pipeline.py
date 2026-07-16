from dataclasses import replace
from datetime import UTC, datetime
from types import SimpleNamespace

import pytest

from backend import pipeline
from backend.agents.insight import GeneratedInsight, InsightCallAudit, VerificationCallAudit
from backend.core.config import settings
from backend.core.model_router import Tier
from backend.models.schema import (
    ChangeSeverity,
    Insight,
    PublicationStatus,
    RawItem,
    VerificationStatus,
)


def make_item(identifier: int, source_id: str = "vllm") -> RawItem:
    return RawItem(
        id=identifier,
        source_id=source_id,
        title=f"Release {identifier}",
        url=f"https://example.com/{identifier}",
        published_at=datetime(2026, 7, identifier, tzinfo=UTC),
        raw_content="Primary release evidence.",
        fetched_at=datetime(2026, 7, identifier, tzinfo=UTC),
    )


def make_generated(identifier: int = 1) -> GeneratedInsight:
    insight = Insight(
        raw_item_ids=[identifier],
        title="vLLM runtime change",
        summary="A runtime default changed.",
        why_it_matters="Benchmark assumptions may shift.",
        what_to_check="Run the staging benchmark.",
        severity=ChangeSeverity.MINOR,
        affected_libraries=["vllm"],
        source_citations=[f"https://example.com/{identifier}"],
        confidence=0.9,
        model_used="gpt-5.6-sol",
    )
    return GeneratedInsight(
        insight=insight,
        audit=InsightCallAudit(
            model_used="gpt-5.6-sol",
            evidence_sha256="a" * 64,
            output_sha256="b" * 64,
            input_tokens=100,
            output_tokens=50,
            settled_usd=0.01,
            attempts=1,
        ),
        verification_audit=VerificationCallAudit(
            model_used="gpt-5.6-sol",
            evidence_sha256="c" * 64,
            output_sha256="d" * 64,
            input_tokens=75,
            output_tokens=25,
            settled_usd=0.005,
            attempts=1,
        ),
    )


def test_select_recent_items_limits_each_source_and_total() -> None:
    selected = pipeline.select_recent_items(
        [make_item(1), make_item(2), make_item(3, "pytorch")],
        per_source_limit=1,
        max_items=2,
    )

    assert [item.id for item in selected] == [3, 2]
    with pytest.raises(ValueError, match="at least 1"):
        pipeline.select_recent_items([], per_source_limit=0, max_items=1)


@pytest.mark.asyncio
async def test_persist_generated_insights_writes_audits_embedding_and_draft_metadata() -> None:
    class FakeSession:
        def __init__(self) -> None:
            self.added: list[object] = []
            self.committed = False

        def add(self, row: object) -> None:
            self.added.append(row)

        async def flush(self) -> None:
            for index, row in enumerate(self.added, start=1):
                if getattr(row, "id", None) is None:
                    row.id = index

        async def commit(self) -> None:
            self.committed = True

    session = FakeSession()
    result = await pipeline._persist_generated_insights(
        session,
        [make_generated()],
        [[0.1] * 1536],
    )

    model_run, verification_run, insight_row = session.added
    assert result == [3]
    assert model_run.evidence_sha256 == "a" * 64
    assert insight_row.model_run_id == 1
    assert verification_run.evidence_sha256 == "c" * 64
    assert insight_row.verification_model_run_id == 2
    assert insight_row.publication_status == PublicationStatus.DRAFT.value
    assert insight_row.verification_status == VerificationStatus.PASSED.value
    assert insight_row.human_review_notes is None
    assert insight_row.reviewed_at is None
    assert insight_row.verified_at is not None
    assert session.committed is True


@pytest.mark.asyncio
async def test_persist_generated_insights_rejects_embedding_mismatch() -> None:
    with pytest.raises(ValueError, match="one embedding"):
        await pipeline._persist_generated_insights(
            object(), [make_generated()], []
        )


@pytest.mark.asyncio
async def test_run_capture_connects_the_bounded_stages(monkeypatch, tmp_path) -> None:
    active_settings = replace(
        settings,
        mode="live",
        openai_api_key="test-key",
        spend_ledger_path=str(tmp_path / "ledger.json"),
    )
    monkeypatch.setattr(pipeline, "settings", active_settings)
    source = {"id": "vllm", "feed_url": "https://example.com/feed"}
    raw_item = make_item(1)
    generated = make_generated()
    calls: list[str] = []

    class FakeClient:
        def __init__(self) -> None:
            self.closed = False

        def close(self) -> None:
            self.closed = True

    client = FakeClient()

    class Context:
        async def __aenter__(self):
            return object()

        async def __aexit__(self, *_args) -> None:
            return None

    monkeypatch.setattr(pipeline, "load_sources", lambda: [source])
    monkeypatch.setattr(pipeline, "run_scout", lambda sources: calls.append("scout") or [raw_item])

    async def store(_session, items, *, sources):
        assert items == [raw_item]
        assert sources == [source]
        return 1

    async def load(_session, urls):
        assert urls == [raw_item.url]
        return [raw_item]

    async def persist(_session, generated_items, embeddings):
        assert generated_items == [generated]
        assert embeddings == [[0.1] * 1536]
        return [42]

    monkeypatch.setattr(pipeline, "store_raw_items", store)
    monkeypatch.setattr(pipeline, "load_persisted_raw_items", load)
    monkeypatch.setattr(pipeline, "session_factory", lambda: Context())
    monkeypatch.setattr(
        pipeline,
        "run_synthesizer",
        lambda items, **_kwargs: [([items[0]], ChangeSeverity.MINOR)],
    )
    monkeypatch.setattr(pipeline, "generate_insight_with_audit", lambda *_args, **_kwargs: generated)
    monkeypatch.setattr(pipeline, "embed_texts", lambda *_args, **_kwargs: [[0.1] * 1536])
    monkeypatch.setattr(pipeline, "_persist_generated_insights", persist)
    monkeypatch.setattr(pipeline, "create_client", lambda *_args: client)

    result = await pipeline.run_capture(
        source_ids={"vllm"},
        tier=Tier.FINAL,
    )

    assert calls == ["scout"]
    assert result == pipeline.CaptureResult(1, 1, 1, [42])
    assert client.closed is True


@pytest.mark.asyncio
async def test_run_capture_rejects_fixture_mode_and_empty_selection(monkeypatch) -> None:
    monkeypatch.setattr(pipeline, "settings", replace(settings, mode="fixture"))
    with pytest.raises(RuntimeError, match="DRIFT_MODE=live"):
        await pipeline.run_capture(client=object())

    monkeypatch.setattr(pipeline, "settings", replace(settings, mode="live", openai_api_key="test-key"))
    monkeypatch.setattr(pipeline, "load_sources", lambda: [])
    with pytest.raises(ValueError, match="No configured"):
        await pipeline.run_capture(client=object())


@pytest.mark.asyncio
async def test_run_capture_rejects_empty_source_response(monkeypatch) -> None:
    monkeypatch.setattr(pipeline, "settings", replace(settings, mode="live", openai_api_key="test-key"))
    monkeypatch.setattr(pipeline, "load_sources", lambda: [{"id": "vllm"}])
    monkeypatch.setattr(pipeline, "run_scout", lambda _sources: [])

    with pytest.raises(RuntimeError, match="no capture candidates"):
        await pipeline.run_capture(client=object())


def test_capture_cli_parser_reads_source_limits(monkeypatch) -> None:
    monkeypatch.setattr(
        "sys.argv",
        [
            "backend.pipeline",
            "--source",
            "vllm",
            "--per-source-limit",
            "2",
            "--max-items",
            "4",
            "--tier",
            "final",
        ],
    )

    args = pipeline._parse_args()

    assert args.source_ids == ["vllm"]
    assert (args.per_source_limit, args.max_items, args.tier) == (2, 4, "final")


def test_capture_cli_arguments_and_main_output(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        pipeline,
        "_parse_args",
        lambda: SimpleNamespace(
            source_ids=["vllm"],
            per_source_limit=1,
            max_items=3,
            tier="final",
        ),
    )

    async def capture(**kwargs):
        assert kwargs["tier"] is Tier.FINAL
        return pipeline.CaptureResult(3, 1, 1, [8])

    monkeypatch.setattr(pipeline, "run_capture", capture)
    pipeline.main()

    assert "draft_insight_ids=[8]" in capsys.readouterr().out

from datetime import UTC, datetime
from types import SimpleNamespace

import pytest
from sqlalchemy.dialects import postgresql

from backend.core import live_store
from backend.models.schema import ChangeSeverity, InsightRow


def make_row(identifier: int) -> InsightRow:
    return InsightRow(
        id=identifier,
        raw_item_ids=[identifier],
        title=f"Insight {identifier}",
        summary="A release changed behavior.",
        why_it_matters="Workload assumptions may change.",
        what_to_check="Run the representative benchmark.",
        severity=ChangeSeverity.MINOR.value,
        affected_libraries=["vllm"],
        source_citations=[f"https://example.com/{identifier}"],
        confidence=0.9,
        model_used="gpt-5.6-luna",
        embedding=[0.1] * 1536,
        created_at=datetime(2026, 7, 15, tzinfo=UTC),
    )


class FakeSession:
    def __init__(self, rows: list[InsightRow]) -> None:
        self.rows = rows
        self.statement = None

    async def scalars(self, statement):
        self.statement = statement
        return SimpleNamespace(all=lambda: self.rows)


class FakeEmbeddings:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    async def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(data=[SimpleNamespace(index=0, embedding=[0.25] * 1536)])


class FakeClient:
    def __init__(self) -> None:
        self.embeddings = FakeEmbeddings()


@pytest.mark.asyncio
async def test_search_live_insights_uses_pgvector_cosine_distance() -> None:
    session = FakeSession([make_row(1), make_row(2)])

    result = await live_store.search_live_insights(session, [0.25] * 1536, limit=2)

    assert [insight.id for insight in result] == [1, 2]
    compiled = str(session.statement.compile(dialect=postgresql.dialect()))
    assert "<=>" in compiled
    assert "LIMIT" in compiled


@pytest.mark.asyncio
async def test_retrieve_live_insights_embeds_query_through_router(monkeypatch) -> None:
    session = FakeSession([make_row(3)])
    client = FakeClient()

    result = await live_store.retrieve_live_insights(
        session,
        "vllm scheduler",
        client=client,
        limit=1,
    )

    assert [insight.id for insight in result] == [3]
    assert client.embeddings.calls == [
        {"model": "text-embedding-3-small", "input": ["vllm scheduler"]}
    ]


@pytest.mark.asyncio
async def test_live_store_rejects_invalid_search_inputs() -> None:
    session = FakeSession([])

    with pytest.raises(ValueError, match="non-empty query embedding"):
        await live_store.search_live_insights(session, [])
    with pytest.raises(ValueError, match="at least 1"):
        await live_store.search_live_insights(session, [0.1], limit=0)


@pytest.mark.asyncio
async def test_retrieve_live_insights_rejects_empty_embedding_response() -> None:
    class EmptyEmbeddings:
        async def create(self, **_kwargs):
            return SimpleNamespace(data=[])

    client = SimpleNamespace(embeddings=EmptyEmbeddings())

    with pytest.raises(RuntimeError, match="no query vector"):
        await live_store.retrieve_live_insights(FakeSession([]), "vllm", client=client)


@pytest.mark.asyncio
async def test_latest_live_insights_orders_by_creation_time_and_validates_limit() -> None:
    session = FakeSession([make_row(2), make_row(1)])

    result = await live_store.latest_live_insights(session, limit=2)

    assert [insight.id for insight in result] == [2, 1]
    compiled = str(session.statement.compile(dialect=postgresql.dialect()))
    assert "ORDER BY insights.created_at DESC" in compiled
    with pytest.raises(ValueError, match="Briefing limit"):
        await live_store.latest_live_insights(session, limit=0)

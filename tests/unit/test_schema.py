import pytest

from backend.models.schema import Base, ModelRunRow, get_session


def test_durable_metadata_contains_day_one_tables() -> None:
    assert set(Base.metadata.tables) == {"sources", "raw_items", "insights", "model_runs"}
    assert Base.metadata.tables["raw_items"].c.url.unique is True
    assert Base.metadata.tables["raw_items"].c.content_sha256.type.length == 64
    assert Base.metadata.tables["insights"].c.embedding.type.dim == 1536
    assert Base.metadata.tables["insights"].c.model_run_id.foreign_keys
    assert Base.metadata.tables["insights"].c.verification_model_run_id.foreign_keys
    assert Base.metadata.tables["insights"].c.claims.nullable is False
    assert Base.metadata.tables["insights"].c.publication_status.index is True


def test_model_run_row_captures_immutable_generation_metadata() -> None:
    row = ModelRunRow(
        operation="insight.generate",
        model_used="gpt-5.6-sol",
        evidence_sha256="a" * 64,
        output_sha256="b" * 64,
        input_tokens=10,
        output_tokens=5,
        settled_usd=0.01,
        provider_attempts=1,
    )

    assert row.model_used == "gpt-5.6-sol"


@pytest.mark.asyncio
async def test_get_session_yields_async_session() -> None:
    async for session in get_session():
        assert session is not None
        break

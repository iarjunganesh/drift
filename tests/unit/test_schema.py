import pytest

from backend.models.schema import Base, get_session


def test_durable_metadata_contains_day_one_tables() -> None:
    assert set(Base.metadata.tables) == {"sources", "raw_items", "insights"}
    assert Base.metadata.tables["raw_items"].c.url.unique is True
    assert Base.metadata.tables["insights"].c.embedding.type.dim == 1536


@pytest.mark.asyncio
async def test_get_session_yields_async_session() -> None:
    async for session in get_session():
        assert session is not None
        break

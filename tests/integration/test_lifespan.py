from dataclasses import replace

import pytest

from backend import main
from backend.core.config import settings


@pytest.mark.asyncio
async def test_live_lifespan_is_explicitly_rejected(monkeypatch) -> None:
    monkeypatch.setattr(
        main,
        "settings",
        replace(settings, mode="live", openai_api_key="test-key"),
    )

    with pytest.raises(RuntimeError, match="Live mode has not been enabled"):
        async with main.lifespan(main.app):
            pass

from dataclasses import replace

import pytest
from fastapi.testclient import TestClient

from backend import main
from backend.core.config import settings


@pytest.fixture
def api_client(monkeypatch):
    monkeypatch.setattr(main, "settings", replace(settings, mode="fixture"))
    with TestClient(main.app) as client:
        yield client

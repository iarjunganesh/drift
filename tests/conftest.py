import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def api_client():
    with TestClient(app) as client:
        yield client

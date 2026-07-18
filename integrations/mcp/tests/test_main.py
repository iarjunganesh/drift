"""Tests for the stdio entrypoint."""

from typing import Any

import pytest

import integrations.mcp.__main__ as entry


class FakeServer:
    def __init__(self) -> None:
        self.ran_with: str | None = None

    def run(self, transport: str) -> None:
        self.ran_with = transport


class FakeSettings:
    def __init__(self, error: str | None = None) -> None:
        self._error = error
        self.validated = False

    def validate(self) -> None:
        self.validated = True
        if self._error:
            raise RuntimeError(self._error)


def test_main_validates_and_runs_stdio(monkeypatch: pytest.MonkeyPatch) -> None:
    server = FakeServer()
    fake_settings = FakeSettings()
    monkeypatch.setattr(entry, "settings", fake_settings)
    monkeypatch.setattr(entry, "build_server", lambda *a, **k: server)

    entry.main()

    assert fake_settings.validated is True
    assert server.ran_with == "stdio"


def test_main_propagates_invalid_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(entry, "settings", FakeSettings(error="DRIFT_API_URL must be an http(s) URL"))

    def unexpected(*_a: Any, **_k: Any) -> None:  # pragma: no cover - must not run
        raise AssertionError("build_server should not run when validation fails")

    monkeypatch.setattr(entry, "build_server", unexpected)

    with pytest.raises(RuntimeError, match="DRIFT_API_URL"):
        entry.main()

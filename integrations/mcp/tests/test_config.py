"""Tests for MCP client configuration."""

import pytest

from integrations.mcp.config import DEFAULT_API_URL, McpSettings, settings


def test_module_settings_default_is_local() -> None:
    assert settings.base_url == DEFAULT_API_URL


def test_base_url_strips_trailing_slash() -> None:
    assert McpSettings(api_url="https://drift-api-prod.up.railway.app/").base_url == (
        "https://drift-api-prod.up.railway.app"
    )


def test_validate_accepts_http_and_https() -> None:
    McpSettings(api_url="http://localhost:8000").validate()
    McpSettings(api_url="https://example.com").validate()


def test_validate_rejects_non_http_url() -> None:
    with pytest.raises(RuntimeError, match="DRIFT_API_URL"):
        McpSettings(api_url="ftp://example.com").validate()


def test_validate_rejects_non_positive_timeout() -> None:
    with pytest.raises(RuntimeError, match="DRIFT_MCP_TIMEOUT_SECONDS"):
        McpSettings(api_url="http://localhost:8000", timeout_seconds=0).validate()

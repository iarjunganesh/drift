"""DRIFT MCP integration — a thin client over the public DRIFT HTTP API.

The server exposes exactly three tools — ``drift_briefing``, ``drift_search``,
and ``ask_drift`` — each a one-to-one call to the existing ``/briefing``,
``/search``, and ``/chat`` endpoints. It is configured with only
``DRIFT_API_URL`` (plus an optional ``DRIFT_MCP_TIMEOUT_SECONDS`` request
timeout) and holds no OpenAI key, database URL, or credentials of any
kind: every guarantee the API enforces (reviewed-only reads, redacted review
notes, spend guards, resilience) applies to MCP traffic automatically because
there is no second path to the store.

See ``docs/adr/011-mcp-thin-client-layer.md``.
"""

from integrations.mcp.client import DriftApiClient, DriftApiError
from integrations.mcp.config import McpSettings, settings
from integrations.mcp.server import build_server

__all__ = [
    "DriftApiClient",
    "DriftApiError",
    "McpSettings",
    "build_server",
    "settings",
]

"""The DRIFT MCP server: three thin tools over the public API.

DRIFT's reviewed release intelligence is also available to any MCP-compatible
assistant. The tools are a consumption channel — additive and subordinate to
the product — not a repositioning: DRIFT stays release intelligence for GPU and
AI infrastructure, cited, bounded, and inspectable. Each tool is a one-to-one
call to an existing public endpoint and can offer nothing the API does not.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from integrations.mcp import formatting
from integrations.mcp.client import DriftApiClient, DriftApiError
from integrations.mcp.config import McpSettings, settings


def build_server(
    *,
    client: DriftApiClient | None = None,
    mcp_settings: McpSettings | None = None,
) -> FastMCP:
    """Construct the FastMCP server with the three DRIFT tools registered."""
    cfg = mcp_settings or settings
    api = client or DriftApiClient(cfg.base_url, cfg.timeout_seconds)
    mcp = FastMCP("drift")

    @mcp.tool()
    async def drift_briefing(top_n: int = 5) -> str:
        """Return DRIFT's ranked release-intelligence briefing.

        Lists the most important reviewed, cited changes across GPU and
        AI-infrastructure libraries. Each entry carries a severity, a
        plain-language summary, why it matters, a bounded what-to-check action,
        a confidence flag, and primary source citations. ``top_n`` is 1–10.
        """
        try:
            items = await api.briefing(top_n)
        except DriftApiError as exc:
            return str(exc)
        return formatting.format_briefing(items)

    @mcp.tool()
    async def drift_search(query: str) -> str:
        """Search DRIFT's reviewed release insights.

        Query by library, release, or operational risk (e.g. 'vllm', 'nccl
        breaking change'). Returns cited insights only from DRIFT's
        human-reviewed, verifier-passed corpus; unmatched queries return no
        results rather than a guess.
        """
        try:
            items = await api.search(query)
        except DriftApiError as exc:
            return str(exc)
        return formatting.format_search(items, query.strip())

    @mcp.tool()
    async def ask_drift(question: str) -> str:
        """Ask a question grounded in DRIFT's reviewed release evidence.

        DRIFT retrieves matching reviewed insights first and answers only from
        them, with citations. If nothing in the reviewed corpus matches, it
        declines rather than guessing. Cost is bounded and server-accounted.
        """
        try:
            response = await api.ask(question)
        except DriftApiError as exc:
            return str(exc)
        if response is None:
            return (
                "DRIFT has no reviewed insight matching that question, so it "
                "declines to answer rather than guessing. Try a GPU or "
                "AI-infrastructure release topic in the reviewed corpus."
            )
        return formatting.format_chat(response)

    return mcp

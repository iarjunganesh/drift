"""Pure formatters that turn DRIFT API JSON into assistant-readable text.

These keep the tools thin: they add no knowledge, only present the reviewed,
cited fields the API already returns. Every formatter tolerates missing keys so
a forward-compatible API response never breaks the client.
"""

from __future__ import annotations

from typing import Any

_NO_BRIEFING = (
    "DRIFT has no reviewed insights to brief right now. In live mode the "
    "briefing lists only human-reviewed, verifier-passed captures."
)


def _citations_block(urls: list[str]) -> str:
    if not urls:
        return "Sources: (none listed)"
    lines = "\n".join(f"  - {url}" for url in urls)
    return f"Sources:\n{lines}"


def format_insight(insight: dict[str, Any]) -> str:
    """Render one insight: what changed, why it matters, what to check, sources."""
    title = insight.get("title", "(untitled insight)")
    severity = str(insight.get("severity", "unknown")).upper()
    confidence = insight.get("confidence")
    libraries = insight.get("affected_libraries") or []
    header = f"[{severity}] {title}"
    if isinstance(confidence, int | float):
        header += f" (confidence {confidence:.2f})"

    lines = [header]
    if libraries:
        lines.append(f"Affected: {', '.join(libraries)}")
    if insight.get("summary"):
        lines.append(str(insight["summary"]))
    if insight.get("why_it_matters"):
        lines.append(f"Why it matters: {insight['why_it_matters']}")
    if insight.get("what_to_check"):
        lines.append(f"What to check: {insight['what_to_check']}")
    lines.append(_citations_block(insight.get("source_citations") or []))
    return "\n".join(lines)


def format_briefing(items: list[dict[str, Any]]) -> str:
    """Render the ranked briefing (a list of ``BriefingItem``)."""
    if not items:
        return _NO_BRIEFING
    blocks = []
    for item in items:
        rank = item.get("rank", "?")
        insight = item.get("insight") or {}
        blocks.append(f"{rank}. {format_insight(insight)}")
    header = f"DRIFT briefing — {len(blocks)} reviewed insight(s):"
    return header + "\n\n" + "\n\n".join(blocks)


def format_search(items: list[dict[str, Any]], query: str) -> str:
    """Render search results (a list of ``Insight``)."""
    if not items:
        return (
            f"No reviewed DRIFT insights match '{query}'. DRIFT searches only the "
            "human-reviewed, verifier-passed corpus."
        )
    blocks = [format_insight(insight) for insight in items]
    header = f"{len(blocks)} reviewed DRIFT insight(s) matching '{query}':"
    return header + "\n\n" + "\n\n".join(blocks)


def format_chat(response: dict[str, Any]) -> str:
    """Render a grounded ``ChatResponse`` with its citations and audit label."""
    answer = response.get("answer", "").strip() or "(no answer text returned)"
    citations = response.get("source_citations") or []
    model_used = response.get("model_used", "unknown")
    grounded_ids = response.get("grounded_insight_ids") or []

    lines = [answer, ""]
    lines.append(_citations_block(citations))
    if grounded_ids:
        ids = ", ".join(str(i) for i in grounded_ids)
        lines.append(f"Grounded in DRIFT insight IDs: {ids}")
    lines.append(f"Answered by: {model_used}")
    return "\n".join(lines)

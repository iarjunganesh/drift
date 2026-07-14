"""
Briefing agent — Day 5.

Produces the daily "Top N Things That Matter" from the accumulated
Insight table, ranked by severity + recency. Also backs the semantic
search and chat-over-knowledge endpoints.

Briefing generation: Tier.DEV (Luna) is fine — it's aggregation, not
fresh reasoning.
Chat endpoint: Tier.LIVE (Terra) — this is what a judge might interact
with directly, so it needs to hold up in a live back-and-forth.
"""

from backend.models.schema import BriefingItem, Insight

_SEVERITY_ORDER = {
    "security": 0,
    "breaking": 1,
    "minor": 2,
    "cosmetic": 3,
}


def build_daily_briefing(insights: list[Insight], top_n: int = 5) -> list[BriefingItem]:
    """
    TODO(codex): rank insights by severity (BREAKING/SECURITY first)
    then recency, take top_n, return as ranked BriefingItems.
    No LLM call needed for ranking itself — pure logic.
    """
    ordered = sorted(
        insights,
        key=lambda insight: (
            _SEVERITY_ORDER[insight.severity.value],
            -insight.confidence,
            -insight.created_at.timestamp(),
        ),
    )
    return [BriefingItem(insight=insight, rank=index)
            for index, insight in enumerate(ordered[:top_n], start=1)]


def answer_question(question: str, relevant_insights: list[Insight]) -> str:
    """
    TODO(codex): semantic-search insights (pgvector) for relevant_insights
    upstream of this call, then use get_model(Tier.LIVE) to answer the
    question grounded only in those insights' content. Cite sources in
    the answer text.
    """
    if not relevant_insights:
        return (
            "I could not find a matching DRIFT insight. Try naming a library or "
            "describing the release risk you want to assess."
        )
    items = " ".join(
        f"{item.title}: {item.why_it_matters} What to check: {item.what_to_check}"
        for item in relevant_insights[:3]
    )
    return f"Based on the available DRIFT insights: {items}"

"""Tests for the pure DRIFT response formatters."""

from integrations.mcp import formatting

FULL_INSIGHT = {
    "id": 13,
    "title": "vLLM v0.25.1",
    "severity": "breaking",
    "confidence": 0.82,
    "affected_libraries": ["vllm"],
    "summary": "Scheduler defaults changed.",
    "why_it_matters": "Throughput regressions are possible.",
    "what_to_check": "Re-benchmark serving throughput.",
    "source_citations": ["https://github.com/vllm-project/vllm/releases/tag/v0.25.1"],
}


def test_format_insight_includes_all_fields() -> None:
    text = formatting.format_insight(FULL_INSIGHT)
    assert "[BREAKING] vLLM v0.25.1 (confidence 0.82)" in text
    assert "Affected: vllm" in text
    assert "Why it matters: Throughput regressions are possible." in text
    assert "What to check: Re-benchmark serving throughput." in text
    assert "https://github.com/vllm-project/vllm/releases/tag/v0.25.1" in text


def test_format_insight_tolerates_missing_fields() -> None:
    text = formatting.format_insight({})
    assert "[UNKNOWN] (untitled insight)" in text
    assert "Sources: (none listed)" in text
    assert "confidence" not in text


def test_format_briefing_empty() -> None:
    assert "no reviewed insights" in formatting.format_briefing([]).lower()


def test_format_briefing_lists_ranked_items() -> None:
    text = formatting.format_briefing([{"rank": 1, "insight": FULL_INSIGHT}])
    assert "DRIFT briefing — 1 reviewed insight(s):" in text
    assert "1. [BREAKING] vLLM v0.25.1" in text


def test_format_briefing_tolerates_missing_insight() -> None:
    text = formatting.format_briefing([{"rank": 2}])
    assert "2. [UNKNOWN] (untitled insight)" in text


def test_format_search_empty_declines() -> None:
    text = formatting.format_search([], "obscure")
    assert "No reviewed DRIFT insights match 'obscure'" in text


def test_format_search_lists_matches() -> None:
    text = formatting.format_search([FULL_INSIGHT], "vllm")
    assert "1 reviewed DRIFT insight(s) matching 'vllm':" in text
    assert "vLLM v0.25.1" in text


def test_format_chat_full() -> None:
    text = formatting.format_chat(
        {
            "answer": "vLLM changed scheduler defaults.",
            "source_citations": ["https://example.com/vllm"],
            "model_used": "gpt-5.6-terra",
            "grounded_insight_ids": [13],
        }
    )
    assert text.startswith("vLLM changed scheduler defaults.")
    assert "https://example.com/vllm" in text
    assert "Grounded in DRIFT insight IDs: 13" in text
    assert "Answered by: gpt-5.6-terra" in text


def test_format_chat_minimal() -> None:
    text = formatting.format_chat({})
    assert "(no answer text returned)" in text
    assert "Sources: (none listed)" in text
    assert "Grounded in DRIFT insight IDs" not in text
    assert "Answered by: unknown" in text

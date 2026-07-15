import json
from datetime import UTC, datetime
from types import SimpleNamespace

import pytest

from backend.agents import insight
from backend.core.model_router import Tier
from backend.models.schema import ChangeSeverity, RawItem


def make_item(identifier: int, content: str = "release notes") -> RawItem:
    return RawItem(
        id=identifier,
        source_id="vllm",
        title=f"Release {identifier}",
        url=f"https://example.com/releases/{identifier}",
        published_at=datetime(2026, 7, 15, tzinfo=UTC),
        raw_content=content,
    )


class FakeClient:
    def __init__(self, output_text: str | None = None) -> None:
        self.response_calls: list[dict] = []
        self.output_text = output_text or json.dumps(
            {
                "title": "vLLM changes scheduler defaults",
                "summary": "The release changes scheduler defaults.",
                "why_it_matters": "Existing throughput and latency assumptions may shift.",
                "what_to_check": "Compare scheduler settings and benchmark a representative workload.",
                "affected_libraries": ["vllm"],
                "confidence": 0.88,
            }
        )

        class Responses:
            def __init__(inner_self, outer: FakeClient) -> None:
                inner_self.outer = outer

            def create(inner_self, **kwargs):
                inner_self.outer.response_calls.append(kwargs)
                return SimpleNamespace(output_text=inner_self.outer.output_text)

        self.responses = Responses(self)
        self.closed = False

    def close(self) -> None:
        self.closed = True


def test_generate_insight_parses_structured_output_and_derives_provenance() -> None:
    client = FakeClient()
    items = [make_item(1, "The scheduler now defaults to chunked prefill."), make_item(2)]

    result = insight.generate_insight(
        items,
        ChangeSeverity.BREAKING,
        tier=Tier.FINAL,
        client=client,
    )

    assert result.raw_item_ids == [1, 2]
    assert result.title == "vLLM changes scheduler defaults"
    assert result.severity is ChangeSeverity.BREAKING
    assert result.source_citations == [item.url for item in items]
    assert result.model_used == "gpt-5.6-sol"
    assert result.confidence == 0.88
    request = client.response_calls[0]
    assert request["model"] == "gpt-5.6-sol"
    assert request["text"]["format"]["name"] == "drift_insight"
    assert "untrusted release evidence" in request["input"]
    assert "The scheduler now defaults to chunked prefill." in request["input"]
    assert client.closed is False


def test_generate_insight_closes_owned_client(monkeypatch) -> None:
    client = FakeClient()
    monkeypatch.setattr(insight, "create_client", lambda *_args: client)

    result = insight.generate_insight([make_item(1)], ChangeSeverity.MINOR)

    assert result.raw_item_ids == [1]
    assert client.closed is True


def test_generate_insight_rejects_empty_cluster() -> None:
    with pytest.raises(ValueError, match="empty cluster"):
        insight.generate_insight([], ChangeSeverity.MINOR)


def test_generate_insight_requires_persisted_raw_item_ids() -> None:
    item = make_item(1)
    item.id = None

    with pytest.raises(ValueError, match="must have an id"):
        insight.generate_insight([item], ChangeSeverity.MINOR)


def test_generate_insight_rejects_empty_provider_output() -> None:
    client = FakeClient()
    client.responses.create = lambda **_kwargs: SimpleNamespace()

    with pytest.raises(ValueError, match="empty Insight JSON"):
        insight.generate_insight([make_item(1)], ChangeSeverity.MINOR, client=client)


def test_generate_insight_rejects_invalid_json() -> None:
    client = FakeClient("not-json")

    with pytest.raises(ValueError, match="invalid Insight JSON"):
        insight.generate_insight([make_item(1)], ChangeSeverity.MINOR, client=client)


def test_generate_insight_rejects_schema_invalid_json() -> None:
    client = FakeClient(json.dumps({"title": "Missing required fields"}))

    with pytest.raises(ValueError, match="failed schema validation"):
        insight.generate_insight([make_item(1)], ChangeSeverity.MINOR, client=client)

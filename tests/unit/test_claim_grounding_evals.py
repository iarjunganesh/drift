import json
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

import pytest

from backend.agents.insight import generate_insight
from backend.models.schema import ChangeSeverity, RawItem

_EVAL_PATH = Path("backend/fixtures/evals/claim_grounding.json")


def _draft(excerpt: str) -> str:
    return json.dumps(
        {
            "claims": [
                {
                    "text": "The runtime adds a startup warning.",
                    "kind": "direct_fact",
                    "evidence": [{"raw_item_id": 1, "excerpt": excerpt}],
                },
                {
                    "text": "This may affect startup observability.",
                    "kind": "inference",
                    "evidence": [{"raw_item_id": 1, "excerpt": excerpt}],
                },
                {
                    "text": "Confirm startup logs in a staging deployment.",
                    "kind": "recommended_check",
                    "evidence": [{"raw_item_id": 1, "excerpt": excerpt}],
                },
            ],
            "affected_libraries": ["runtime"],
            "confidence": 0.8,
            "upstream_release_type": "unknown",
            "operator_risks": ["startup"],
            "applicability_conditions": ["If you monitor process startup."],
        }
    )


class FakeClient:
    def __init__(self, outputs: list[str]) -> None:
        self.outputs = outputs
        self.calls: list[dict] = []
        self.responses = SimpleNamespace(create=self.create)

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(output_text=self.outputs.pop(0))


def _item(content: str) -> RawItem:
    return RawItem(
        id=1,
        source_id="eval",
        title="Evaluation release",
        url="https://example.com/release",
        published_at=datetime(2026, 7, 15, tzinfo=UTC),
        raw_content=content,
    )


@pytest.mark.parametrize("case", json.loads(_EVAL_PATH.read_text(encoding="utf-8")), ids=lambda case: case["id"])
def test_claim_grounding_calibration_cases(case: dict) -> None:
    verdict = (
        json.dumps({"accepted_claim_indexes": [0, 1, 2], "notes": []})
        if case["verdict"] == "accept"
        else json.dumps({"accepted_claim_indexes": [0, 1], "notes": ["Not sufficiently supported."]})
    )
    client = FakeClient([_draft(case["excerpt"]), verdict])

    if case["expected_error"]:
        with pytest.raises(ValueError, match=case["expected_error"]):
            generate_insight([_item(case["raw_content"])], ChangeSeverity.MINOR, client=client)
    else:
        result = generate_insight([_item(case["raw_content"])], ChangeSeverity.MINOR, client=client)
        assert result.claims[0].evidence[0].excerpt == case["excerpt"]
        assert "untrusted release evidence" in client.calls[0]["input"]

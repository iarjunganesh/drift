import json
from datetime import UTC, datetime
from types import SimpleNamespace

import pytest

from backend.agents import insight
from backend.core.model_router import Tier
from backend.models.schema import (
    ChangeSeverity,
    ClaimKind,
    PublicationStatus,
    RawItem,
    VerificationStatus,
)


def make_item(
    identifier: int,
    content: str = "The scheduler now defaults to chunked prefill.",
    *,
    url: str | None = None,
) -> RawItem:
    return RawItem(
        id=identifier,
        source_id="vllm",
        title=f"Release {identifier}",
        url=url or f"https://example.com/releases/{identifier}",
        published_at=datetime(2026, 7, 15, tzinfo=UTC),
        raw_content=content,
    )


def draft_output(*, excerpt: str = "The scheduler now defaults to chunked prefill.") -> str:
    return json.dumps(
        {
            "claims": [
                {
                    "text": "The scheduler now defaults to chunked prefill.",
                    "kind": "direct_fact",
                    "evidence": [{"raw_item_id": 1, "excerpt": excerpt}],
                },
                {
                    "text": "This may change throughput and latency assumptions.",
                    "kind": "inference",
                    "evidence": [{"raw_item_id": 1, "excerpt": excerpt}],
                },
                {
                    "text": "Benchmark a representative workload before rollout.",
                    "kind": "recommended_check",
                    "evidence": [{"raw_item_id": 1, "excerpt": excerpt}],
                },
            ],
            "affected_libraries": ["vllm"],
            "confidence": 0.88,
            "upstream_release_type": "patch",
            "operator_risks": ["performance"],
            "applicability_conditions": ["If your deployment uses the scheduler."],
        }
    )


class FakeClient:
    def __init__(self, outputs: list[str] | None = None) -> None:
        self.response_calls: list[dict] = []
        self.outputs = outputs or [draft_output(), json.dumps({"accepted_claim_indexes": [0, 1, 2], "notes": []})]

        class Responses:
            def __init__(inner_self, outer: FakeClient) -> None:
                inner_self.outer = outer

            def create(inner_self, **kwargs):
                inner_self.outer.response_calls.append(kwargs)
                return SimpleNamespace(output_text=inner_self.outer.outputs.pop(0))

        self.responses = Responses(self)
        self.closed = False

    def close(self) -> None:
        self.closed = True


def test_generate_insight_freezes_claim_evidence_and_verifies_it() -> None:
    client = FakeClient()
    items = [make_item(1), make_item(2)]

    result = insight.generate_insight(items, ChangeSeverity.BREAKING, tier=Tier.FINAL, client=client)

    assert result.raw_item_ids == [1, 2]
    assert result.title == "Release 1"
    assert result.summary == "The scheduler now defaults to chunked prefill."
    assert result.severity is ChangeSeverity.BREAKING
    assert result.source_citations == [item.url for item in items]
    assert result.model_used == "gpt-5.6-sol"
    assert result.confidence == 0.88
    assert result.publication_status is PublicationStatus.DRAFT
    assert result.verification_status is VerificationStatus.PASSED
    assert result.claims[0].kind is ClaimKind.DIRECT_FACT
    assert result.claims[0].evidence[0].start_char == 0
    assert result.claims[0].evidence[0].end_char == len(result.claims[0].evidence[0].excerpt)
    assert [call["text"]["format"]["name"] for call in client.response_calls] == [
        "drift_claim_draft",
        "drift_claim_verdict",
    ]
    assert "untrusted release evidence" in client.response_calls[0]["input"]
    assert client.closed is False


def test_generate_insight_retains_exact_github_pr_and_commit_cross_references() -> None:
    content = (
        "Fixes #42 and includes https://github.com/vllm-project/vllm/commit/abcdef1234567. "
        "The scheduler now defaults to chunked prefill."
    )
    exact_excerpt = "The scheduler now defaults to chunked prefill."
    client = FakeClient(outputs=[draft_output(excerpt=exact_excerpt), json.dumps({"accepted_claim_indexes": [0, 1, 2], "notes": []})])
    result = insight.generate_insight(
        [
            make_item(
                1,
                content,
                url="https://github.com/vllm-project/vllm/releases/tag/v0.25.1",
            )
        ],
        ChangeSeverity.MINOR,
        client=client,
    )

    references = result.claims[0].evidence[0].cross_references
    assert [(reference.kind, reference.identifier) for reference in references] == [
        ("release", "Release 1"),
        ("pull_request", "#42"),
        ("commit", "abcdef123456"),
    ]
    assert references[1].url.endswith("/pull/42")
    assert references[2].commit_sha == "abcdef1234567"


def test_generate_insight_with_audit_keeps_both_model_runs() -> None:
    generated = insight.generate_insight_with_audit([make_item(1)], ChangeSeverity.MINOR, client=FakeClient())

    assert generated.audit.model_used == "gpt-5.6-luna"
    assert len(generated.audit.evidence_sha256) == 64
    assert len(generated.audit.output_sha256) == 64
    assert generated.audit.attempts == 1
    assert generated.verification_audit.model_used == "gpt-5.6-luna"
    assert len(generated.verification_audit.evidence_sha256) == 64
    assert generated.verification_audit.attempts == 1


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
    client = FakeClient(outputs=[""])

    with pytest.raises(ValueError, match="empty Insight draft JSON"):
        insight.generate_insight([make_item(1)], ChangeSeverity.MINOR, client=client)


def test_generate_insight_rejects_invalid_and_schema_invalid_json() -> None:
    with pytest.raises(ValueError, match="invalid Insight draft JSON"):
        insight.generate_insight(
            [make_item(1)], ChangeSeverity.MINOR, client=FakeClient(outputs=["not-json"])
        )
    with pytest.raises(ValueError, match="failed schema validation"):
        insight.generate_insight(
            [make_item(1)],
            ChangeSeverity.MINOR,
            client=FakeClient(outputs=[json.dumps({"claims": []})]),
        )


def test_generate_insight_rejects_non_exact_evidence_and_unusable_verdicts() -> None:
    with pytest.raises(ValueError, match="not an exact source substring"):
        insight.generate_insight(
            [make_item(1)],
            ChangeSeverity.MINOR,
            client=FakeClient(outputs=[draft_output(excerpt="invented evidence")]),
        )
    # Verifier accepts nothing: no insight can be published.
    with pytest.raises(ValueError, match="accepted none of the drafted"):
        insight.generate_insight(
            [make_item(1)],
            ChangeSeverity.MINOR,
            client=FakeClient(outputs=[draft_output(), json.dumps({"accepted_claim_indexes": [], "notes": ["all unsupported"]})]),
        )
    # Verifier drops the only recommended check: the survivor is not inspectable.
    with pytest.raises(ValueError, match="no accepted recommended check"):
        insight.generate_insight(
            [make_item(1)],
            ChangeSeverity.MINOR,
            client=FakeClient(outputs=[draft_output(), json.dumps({"accepted_claim_indexes": [0, 1], "notes": ["action too broad"]})]),
        )
    # Verifier drops the only direct fact: the survivor has no upstream anchor.
    with pytest.raises(ValueError, match="no accepted direct factual"):
        insight.generate_insight(
            [make_item(1)],
            ChangeSeverity.MINOR,
            client=FakeClient(outputs=[draft_output(), json.dumps({"accepted_claim_indexes": [1, 2], "notes": []})]),
        )


def test_generate_insight_publishes_only_verifier_accepted_claims() -> None:
    # Verifier accepts the direct fact (0) and recommended check (2) but rejects
    # the inference (1); the insight publishes with only the two accepted claims.
    client = FakeClient(
        outputs=[
            draft_output(),
            json.dumps({"accepted_claim_indexes": [0, 2], "notes": ["inference unsupported"]}),
        ]
    )

    result = insight.generate_insight([make_item(1)], ChangeSeverity.MINOR, client=client)

    assert result.verification_status is VerificationStatus.PASSED
    assert [claim.kind for claim in result.claims] == [
        ClaimKind.DIRECT_FACT,
        ClaimKind.RECOMMENDED_CHECK,
    ]
    assert result.why_it_matters == "No additional operator interpretation was accepted from this evidence."


def test_claim_grounding_rejects_unknown_items_and_missing_required_claim_kinds() -> None:
    unknown_item = json.loads(draft_output())
    unknown_item["claims"][0]["evidence"][0]["raw_item_id"] = 99
    with pytest.raises(ValueError, match="was not supplied"):
        insight.generate_insight(
            [make_item(1)], ChangeSeverity.MINOR, client=FakeClient(outputs=[json.dumps(unknown_item)])
        )

    missing_fact = json.loads(draft_output())
    missing_fact["claims"] = missing_fact["claims"][1:]
    with pytest.raises(ValueError, match="direct factual"):
        insight.generate_insight(
            [make_item(1)], ChangeSeverity.MINOR, client=FakeClient(outputs=[json.dumps(missing_fact)])
        )

    missing_check = json.loads(draft_output())
    missing_check["claims"] = missing_check["claims"][:2]
    with pytest.raises(ValueError, match="bounded recommended"):
        insight.generate_insight(
            [make_item(1)], ChangeSeverity.MINOR, client=FakeClient(outputs=[json.dumps(missing_check)])
        )


def test_cross_reference_limit_stops_pr_and_commit_scans() -> None:
    many_prs = " ".join(f"#{number}" for number in range(1, 25))
    pr_references = insight._cross_references(
        make_item(
            1,
            many_prs,
            url="https://github.com/vllm-project/vllm/releases/tag/v0.25.1",
        )
    )
    assert len(pr_references) == insight._MAX_CROSS_REFERENCES

    commits = " ".join(
        f"https://github.com/example/runtime/commit/{number:040x}" for number in range(1, 25)
    )
    commit_references = insight._cross_references(make_item(1, commits))
    assert len(commit_references) == insight._MAX_CROSS_REFERENCES


def test_run_insight_batch_forwards_explicit_provider_controls(monkeypatch, tmp_path) -> None:
    calls: list[dict] = []

    def fake_generate(*_args, **kwargs):
        calls.append(kwargs)
        return make_item(1)  # type: ignore[return-value]

    monkeypatch.setattr(insight, "generate_insight", fake_generate)

    result = insight.run_insight_batch(
        [([make_item(1)], ChangeSeverity.MINOR)],
        client=object(),
        spend_guard=insight.SpendGuard(tmp_path / "ledger.json", 1, 0.5),
    )

    assert result[0].id == 1
    assert calls[0]["client"] is not None

"""Keep the no-key example claims as inspectable as their live counterparts."""

import json
from hashlib import sha256
from pathlib import Path

from backend.models.schema import Insight

_FIXTURE_PATH = Path("backend/fixtures/insights.json")
_SOURCE_DIRECTORY = Path("backend/fixtures/source_evidence")
_SOURCE_URL_PREFIX = (
    "https://github.com/iarjunganesh/drift/blob/v0.8.0/"
    "backend/fixtures/source_evidence/"
)


def test_fixture_claim_evidence_matches_frozen_synthetic_sources() -> None:
    """Fixture evidence is exact, shared per raw item, and never upstream data."""
    insights = [
        Insight.model_validate(item)
        for item in json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))
    ]
    source_texts = {
        int(path.stem): path.read_bytes().decode("utf-8")
        for path in _SOURCE_DIRECTORY.glob("*.txt")
    }

    referenced_raw_item_ids = set()
    for insight in insights:
        for claim in insight.claims:
            for evidence in claim.evidence:
                source_text = source_texts[evidence.raw_item_id]
                expected_url = f"{_SOURCE_URL_PREFIX}{evidence.raw_item_id}.txt"

                referenced_raw_item_ids.add(evidence.raw_item_id)
                assert evidence.raw_item_id in insight.raw_item_ids
                assert evidence.source_url == expected_url
                assert evidence.source_url in insight.source_citations
                assert evidence.source_sha256 == sha256(source_text.encode("utf-8")).hexdigest()
                assert source_text[evidence.start_char : evidence.end_char] == evidence.excerpt

    assert set(source_texts) == referenced_raw_item_ids

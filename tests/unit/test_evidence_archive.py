import json
from datetime import UTC, datetime
from hashlib import sha256

import pytest

from backend.evidence_archive import archive_reviewed_capture
from backend.models.schema import (
    ChangeSeverity,
    Insight,
    PublicationStatus,
    VerificationStatus,
)


def make_insight(
    *,
    publication_status: PublicationStatus = PublicationStatus.REVIEWED,
    verification_status: VerificationStatus = VerificationStatus.PASSED,
) -> Insight:
    return Insight(
        id=7,
        raw_item_ids=[11],
        title="Reviewed release",
        summary="A direct source fact.",
        why_it_matters="A labelled interpretation.",
        what_to_check="Run one bounded check.",
        severity=ChangeSeverity.MINOR,
        affected_libraries=["vllm"],
        source_citations=["https://example.com/release"],
        confidence=0.9,
        model_used="gpt-5.6-luna",
        publication_status=publication_status,
        verification_status=verification_status,
        human_review_notes="Private reviewer detail that must not be archived.",
        reviewed_at=datetime(2026, 7, 15, tzinfo=UTC),
    )


def test_archive_reviewed_capture_writes_scrubbed_evidence_and_manifest(tmp_path) -> None:
    result = archive_reviewed_capture(
        [make_insight()],
        archive_name="2026-07-15-all-sources-reviewed",
        capture_metadata={"source_ids": ["vllm"], "selected_count": 1},
        evidence_directory=tmp_path,
    )

    payload = json.loads(result.evidence_path.read_text(encoding="utf-8"))
    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    assert payload["record_type"] == "reviewed_manual_capture"
    assert payload["capture"]["source_ids"] == ["vllm"]
    assert "human_review_notes" not in payload["insights"][0]
    assert manifest["evidence_file"] == result.evidence_path.name
    assert manifest["sha256"] == result.sha256


def test_archive_manifest_hash_matches_exact_evidence_bytes(tmp_path) -> None:
    result = archive_reviewed_capture(
        [make_insight()],
        archive_name="2026-07-15-byte-exact",
        capture_metadata={"source_ids": ["vllm"], "selected_count": 1},
        evidence_directory=tmp_path,
    )

    evidence_bytes = result.evidence_path.read_bytes()
    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    # The recorded hash must match the evidence file's exact on-disk bytes, not a
    # newline-normalized variant. Guards the Windows write_text CRLF regression:
    # write_text would emit "\r\n" while the hash was computed over "\n" bytes.
    assert sha256(evidence_bytes).hexdigest() == manifest["sha256"]
    assert manifest["sha256"] == result.sha256
    assert b"\r\n" not in evidence_bytes
    assert b"\r\n" not in result.manifest_path.read_bytes()


def test_archive_reviewed_capture_rejects_unsafe_inputs_and_overwrite(tmp_path) -> None:
    with pytest.raises(ValueError, match="at least one"):
        archive_reviewed_capture(
            [], archive_name="2026-07-15-empty", capture_metadata={}, evidence_directory=tmp_path
        )
    with pytest.raises(ValueError, match="lowercase"):
        archive_reviewed_capture(
            [make_insight()], archive_name="Bad Name", capture_metadata={}, evidence_directory=tmp_path
        )
    with pytest.raises(ValueError, match="Only reviewed"):
        archive_reviewed_capture(
            [make_insight(publication_status=PublicationStatus.DRAFT)],
            archive_name="2026-07-15-draft",
            capture_metadata={},
            evidence_directory=tmp_path,
        )
    with pytest.raises(ValueError, match="Only verifier-passed"):
        archive_reviewed_capture(
            [make_insight(verification_status=VerificationStatus.LEGACY_UNVERIFIED)],
            archive_name="2026-07-15-unverified",
            capture_metadata={},
            evidence_directory=tmp_path,
        )
    with pytest.raises(ValueError, match="credentials or review notes"):
        archive_reviewed_capture(
            [make_insight()],
            archive_name="2026-07-15-secret-metadata",
            capture_metadata={"database_url": "postgresql://user:password@example.test/drift"},
            evidence_directory=tmp_path,
        )
    with pytest.raises(ValueError, match="JSON object"):
        archive_reviewed_capture(
            [make_insight()],
            archive_name="2026-07-15-list-metadata",
            capture_metadata=[],  # type: ignore[arg-type]
            evidence_directory=tmp_path,
        )
    with pytest.raises(ValueError, match="JSON values"):
        archive_reviewed_capture(
            [make_insight()],
            archive_name="2026-07-15-non-json-metadata",
            capture_metadata={"source_ids": {"vllm"}},
            evidence_directory=tmp_path,
        )

    archive_reviewed_capture(
        [make_insight()], archive_name="2026-07-15-existing", capture_metadata={}, evidence_directory=tmp_path
    )
    with pytest.raises(FileExistsError, match="already exists"):
        archive_reviewed_capture(
            [make_insight()],
            archive_name="2026-07-15-existing",
            capture_metadata={},
            evidence_directory=tmp_path,
        )

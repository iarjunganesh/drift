"""Write scrubbed, integrity-checked evidence records for reviewed captures."""

import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any

from backend.models.schema import Insight, PublicationStatus, VerificationStatus

_ARCHIVE_NAME = re.compile(r"^[a-z0-9][a-z0-9-]{2,100}$")
_SENSITIVE_METADATA = re.compile(
    r"(?:\b(?:api[_-]?key|access[_-]?token|authorization|credential|database[_-]?url|"
    r"password|secret|review[_-]?notes)\b|\bpostgres(?:ql)?(?:\+\w+)?://|\bbearer\s+|\bsk-[A-Za-z0-9])",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class EvidenceArchive:
    """The two durable artifact paths and content hash for one reviewed capture."""

    evidence_path: Path
    manifest_path: Path
    sha256: str


def _public_capture_metadata(capture_metadata: dict[str, Any]) -> dict[str, Any]:
    """Validate JSON metadata and reject common credential/review-note markers."""
    if not isinstance(capture_metadata, dict):
        raise ValueError("Capture metadata must be a JSON object.")
    try:
        serialized = json.dumps(
            capture_metadata,
            ensure_ascii=False,
            sort_keys=True,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise ValueError("Capture metadata must contain only JSON values.") from exc
    if _SENSITIVE_METADATA.search(serialized):
        raise ValueError("Capture metadata must not contain credentials or review notes.")
    return json.loads(serialized)


def archive_reviewed_capture(
    insights: list[Insight],
    *,
    archive_name: str,
    capture_metadata: dict[str, Any],
    evidence_directory: Path = Path("assets/evidence"),
) -> EvidenceArchive:
    """Create a dated, scrubbed evidence JSON and checksum manifest without overwrite."""
    if not insights:
        raise ValueError("Archive at least one reviewed Insight.")
    if not _ARCHIVE_NAME.fullmatch(archive_name):
        raise ValueError("Archive names must be lowercase letters, numbers, and hyphens.")
    for insight in insights:
        if insight.publication_status is not PublicationStatus.REVIEWED:
            raise ValueError("Only reviewed Insights may be archived as evidence.")
        if insight.verification_status is not VerificationStatus.PASSED:
            raise ValueError("Only verifier-passed Insights may be archived as evidence.")
    public_metadata = _public_capture_metadata(capture_metadata)

    evidence_path = evidence_directory / f"{archive_name}.json"
    manifest_path = evidence_directory / f"{archive_name}.manifest.json"
    if evidence_path.exists() or manifest_path.exists():
        raise FileExistsError("Evidence archive already exists; choose a new dated archive name.")

    payload = {
        "record_type": "reviewed_manual_capture",
        "archived_at": datetime.now(UTC).isoformat(),
        "capture": public_metadata,
        "insights": [
            insight.model_dump(mode="json", exclude={"human_review_notes"}) for insight in insights
        ],
        "limitations": [
            "This record contains reviewed captured evidence, not a guarantee of compatibility or release completeness.",
            "Operator risks and recommended checks are labelled interpretations, not upstream facts.",
        ],
    }
    serialized = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    evidence_bytes = serialized.encode("utf-8")
    content_sha256 = sha256(evidence_bytes).hexdigest()
    manifest = {
        "record_type": "evidence_integrity_manifest",
        "evidence_file": evidence_path.name,
        "sha256": content_sha256,
        "preservation_policy": "Do not overwrite this record; create a new dated archive for every capture.",
    }
    manifest_bytes = (json.dumps(manifest, indent=2) + "\n").encode("utf-8")

    evidence_directory.mkdir(parents=True, exist_ok=True)
    # Write raw bytes, not write_text: text mode translates "\n" to the platform
    # newline (CRLF on Windows), which would leave the manifest SHA-256 hashing
    # bytes the evidence file no longer contains. The recorded hash must match the
    # evidence file's exact on-disk bytes on every platform.
    evidence_path.write_bytes(evidence_bytes)
    manifest_path.write_bytes(manifest_bytes)
    return EvidenceArchive(evidence_path, manifest_path, content_sha256)

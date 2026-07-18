# Hosted evidence

This directory contains scrubbed, committed evidence from explicitly verified
hosted workflows. It must never contain API keys, database URLs, credentials,
or raw local spend-ledger files.

Evidence records identify their verification scope and limitations. In
particular, an unreviewed model capture is not a claim of broad or continuously
fresh release analysis.

The 2026-07-15 vLLM record predates the local claim-evidence/review-gate work.
It is historical pre-gate evidence and must not be described as verifier-passed,
human-reviewed, or proof that the current local publication policy is deployed.

Its adjacent `.manifest.json` records a SHA-256 checksum and preservation
policy. Do not overwrite that record; add any future all-source capture as a
new dated evidence file and manifest after human review.

The archive helper accepts JSON-only capture metadata and rejects common
credential, database-URL, and review-note markers before writing either file.
The 2026-07-18 Terra record is a grounded-chat capture over the reviewed store;
it is not a new Insight capture or a hosted deployment claim.

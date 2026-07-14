# Security Policy

## Supported versions

DRIFT is an early-stage build-week project. Security fixes apply to the current
development baseline while the live pipeline is being implemented.

| Version | Supported |
| --- | --- |
| `0.1.x` | ✅ Current baseline |

Fixture data is synthetic. Live ingestion and provider-backed generation are not
enabled in this baseline.

## Reporting a vulnerability

Please **do not open a public GitHub issue** for a security vulnerability.

Once the GitHub repository is published, use its private Security Advisory
reporting flow. Until then, report privately to the project maintainer through
the repository’s private contact channel; do not include credentials or
personal data in a public message.

Include:

- a concise description of the vulnerability;
- affected file, endpoint, dependency, or deployment surface;
- reproducible steps or a minimal proof of concept;
- potential impact and required conditions; and
- any suggested mitigation.

Please allow reasonable time for acknowledgement, validation, a fix, and a
coordinated disclosure decision.

## Security notes

- API keys and database URLs are loaded from environment variables only.
- `.env` files, credentials, and private provider responses must never be
  committed or pasted into issues, prompts, logs, or demo recordings.
- Release text is untrusted data and must not be treated as model instructions.
- Model/provider calls stay behind the router so secrets and budgets have one
  controlled boundary.
- Chat is retrieve-first; no-match requests must not fall back to ungrounded
  model knowledge.
- Fixture records are clearly labelled and are not represented as live analysis.
- CORS origins are explicit; the frontend never receives `DATABASE_URL`.
- Breaking or security-labelled insights increase review priority but never
  authorize automated infrastructure changes.
- The first public deployment should use `DRIFT_MODE=fixture` until live-stage
  security and provenance gates are complete.

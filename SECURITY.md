# Security Policy

## Supported versions

DRIFT is an early-stage build-week project. Security fixes apply to the current
development baseline while the live pipeline is being implemented.

| Version | Supported |
| --- | --- |
| `0.6.0` | ✅ Current local source release; hosted application deployment verification pending |
| `0.5.1` | Historical hosted baseline |

Fixture data is synthetic. Local live ingestion and provider-backed generation
are explicitly operator-enabled and review-gated; the updated gate has not yet
been deployed to the historical hosted baseline.

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
- Live release claims are frozen to exact source excerpts before persistence;
  a separate verifier and human review gate prevent drafts from reaching public
  live endpoints. The verifier is fallible and must not be treated as proof.
- Chat is retrieve-first; no-match requests must not fall back to ungrounded
  model knowledge.
- Fixture records are clearly labelled and are not represented as live analysis.
- CORS origins are explicit; the frontend never receives `DATABASE_URL`.
- Breaking or security-labelled insights increase review priority but never
  authorize automated infrastructure changes.
- Do not represent `v0.6.0` as hosted review-gated live analysis until its
  application deployment and reviewed endpoint smoke tests are verified.

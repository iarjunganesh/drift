# Security Policy

## Supported versions

DRIFT is an early-stage build-week project. Security fixes apply to the current
development baseline while the live pipeline is being implemented.

| Version | Supported |
| --- | --- |
| `0.10.2` | Current source release; adds a deterministic `upstream_release_type` classification (ADR-012) and applies it to three reviewed Insights via direct database write — no other Insight field, capture, or provider path changed |
| `0.10.1` | Prior source release; evidence/documentation patch on `0.10.0` that commits the VS Code MCP client evidence and synchronizes current-state records — no backend behavior change |
| `0.10.0` | ✅ Current hosted application; verified 2026-07-18: Railway `/health` and `/` report `0.10.0`, `/docs` returns `200`, `/briefing?top_n=10` returns the five reviewed Insights with no review notes, and Vercel CORS allows `GET, POST` (paid `/search`/`/chat` not re-invoked). Adds the `integrations/mcp/` thin-client MCP server, which carries no credentials and cannot reach the review gate; the scrubbed hosted MCP response archive is pending |
| `0.9.1` | Prior hosted application; verified earlier on 2026-07-18 with the same health/docs/briefing/CORS checks |
| `0.8.0` | Prior hosted application; on 2026-07-17 Railway `/health` reported `0.8.0`, `/docs` returned `200`, the public Vercel page rendered Ask DRIFT, and Vercel CORS was verified |
| `0.7.0` | Prior verified hosted application; public review notes are redacted and the frontend requests up to ten briefing records |
| `0.6.1` | Previously verified hosted application |
| `0.5.1` | Historical hosted baseline |

Fixture data is synthetic. Local live ingestion and provider-backed generation
are explicitly operator-enabled and review-gated; the hosted gate returned no
live evidence until the first human-reviewed capture. On 2026-07-16 it served
four human-reviewed Insights from an eight-source capture (six verifier-passed
drafts); as of 2026-07-18 the reviewed store serves five human-reviewed
Tier.FINAL Insights (10, 11, 13, 15, 16), verified through `/briefing` on the
deployed `0.10.0` build. Version `0.7.0` keeps human review notes database-only; its deployed
`/briefing` and `/openapi.json` boundaries were verified to omit them. Version
`0.8.0` keeps fixture evidence explicitly synthetic and locally verifiable; it
does not add an unverified hosted claim.

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
- The `integrations/mcp/` MCP server (ADR-011) is a thin client on the untrusted
  consumer side of the API boundary. It reads only `DRIFT_API_URL` (plus an
  optional `DRIFT_MCP_TIMEOUT_SECONDS` request timeout), holds no
  OpenAI key or database URL, and cannot draft, verify, publish, or retract an
  Insight. Reviewed-only reads, review-note redaction, spend guards, and
  resilience remain enforced server-side, because there is no second path to the
  store.
- Do not represent the hosted app as broad live analysis. As of 2026-07-18 the
  deployed `0.10.0` build serves five human-reviewed Insights (10, 11, 13, 15,
  16), verified through `/briefing`; hosted `/briefing`, `/search`, and `/chat`
  were verified provider-backed over the earlier reviewed set on 2026-07-16. This
  is a small, bounded reviewed set — not continuous or comprehensive release
  monitoring.

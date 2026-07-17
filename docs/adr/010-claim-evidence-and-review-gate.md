# ADR-010: Claim evidence and review-first publication

**Status:** Accepted  
**Date:** 2026-07-15

## Decision

Treat a live Insight as a set of typed claims, not an opaque summary. Every
claim retains one or more exact primary-source excerpts, character offsets,
the source-content SHA-256, and retained upstream release, pull-request, or
commit references when present. Claims are classified as `direct_fact`,
`inference`, or `recommended_check`.

Generate drafts through the routed model boundary, then run a separate
structured verifier call. The verifier may reject unsupported or misclassified
claims; a pass is model-aided screening, not proof. Persist generation and
verification audits independently.

All capture output is `draft`. Public live briefing, search, and chat return
only records that both passed verification and were explicitly promoted by a
human reviewer with meaningful review notes. Upstream release type is stored
separately from potential operator-risk labels.

## Context

The earlier contract preserved citation URLs and an audit label, which made a
record inspectable but did not show which source text supported a particular
sentence. It also allowed an unreviewed capture to be returned by local live
read paths. That is insufficient for a tool that aims to help engineers reason
about GPU and infrastructure release drift without overstating certainty.

## Consequences

- A model cannot invent an evidence offset or hash: code locates the supplied
  contiguous excerpt in persisted raw source content and freezes the result.
- A verifier rejection fails the capture instead of silently weakening the
  source boundary. The verifier remains fallible and requires human review.
- `severity` remains a review priority; it does not replace release type or
  establish compatibility/risk certainty.
- The public live store may be empty until reviewed captures exist. This is an
  intended fail-closed behavior, not a reason to show drafts.
- Migration `0003_claim_evidence_review_gate` makes existing rows
  `legacy_unverified` and `draft`, so historical captures cannot pass the new
  publication predicate merely by existing in the database.
- The local manual notebook uses the same pipeline and promotion function,
  rather than adding a parallel, less-guarded Railway execution path.
- Reviewed captures can be archived as dated, scrubbed evidence JSON with a
  SHA-256 sidecar manifest. Archives omit human review notes and secrets and
  cannot overwrite a prior capture record.

## Implementation addendum — 2026-07-15

`backend/agents/insight.py` now drafts typed claims and invokes the separate
verifier. `backend/pipeline.py` records both audits and persists drafts only.
`backend/review.py` is the explicit promotion gate. `backend/core/live_store.py`
filters live reads to verified/reviewed rows, and the frontend displays claim
types and evidence when present. Calibration fixtures cover unsupported claims,
ambiguous interpretation, and instruction-shaped release text. The changes are
locally tested; Railway PostgreSQL was verified at migration `0003` through its
public TCP proxy on 2026-07-16. Later that day hosted `v0.6.1` health, empty
fail-closed briefing, branded docs/banner routes, and CORS were verified. The
2026-07-15 hosted vLLM response remains historical pre-gate evidence; on
2026-07-16, four human-reviewed Insights were published and hosted
`/briefing`/`/search`/`/chat` verified provider-backed.

**2026-07-16 privacy addendum:** `v0.7.0` makes `human_review_notes`
database-only in the serialized Insight contract and prevents the live-store
reader from copying them into public records. It also tests the public API and
OpenAPI boundary. The Git-connected `v0.7.0` deployment was verified to omit
the field from `/briefing` and `/openapi.json`.

**2026-07-17 fixture addendum:** `v0.8.0` makes no-key example claims conform
to the same evidence contract without representing synthetic text as an
upstream release. Each fixture evidence reference resolves to a checked-in,
explicitly synthetic source file; the full-file SHA-256, exact excerpt, offsets,
source URL, and raw-item relationship are asserted by a regression test. This
is source-release behavior only until a hosted deployment is observed.

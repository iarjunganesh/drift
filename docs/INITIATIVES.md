# DRIFT project initiatives

These are the twelve Codex project initiatives associated with the DRIFT baseline,
publication follow-up, `0.2.0` release candidate, and the current build-sequence
implementation work. They are submission evidence pointers for the build work;
they are not model-run provenance and do not turn fixture records into live
analysis.

## Initiative 01 — Foundation and inspectable vertical slice

**Codex Session ID:** `019f61e7-1ea1-7742-9acc-99d62f39b888`

This initiative established the DRIFT foundation:

- fixture-first FastAPI path and typed Pydantic contracts;
- explicit Scout, Synthesizer, Insight, and Briefing boundaries;
- citation, confidence, severity, audit-label, and bounded-action invariants;
- deterministic briefing/search/chat behavior;
- model-router and local budget boundaries; and
- initial tests, coverage enforcement, and architecture decisions.

## Initiative 02 — Publication and judge-readiness baseline

**Codex Session ID:** `019f61fc-c32e-7d92-9d2e-0bd9083d08e7`

This initiative prepared the repository for public judging and continued work:

- README, architecture, ADR, runbook, contribution, and security documentation;
- Mermaid source with light/dark SVG and PNG architecture renders;
- Python and frontend lockfiles, CI/release workflows, Codecov configuration,
  Docker, Railway, and Vercel deployment surfaces;
- local Next.js briefing view and three-minute demo script; and
- GitHub publication, `v0.1.0`, Codecov activation, and submission handoff plan.

## Initiative 03 — Hosted deployment and README follow-up

**Codex Session ID:** `019f6253-ddfc-7272-8077-e34dfb3aee84`

This initiative records the hosted publication follow-up:

- Railway Docker deployment URL and `/health` route alignment;
- Vercel frontend and Railway API links in the public README;
- public endpoints `https://dr1ftless.vercel.app` and
  `https://drift-api-prod.up.railway.app`;
- release badge and demo-surface cleanup; and
- continued separation between the hosted fixture path and the future live
  release-analysis pipeline.

## Initiative 04 — Grounded live chat, resilience, and locked delivery

**Codex Session ID:** `019f62b9-10b7-7d82-a463-e6eb1192141c`

This was the primary implementation initiative for the v0.2.0 release
candidate. It delivered:

- retrieve-first, citation-preserving local live chat over the fixture store,
  without representing fixture evidence as live release analysis;
- `.env` development loading without reading, logging, or overriding secrets;
- a single application-owned async resilience policy: queue-bounded
  concurrency, per-attempt timeout, jittered transient retry, circuit breaker,
  cancellation-safe cleanup, and conservative spend settlement;
- a single frozen Python dependency resolution path through `uv.lock` for
  local development, CI, and the Railway image; and
- deterministic tests covering the implemented behavior at a 100% coverage
  floor, with future live-stage raises left explicit.

## Initiative 05 — Day 1 feed/database foundation and Day 2 Synthesizer

**Codex Session ID:** `019f62e8-6715-70e2-a92a-fe28254f7b71`

**Date:** 2026-07-15

This session completed the Day 1 and Day 2 implementation slices in
`docs/BUILD_SEQUENCE.md`, then reconciled the project’s status-bearing
instructions and evidence. It is a substantive implementation follow-up to
Initiative 04, not a replacement for Initiative 04’s primary session ID.

### Day 1 — Scout ingestion

- Implemented real HTTP feed retrieval in `backend/agents/scout.py` using
  `feedparser` over the eight configured GitHub Atom sources.
- Added explicit transport timeout handling, HTTP status classification,
  malformed-feed rejection, title/link validation, publication-date
  normalization, content extraction, and canonical URL deduplication.
- Reused the application `RetryPolicy` for bounded retry/backoff behavior,
  continued after an individual source failure, and emitted structured
  source/item-count/attempt/duration logs.
- Added async `store_sources()` and `store_raw_items()` helpers with database
  URL deduplication, within-batch suppression, and commit behavior.
- Added bounded Scout settings to `backend/core/config.py` and documented the
  knobs in `.env.example`.

### Day 1 — PostgreSQL and pgvector foundation

- Wired SQLAlchemy 2.x async metadata, engine, session factory, and a
  FastAPI/job-friendly `get_session()` dependency in
  `backend/models/schema.py`.
- Added typed ORM rows for `sources`, `raw_items`, and `insights`, including
  foreign keys, unique source URLs, JSONB provenance arrays, confidence range
  validation, timestamps, and `Vector(1536)` insight embeddings.
- Added `alembic.ini`, migration environment/template files, and the initial
  migration that enables pgvector and creates the three durable tables and
  indexes.
- Wired the migration into the container and `make migrate`, while preserving
  the database-free fixture path.

### Day 2 — Synthesizer stages

- Added a synchronous routed provider client and centralized embedding and
  structured-response helpers in `backend/core/model_router.py`; provider
  model identifiers remain router-owned.
- Implemented `embed_items()` as a batched `text-embedding-3-small` call with
  deterministic response ordering and safe ownership/cleanup of clients.
- Implemented `cluster_items()` as validated, deterministic greedy cosine
  clustering with an explicit similarity threshold and dimension/zero-vector
  handling.
- Implemented `classify_change()` as a narrow Tier.DEV structured severity
  call using the `ChangeSeverity` vocabulary, strict output validation, and
  bounded evidence serialization.
- Kept release text inside an untrusted data boundary and made
  `run_synthesizer()` share one client across the batch instead of creating a
  client per stage.

### Verification evidence

- Real Scout smoke run: all eight configured GitHub Atom feeds succeeded with
  ten normalized items each, for 80 fetched items; the smoke path made no
  model calls and did not write to the database.
- Initial Day 1/Day 2 checkpoint: 79 tests passed with 100.00% backend line
  coverage.
- Post-release v0.3.1 validation at the close of Initiative 05: 80 tests
  passed with 100.00% backend line coverage after making orchestration tests
  independent of local credentials.
- `uv run ruff check --fix backend tests` passed.
- `uv run mypy backend` passed with no issues.
- `git diff --check` passed after the implementation and documentation edits.
- Provider behavior in Day 2 tests is mocked; no paid model call is presented
  as implementation evidence.

### Documentation and session synchronization

- Added mandatory start/end reconciliation rules to `AGENTS.md`, including
  status, deployment, URL, checklist, ADR, changelog, and stale-reference
  checks for every session.
- Reconciled `README.md`, `BUILD_SEQUENCE.md`, `CODEX_PROMPTS.md`,
  `ARCHITECTURE.md`, `RUNBOOK.md`, ADR indexes/addenda, `CHANGELOG.md`, and
  submission notes with the implemented state.
- Recorded the hosted facts verified on 2026-07-15: Railway is in bounded
  `DRIFT_MODE=live`, Vercel CORS is enabled, and only grounded `/chat` uses
  the live model tier; `/briefing` remains fixture-backed.
- Removed the obsolete project reference requested earlier and retained both
  session IDs additively, with Initiative 04 remaining the primary
  `/feedback` session.

### Explicit remaining boundaries at the close of Initiative 05

The following were intentionally not marked complete because the code and
hosted behavior do not yet support those claims:

- applying the migration to a clean PostgreSQL instance and wiring scheduled
  Scout persistence into the service;
- persisting Day 2 vectors to `InsightRow` and adding live-store/pgvector
  retrieval;
- implementing structured Insight generation, provenance persistence, and a
  controlled Scout → Synthesizer → Insight → Briefing run; and
- broadening hosted `/briefing` beyond fixtures or claiming live release
  analysis. A hosted provider `/chat` smoke result still needs to be recorded
  separately from the verified health/CORS checks.

## Initiative 06 — Day 3/4 Insight agent

**Codex Session ID:** `019f6336-3690-7022-a8ef-c8c0947e240f`

**Date:** 2026-07-15

The standalone `generate_insight()` stage is now implemented. It sends bounded
release evidence through the model router, requests strict structured output,
validates the model-owned explanation fields, and derives source citations,
severity, raw-item IDs, and model provenance from trusted pipeline inputs. The
mocked test suite now passes 87 tests with 100.00% backend coverage.

Durable Insight/provenance persistence, embedding population, and controlled
Scout → Synthesizer → Insight → Briefing wiring remain incomplete; hosted
`/briefing` remains fixture-backed.

## Current status addendum — Day 5 pgvector retrieval

The local live-store path now embeds a query through the model router, orders
populated `InsightRow.embedding` values by pgvector cosine distance, maps rows
back to the cited `Insight` contract, and uses that retrieval for live
`/search` and `/chat`. The later capture-path follow-up expanded the suite to
118 tests at 100.00% backend coverage.

The local capture path now supplies durable Insight/embedding population and
model-run/source-hash provenance. A real PostgreSQL integration run, reviewed
real-model captures, deployed capture-job verification, and hosted verification
remain incomplete.

## Initiative 07 — Bounded capture, provenance, and status cleanup

**Codex Session ID:** `019f66b4-78b8-7943-a41d-91e836d28f00`

**Date:** 2026-07-15

This session closed the local code gap between the individual typed stages and
an inspectable, persisted capture path:

- added a one-shot `backend.pipeline` CLI that selects a bounded source set,
  persists and reloads raw evidence, synthesizes and generates Insights,
  embeds them, and writes the cited live store;
- added source-content hashes, `model_runs` audit rows, response-token/cost and
  retry-attempt records, plus optional human review notes and timestamps;
- extended the bounded retry/circuit and spend-reservation policy to sync
  embeddings, classification, and Insight generation rather than chat alone;
- made local live `/briefing` read the captured store and exposed confidence,
  model/audit labels, and source links in the frontend; and
- corrected the misleading fixture `security` label and reconciled the project
  status documents with the new local boundary.

The session did not run a paid model capture, apply migrations to a real
PostgreSQL service, deploy, record a video, or submit the project. Those remain
operator-owned verification gates.

## Initiative 08 — Grounding guardrails and capture readiness

**Codex Session ID:** `019f6773-0e96-7363-9657-0e0531c3d594`

**Date:** 2026-07-15

This follow-up assessed the first hosted vLLM evidence against its primary
release note and prepared the bounded capture path for a broader source pass:

- confirmed the first vLLM Insight's core change claims against the upstream
  v0.25.1 release note, while separating direct facts from inferred impact and
  recommended checks;
- bounded only the derived raw-item text sent to embeddings, preserving full
  source evidence and provenance in the durable store;
- corrected successful embedding settlement to use returned token usage rather
  than the conservative per-call cap, with mocked coverage;
- documented the remaining claim-level citation, verification, severity, and
  publication-gate requirements before DRIFT can promise truth-like engineer
  guidance; and
- verified Ruff, mypy, 124 tests, and 100.00% backend coverage. An all-source
  preflight fetched 80 feed items and selected one from each of eight sources;
  the authorized capture itself was blocked before database/model calls because
  this workspace cannot resolve Railway's private PostgreSQL hostname.

The first hosted vLLM record remains a single unreviewed, source-grounded
capture; this initiative does not turn it into a broad live-analysis claim.

### Implementation addendum — 2026-07-15

The planned guardrails are now implemented locally and covered by 150 tests at
100.00% backend coverage:

- each live claim has a type, frozen exact primary-source excerpt, character
  offsets, SHA-256 source hash, and retained GitHub release/PR/commit references
  where present;
- a separate routed verifier rejects unsupported/misclassified drafts, while
  remaining explicitly model-aided screening rather than proof;
- `upstream_release_type` is separate from potential `operator_risks` and
  applicability conditions;
- captures persist as drafts, and local briefing/search/chat filter to only
  human-reviewed verifier-passed records after meaningful review notes;
- calibration fixtures cover unsupported claims, ambiguity, and
  instruction-shaped release text; and
- `notebooks/drift_manual_run.ipynb` runs the same guarded local capture/review
  flow, refuses Railway's private database hostname, and starts with one item
  per configured source (at most eight).

Railway PostgreSQL schema `0003_claim_evidence_review_gate` was verified
through its public TCP proxy on 2026-07-16. Later that day hosted `v0.6.1`
health, empty fail-closed briefing, `/docs`, Vercel canonical-banner source,
and CORS were verified. On 2026-07-16, four human-reviewed Insights were
published and hosted `/briefing`, `/search`, and `/chat` were verified
provider-backed. The prior hosted vLLM capture is
historical pre-gate evidence and is not retroactively reviewed.

## Initiative 09 — Submission audit and frontend evidence presentation

**Codex Session ID:** `019f6a46-e3eb-7de2-81b1-91515ae80043`

**Date:** 2026-07-16

This follow-up audited the handwritten submission next steps against the local
source and deployed boundaries. It made the frontend distinguish loading, API
failure, and the intentional empty reviewed-evidence state; aligned the page
palette with the user's light/dark preference; and made the frontend load the
canonical banners through FastAPI's `assets/brand/` routes without a duplicate
Vercel copy. It also synchronized the current 142-test result, public clone
URLs, legacy path cleanup, and status documentation. It did not publish a
reviewed capture, call a provider, deploy Vercel, record the demo video, or
change the primary Initiative 04 `/feedback` session. The Git-connected
`v0.6.1` deployment subsequently reached Railway and Vercel; its Railway
health, docs, CORS, and Vercel banner source were verified, and a later
2026-07-16 session published four human-reviewed Insights with hosted
`/briefing`, `/search`, and `/chat` verified provider-backed. The amended
`v0.6.1` release also makes the API-docs banner frame system-theme-aware.

## Initiative 10 — Reviewed-evidence hardening and v0.8.0 hosted verification

**Codex Session ID:** `019f6a78-6fa2-7121-9059-85ac8ceb9904`

**Dates:** 2026-07-16–17

This initiative audited and completed the reviewed-evidence release boundary:

- fixed the Windows evidence-manifest newline mismatch and preserved byte-exact
  SHA-256 verification;
- made human review notes database-only in public API serialization and OpenAPI;
- made the saved results notebook Markdown-only and added a regression test;
- verified Railway `v0.7.0`, public redaction, Vercel CORS, and the deployed
  ten-item briefing request; and
- synchronized release, architecture, ADR, runbook, and submission records;
- carried the same work through the `v0.8.0` release: corrected no-key
  fixture claims to use explicitly synthetic, checked-in source text with
  byte-exact hashes/spans, aligned the Ask DRIFT UI with the `/chat` contract,
  added the regression test, and performed the final status/version sweep; and
- verified the Git-connected `v0.8.0` rollout: Railway `/health` reported
  `0.8.0`, `/docs` returned `200`, the public Vercel page rendered Ask DRIFT,
  Vercel CORS passed, and a tag-pinned fixture source resolved. Paid `/search`
  and `/chat` were not re-invoked.

## Initiative 11 — Freeze-plan audit and documentation synchronization

**Codex Session ID:** `019f7190-912d-70e3-be6d-fcc81bf8e203`

**Date:** 2026-07-17

This session performed a deep audit of `submission/DRIFT_FREEZE_PLAN.md`
against tracked implementation, assets, tests, deployment records, and
submission requirements. It corrected the plan's false shipped-status marks
for release timeline, MCP, tool calling, and IDE integration; aligned the
demo duration with the under-three-minute requirement; recorded the available
screenshots and missing GIFs; and synchronized the project session registries.
It did not add product features, alter hosted state, or replace the primary
Devpost `/feedback` session.

## Initiative 12 — v0.9.0 evidence cleanup and session synchronization

**Codex Session ID:** `019f7213-be19-7e50-92ac-a48bd5ecaacb`

**Date:** 2026-07-18

This follow-up retracted superseded Luna Insights 3, 6, 7, and 8 through the
audited `REVIEWED → DRAFT` helper, verified the hosted five-record Sol
briefing, synchronized the v0.9.0 release boundary, and made the Luna results
notebook name explicit for future Terra results.

It did not commit, push, or redeploy the application.

## Submission usage

Devpost requires one primary `/feedback` session, use Initiative 04. All twelve
IDs should be retained in the project README, changelog, and submission notes.
If Devpost requires one primary `/feedback` session, use Initiative 04:
`019f62b9-10b7-7d82-a463-e6eb1192141c`. Initiative 05 is the additive Day 1/Day
2 implementation and synchronization record, Initiative 06 is the additive
Day 3/Day 4 Insight implementation record, and Initiative 07 is the bounded
capture/provenance and cleanup record. Initiative 08 is the additive grounding
guardrail and capture-readiness record, Initiative 09 is the additive
submission-audit/frontend-presentation record, and Initiative 10 is the
reviewed-evidence hardening and `v0.8.0` hosted-verification
record; the earlier sessions remain the foundation, publication, and hosted-demo
follow-up initiatives, Initiative 11 is the additive freeze-plan audit and
documentation-synchronization record, and Initiative 12 is the v0.9.0 evidence
cleanup and session-synchronization follow-up.

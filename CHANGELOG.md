# Changelog

All notable changes to DRIFT are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) · Versioning:
[Semantic Versioning](https://semver.org/)

The `0.1.0` entry is the initial repository baseline published on GitHub as
the annotated `v0.1.0` tag.

## [Unreleased]

### Added

- **Ask DRIFT** grounded-chat box in the frontend (`frontend/app/AskDrift.tsx`):
  a single client component that posts a question to `/chat` and renders the
  grounded answer, its source citations, the model/audit label, and the grounded
  insight IDs, with explicit loading, no-match (HTTP 404), and error states. It
  works in both fixture and live mode. The `/chat` contract was verified against
  the fixture backend and the production frontend build passes.
- Embedded the reviewed-briefing and claim-evidence screenshots in the README as
  live-state visual evidence (`assets/screenshots/03-briefing.png` and
  `04-briefing-claim-evidence.png`), alongside the branded Swagger and
  architecture assets.

### Changed

- Restructured the README top for first impression: **The Problem → What DRIFT
  Does → Try DRIFT in 60 Seconds**, leading with the hosted demo links and a
  one-command `docker compose up` judge path. Reframed the closing **Disclaimer**
  as a positive **Trust Model** (untrusted input → frozen source span → separate
  verifier pass → human review gate) and kept the Codex/GPT-5.6 usage section
  prominent.
- Made the Quick Start cross-platform: promoted `docker compose up` as the
  one-command local path and added bash/curl equivalents beside every PowerShell
  command (setup, endpoint calls, and the live capture command).
- Renamed the tracked UI screenshots to clean kebab-case filenames
  (`01-landing`, `02-api-docs`, `03-briefing`, `04-briefing-claim-evidence`) so
  they embed reliably in Markdown.

## [0.7.0] - 2026-07-16

### Hosted deployment verification — 2026-07-16

- Verified the Git-connected Railway `v0.7.0` deployment in `DRIFT_MODE=live`:
  `/health` reports `0.7.0`, `/docs` returns `200`, and a Vercel-origin CORS
  preflight allows `GET, POST`.
- Verified that `/briefing?top_n=10` returns the four reviewed Insights without
  `human_review_notes`, and that `/openapi.json` does not expose that field.
- Verified the deployed Vercel bundle requests `briefing?top_n=10`.

### Reviewed-evidence capture and hosted verification — 2026-07-16

- Published four human-reviewed Insights through `publish_verified_insights`
  after source-excerpt review: Transformers v5.14.1, vLLM v0.25.1,
  NCCL v2.30.7-1, and TensorRT 11.1 (draft IDs 3, 6, 7, 8; drafted and verified
  at the `dev` / `gpt-5.6-luna` tier to bound cost).
- Verified the hosted Railway `v0.6.1` app in `DRIFT_MODE=live` now returns
  provider-backed content: `/briefing` is non-empty, `/search?q=vllm` returns
  the vLLM v0.25.1 Insight, and `/chat` returns a grounded `gpt-5.6-terra`
  answer citing the vLLM/NCCL/Transformers releases
  (`grounded_insight_ids` [6, 7, 3]). This supersedes the earlier empty
  fail-closed briefing verification.
- Archived the reviewed evidence and SHA-256 integrity manifest to
  `assets/evidence/2026-07-16-all-sources-reviewed.json`
  (sha256 `2e08896b3c1c9507b557fc84e5558ce05343f9202227bb3a1ff7e964002d2318`).

### Fixed

- Prevented empty or truncated structured-model responses from aborting a
  capture. Reasoning tokens share the response budget, so the output-token
  ceilings were raised for severity classification (40 → 256), Insight drafting
  (1200 → 4000), and the claim verifier (400 → 800).
- Raised the frontend briefing request from `top_n=3` to `top_n=10` so the home
  page surfaces every reviewed Insight across sources, not just the top three
  (the `/briefing` endpoint already accepts `top_n` up to 10).

### Changed

- The capture pipeline now generates each cluster's Insight independently and
  skips — with a logged `insight.generate.skipped` warning — any cluster whose
  draft fails grounding or verification, instead of discarding the whole run on
  a single failed cluster.
- The claim verifier now publishes only the verifier-accepted claims and drops
  the rejected ones, still requiring at least one direct fact and one
  recommended check, rather than rejecting an entire Insight when any single
  claim is rejected.

### Added

- `scripts/check_openai_spend.py`: a read-only, admin-key OpenAI cost check that
  reconciles the DRIFT project's real spend against the local
  `.drift/spend-ledger.json` guard (the local guard tracks only DRIFT's calls, so
  reconciliation is scoped to an explicit `--project-id` / `DRIFT_OPENAI_PROJECT_ID`
  rather than the organization total), with `scripts/README.md`. Uses the Costs
  API `group_by`/`project_ids` array query parameters.

### Testing

- Added pipeline tests for per-cluster skip-on-failure and the all-skipped
  guard, an Insight test for publishing only verifier-accepted claims, and
  updated the claim-grounding calibration eval so an ambiguous inference is
  dropped while the verified fact and check survive.

### Evidence-integrity, review-note redaction, and notebook hardening — 2026-07-16

- Fixed the evidence archive writer to emit raw LF bytes (`write_bytes`) so the
  manifest SHA-256 matches the evidence file's exact on-disk bytes on every
  platform; `write_text` previously translated `\n` to `\r\n` on Windows,
  leaving the manifest hashing bytes the file no longer contained. Added
  `.gitattributes` pinning `assets/evidence/*.json` to LF so `core.autocrlf`
  cannot re-introduce the mismatch, and a byte-level hash regression test.
- Made `human_review_notes` database-only: the public `Insight` contract now
  excludes it from serialization (`Field(exclude=True)`) and the live-store
  reader no longer copies it across the API boundary, so `/briefing`, `/search`,
  and `/chat` can never return internal review text. Added model- and
  endpoint-level regression tests.
- Sanitized `notebooks/drift_manual_run.ipynb` to a clean, output-free template
  (reset capture trigger, publish/archive IDs, and review notes), and made
  `notebooks/drift_manual_run.results.ipynb` a Markdown-only display record;
  it contains no runnable cells, operator configuration, provider/budget logs,
  or review notes. A regression test protects that boundary.
- Full suite: 149 tests at 100% backend coverage.

## [0.6.1] - 2026-07-16

### Fixed

- Made the FastAPI documentation banner frame follow `prefers-color-scheme`,
  so the light canonical banner no longer sits inside a dark wrapper.

- Made the frontend briefing state explicit: it now distinguishes a loading
  request, an unreachable API, and the intentional empty state before reviewed
  evidence has been published.
- Made the frontend select the API-served canonical DRIFT banner pair with
  `prefers-color-scheme`; it no longer copies SVGs into the Vercel build, and
  its palette follows the same light/dark system preference as the README and
  API docs.
- Corrected current local-test documentation to 142 tests at 100.00% backend
  coverage and replaced the placeholder clone URL.

### Hosted deployment verification — 2026-07-16

- Verified the Git-connected Railway `v0.6.1` deployment in `DRIFT_MODE=live`:
  `/health` reported `v0.6.1`, `/briefing` returned `[]` because no Insight is
  human-reviewed, `/docs` returned `200`, and a Vercel-origin CORS preflight
  passed.
- Verified that the deployed Vercel HTML references the canonical API-served
  light/dark banner pair. This is source-markup verification, not a separate
  browser visual check of the post-fetch empty state.

### Codex session record

- Added `019f6a46-e3eb-7de2-81b1-91515ae80043` for the submission audit and
  frontend evidence-presentation follow-up. Initiative 04 remains the primary
  `/feedback` session for core functionality.

## [0.6.0] - 2026-07-16

At release-tag creation, `v0.6.0` was the current local source release and its
hosted verification had not yet occurred. The dated hosted-deployment addendum
below records the subsequent verification without rewriting that history.

### Hosted deployment verification — 2026-07-16

- Verified the Git-connected `v0.6.0` Railway deployment in `DRIFT_MODE=live`:
  `/health` reported `v0.6.0`, `/briefing` returned `[]` because no Insights are
  human-reviewed, and branded `/docs`, `/brand/dark.svg`, and `/brand/light.svg`
  returned `200`.
- Verified the Vercel frontend serves the canonical banner and Railway accepts a
  Vercel-origin CORS preflight. Hosted `/search` and `/chat` remain untested to
  avoid provider-backed calls before a reviewed capture exists.

### Added

- Added migration `0003_claim_evidence_review_gate`, typed claim contracts, and
  frozen exact evidence spans with character offsets, source SHA-256 hashes,
  and retained upstream GitHub release/PR/commit references where present.
- Added a separate, routed structured claim-verifier call and a second durable
  `model_runs` audit pointer for each generated draft. The verifier rejects
  unsupported or misclassified claims but remains model-aided screening, not
  proof.
- Added explicit `direct_fact`, `inference`, and `recommended_check` labels;
  separate upstream release-type, potential operator-risk, and applicability
  metadata; and claim-evidence presentation in the frontend.
- Added `backend.review.publish_verified_insights()` and the judge-facing
  **DRIFT Manual Run** in `notebooks/drift_manual_run.ipynb`. It makes the source
  roster, spend-gated capture, claim evidence, human review, and archive proof
  chain visible; it starts at one item per configured source (at most eight),
  refuses Railway's private database hostname, and leaves publication empty by
  default.
- Added reviewed-capture evidence archiving with a SHA-256 sidecar manifest.
  The notebook archives only reviewed verifier-passed Insights, excludes review
  notes/secrets, and refuses to overwrite a dated record.
- Added claim-grounding calibration fixtures/tests for unsupported facts,
  ambiguous interpretation, and instruction-shaped release text.

### Changed

- Replaced the canonical dark and light DRIFT brand banners with a cinematic,
  semiconductor-inspired evidence path. Vercel derives the dark variant from
  `assets/brand/` at build time; the README renders the dark/light pair by
  color scheme. Both show an explicitly connected primary-release → GPU
  compute-lattice → evidence/review/check story with source-neutral copy.
  Headline spacing is responsive and avoids compressed word shapes at narrow
  widths.
- Capture output is now always a verifier-passed **draft**. Live briefing,
  search, and chat filter to human-reviewed drafts with recorded review notes;
  no capture flag can publish output automatically.
- Updated the product contract: DRIFT offers traceable primary facts, labelled
  interpretation, and bounded checks—not a compatibility verdict, guarantee, or
  automated infrastructure decision.
- Updated architecture, ADRs, runbook, build sequence, contributor guidance,
  submission guidance, and diagrams for the review-first boundary.

### Fixed

- Added an optional `DRIFT_DATABASE_PUBLIC_HOST` / `DRIFT_DATABASE_PUBLIC_PORT`
  override that preserves a private Railway `DATABASE_URL`'s credentials and
  database name while routing local notebook/Alembic connections through its
  public TCP proxy.
- Bound only the derived raw-item text sent to `text-embedding-3-small`, while
  preserving complete fetched evidence for provenance and Insight generation.
  This prevents oversized release bodies from exceeding the embedding API's
  per-input limit during a bounded capture.
- Settle successful embedding calls from their returned token usage and the
  router's embedding rate, rather than recording the full conservative call
  cap as spend. Failed or usage-unknown calls remain conservatively capped.
- Reject non-JSON or secret-shaped capture metadata before an evidence archive
  can be written, preserving the archive's no-credentials/no-review-notes
  contract at the helper boundary as well as in the notebook.

### Hosted verification

- On 2026-07-16, Railway PostgreSQL was verified at
  `0003_claim_evidence_review_gate` through its public TCP proxy before the
  subsequent `v0.6.0` application deployment verification recorded above.
- On 2026-07-15, the previous hosted `v0.5.1` deployment applied migrations
  through `0002_capture_provenance` and served one unreviewed vLLM Insight from
  public `/briefing` with its primary citation; Vercel CORS preflight also
  passed. This historical application verification predates `0003`; it is not
  evidence of review-gated live analysis.
- Added a scrubbed, committed hosted-evidence record under `assets/evidence/`;
  it preserves the verified response and boundaries without credentials or
  local spend-ledger data.

## [0.5.1] - 2026-07-15

Railway PostgreSQL connection-string compatibility patch.

### Fixed

- Normalize provider-native `postgres://` and `postgresql://` connection URLs
  to SQLAlchemy's required async `postgresql+asyncpg://` dialect before the
  application engine or Alembic migration environment is initialized.
- Added full branch coverage for native, legacy, and already-normalized
  PostgreSQL connection URLs, so the Railway database reference can be used
  directly without composing credential variables.

### Deployment note

- The API service must reference the database service's complete native
  `DATABASE_URL`; `v0.5.1` supplies the driver normalization. Applying
  migrations and creating the first reviewed capture remain operator actions.

## [0.5.0] - 2026-07-15

Bounded local capture-path release with persisted source and model provenance.

### Added

- Added a bounded one-shot `backend.pipeline` capture job that persists and
  reloads primary-source evidence, generates and embeds Insights, writes the
  live store, and records optional human review notes.
- Added Alembic revision `0002_capture_provenance` with source-content hashes,
  durable `model_runs` audit rows, Insight-to-run linkage, and review metadata.
- Added bounded spend reservation and retry/circuit handling to synchronous
  embedding, classification, and Insight-generation provider calls.
- Added local live-store-backed `/briefing` and frontend cards that expose
  source links, confidence, model/audit label, rationale, and bounded action.

### Changed

- Corrected the generic NCCL fixture from an unsupported `security` label to
  `minor`; fixture records remain examples, not release findings.
- Removed the superseded `docs/DRIFT_Realistic_Next_Steps.md` plan and
  synchronized current-state documentation with the capture boundary.
- Verified 118 tests at 100.00% backend coverage with Ruff, mypy, and the
  frontend production build passing.

### Remaining operator gates

- Apply the new migration to a clean PostgreSQL/pgvector instance, run and
  review real model captures, then deploy and verify the updated hosted path.
- Record the public narrated demo and submit the Developer Tools entry.

### Codex session record

All project-session IDs are retained here in addition to
[`docs/INITIATIVES.md`](docs/INITIATIVES.md):

- Foundation and inspectable vertical slice —
  `019f61e7-1ea1-7742-9acc-99d62f39b888`
- Publication and judge-readiness baseline —
  `019f61fc-c32e-7d92-9d2e-0bd9083d08e7`
- Hosted deployment and README follow-up —
  `019f6253-ddfc-7272-8077-e34dfb3aee84`
- Grounded live chat, resilience, and locked delivery (primary `/feedback`
  candidate) — `019f62b9-10b7-7d82-a463-e6eb1192141c`
- Day 1 feed/database and Day 2 Synthesizer —
  `019f62e8-6715-70e2-a92a-fe28254f7b71`
- Day 3/Day 4 Insight structured output —
  `019f6336-3690-7022-a8ef-c8c0947e240f`
- Bounded capture/provenance and documentation cleanup —
  `019f66b4-78b8-7943-a41d-91e836d28f00`
- Grounding guardrails and capture readiness —
  `019f6773-0e96-7363-9657-0e0531c3d594`

## [0.4.0] - 2026-07-15

This bounded minor release adds structured Insight generation and local
PostgreSQL/pgvector retrieval while keeping live-store population, real
PostgreSQL integration, hosted redeployment, and live release-analysis claims
explicitly out of scope.

### Added

- Implemented Day 3/4 `generate_insight()` with bounded untrusted evidence,
  router-owned structured Responses API calls, strict output validation, and
  derived citation/severity/model provenance.
- Implemented local Day 5 async pgvector retrieval for live `/search` and
  `/chat`, including router-owned query embeddings and cited `InsightRow`
  conversion.

### Changed

- Verified 95 tests at 100.00% backend coverage with Ruff and mypy passing.
- Recorded the additive Day 3/Day 4 Insight implementation session:
  `019f6336-3690-7022-a8ef-c8c0947e240f`.
- Durable live-store population and hosted verification remain pending.

### Remaining boundaries

- Insight generation and local pgvector retrieval are implemented and tested;
  durable Insight/embedding population, a real PostgreSQL integration run, and
  controlled Scout → Synthesizer → Insight → Briefing wiring remain incomplete.

## [0.3.1] - 2026-07-15

This corrective patch makes the v0.3.0 test and release path independent of
developer-only environment credentials.

### Fixed

- Injected a dummy client into the Synthesizer orchestration unit test and
  added deterministic sync-client factory coverage, so GitHub Actions does not
  attempt to construct an OpenAI client without `OPENAI_API_KEY`.
- Preserved the 100% backend coverage gate with 80 passing tests.

## [0.3.0] - 2026-07-15

This release adds bounded primary-source feed ingestion, the async
PostgreSQL/pgvector schema foundation, and the first routed Synthesizer stages
while preserving DRIFT’s fixture-first and evidence-grounded live-chat
boundaries.

### Added

- Day 1 Scout ingestion with feedparser normalization, canonical URL
  deduplication, bounded transport retries, malformed-feed handling, and
  structured source fetch logging.
- Async SQLAlchemy metadata/session wiring and an initial Alembic migration for
  `sources`, `raw_items`, and `insights`, including the pgvector extension and
  1536-dimensional insight embeddings.
- Day 2 Synthesizer stages: routed batch embeddings, deterministic cosine
  clustering, and narrow Tier.DEV structured severity classification with
  mocked provider coverage.

### Changed

- Synchronized the agent instructions and status-bearing documentation with
  the verified hosted state; Railway is now documented as bounded live chat
  over fixture evidence, with Vercel CORS enabled.

### Verification

- Scout smoke ingestion reached all eight configured GitHub Atom feeds and
  normalized 80 items without model calls or database writes.
- The expanded repository suite passes 79 tests at 100.00% backend line
  coverage; Ruff and mypy also pass.

### Remaining boundaries

- Day 1 now supplies feed normalization, persistence helpers, and the
  PostgreSQL/pgvector migration foundation; Day 2 now supplies routed
  embeddings, deterministic clustering, and Tier.DEV severity
  classification. Scheduled live persistence, vector persistence/retrieval,
  generated Insight output, and controlled end-to-end wiring remain future
  implementation slices.
- Hosted `DRIFT_MODE=live` remains bounded to grounded chat over fixture
  evidence; `/briefing` is not live release analysis.

## [0.2.0] - 2026-07-15

This release adds a bounded, evidence-grounded local live-chat path while
preserving the fixture-first release-analysis boundary. It does not enable live
feed ingestion, generated Insight records, embeddings, or pgvector retrieval.

### Added

- Bounded live-model resilience: queue timeout, concurrency bulkhead,
  per-attempt timeout, jittered transient retry, circuit breaker, and
  cancellation-safe conservative spend settlement.
- ADR-009 documenting model-call resilience and a single frozen dependency
  resolution path.
- Deterministic coverage for live-chat success, provider failure, budget
  exhaustion, model routing, and typed agent orchestration.
- `DRIFT_MODE=live` can now call the OpenAI Responses API for retrieve-first,
  cited chat over the fixture store, with a local spend reservation.
- Local `.env` loading for development without overriding deployed environment
  variables.
- ADR-008 documenting the limited live-chat boundary.
- `GET /` service metadata endpoint for hosted API discovery.
- Ordered OpenAPI groups for `system`, `briefing`, `search`, and `chat`.
- Vercel configuration rooted at `frontend/`, with the Railway fixture API as
  `NEXT_PUBLIC_API_URL`.
- Node.js 24.x runtime declarations for Vercel, CI, local frontend work, and
  the frontend container.

### Changed

- Docker now installs from the frozen `uv.lock` dependency set.
- Raised local, CI, release, and Codecov coverage enforcement to 100% for
  implemented code; explicit future-stage `NotImplementedError` boundaries are
  excluded only at the raise line.
- Public documentation now links to the verified Railway fixture API at
  `https://drift-api-prod.up.railway.app` and the deployed Vercel frontend at
  `https://dr1ftless.vercel.app`.
- The README uses the Codecov badge as the coverage signal and links releases
  to the GitHub releases page.
- Package, API, and frontend metadata now identify this release as `0.2.0`.
- The frontend lockfile overrides Next’s nested PostCSS to patched `8.5.14`;
  the production dependency audit reports zero vulnerabilities.

### Removed

- The duplicate broad runtime requirements file and the unused direct
  `tenacity` dependency; `uv.lock` is the single Python dependency resolution
  authority.

### Fixed

- Railway’s root URL returns DRIFT service metadata instead of a 404.
- Uvicorn container output is redirected to stdout so Railway does not label
  informational startup logs as errors.
- The frontend labels live mode as grounded chat over fixture evidence rather
  than live release analysis.

## [0.1.0] - 2026-07-14

Initial DRIFT repository baseline: a fixture-first release-intelligence slice
with explicit live-path architecture and publication-ready quality gates.

### Added

- FastAPI fixture API with `/health`, `/briefing`, `/search`, `/chat`, `/docs`,
  and generated `/openapi.json` surfaces.
- Pydantic contracts for `RawItem`, `Insight`, `BriefingItem`, `ChatRequest`,
  and `ChatResponse`, including citations, confidence, severity, model/audit
  labels, and bounded `what_to_check` actions.
- Typed agent boundaries for Scout, Synthesizer, Insight, and Briefing, with a
  provider/model-router boundary and local SpendGuard.
- Curated GPU/AI-infrastructure source configuration for PyTorch, TensorRT,
  Triton, vLLM, Transformers, CUTLASS, JAX, and NCCL.
- Next.js + React + TypeScript briefing view with local API wiring.
- PostgreSQL + pgvector target architecture, Docker Compose wiring, Railway
  backend configuration, and Vercel frontend deployment guidance.
- Python dependency metadata in `pyproject.toml` and `uv.lock`, plus runtime
  container requirements.
- GitHub Actions gates for Ruff, mypy, pytest/coverage, Codecov upload,
  frontend build, release quality, and documentation hygiene.
- Mermaid architecture source with light/dark SVG and PNG renders, plus
  repository-native DRIFT hero banners.
- Seven ADRs covering fixture-first execution, typed stages, provenance,
  budget control, persistence, CI, and deployment topology.
- Contribution, security, runbook, architecture, build-sequence, and timed
  three-minute demo-script documentation.

### Quality baseline

- 19 pytest tests pass on Python 3.14.
- Coverage is 81.25% with an enforced 81% floor.
- The engineering target is 99–100% line coverage for implemented behavior.
- Ruff, mypy, frontend production build, configuration parsing, SVG parsing,
  and documentation-link checks pass.

### Known boundaries

- Fixture records are deterministic examples, not live release analysis.
- `DRIFT_MODE=live` remains intentionally blocked until migrations, provider
  mocks, retrieval, provenance persistence, and a reproducible end-to-end run
  are complete.
- Codecov activation, public deployment, and the final YouTube URL remain
  publication steps after this baseline.

### Codex project initiatives

- Foundation and inspectable vertical slice:
  `019f61e7-1ea1-7742-9acc-99d62f39b888`.
- Publication and judge-readiness baseline:
  `019f61fc-c32e-7d92-9d2e-0bd9083d08e7`.
- Full scope and submission guidance: [`docs/INITIATIVES.md`](docs/INITIATIVES.md).

[Unreleased]: #unreleased
[0.7.0]: #070---2026-07-16
[0.6.1]: #061---2026-07-16
[0.6.0]: #060---2026-07-16
[0.5.1]: #051---2026-07-15
[0.5.0]: #050---2026-07-15
[0.4.0]: #040---2026-07-15
[0.3.1]: #031---2026-07-15
[0.3.0]: #030---2026-07-15
[0.2.0]: #020---2026-07-15
[0.1.0]: #010---2026-07-14

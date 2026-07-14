# Changelog

All notable changes to DRIFT are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) · Versioning:
[Semantic Versioning](https://semver.org/)

The `0.1.0` entry is the initial repository baseline published on GitHub as
the annotated `v0.1.0` tag.

## [Unreleased]

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
[0.2.0]: #020---2026-07-15
[0.1.0]: #010---2026-07-14

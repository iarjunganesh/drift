# DRIFT

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/brand/drift-banner-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="assets/brand/drift-banner-light.svg">
    <img width="900" src="assets/brand/drift-banner-light.svg"
         alt="DRIFT — Release intelligence for GPU and AI infrastructure. Cited, bounded, inspectable."/>
  </picture>
</p>

[![CI](https://github.com/iarjunganesh/drift/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/iarjunganesh/drift/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/pytest%20coverage-81.25%25%20%7C%20gate%2081%25-f2c94c?logo=pytest&logoColor=111827)](#production--quality)
[![Codecov](https://codecov.io/gh/iarjunganesh/drift/graph/badge.svg)](https://codecov.io/gh/iarjunganesh/drift)
[![Release](https://img.shields.io/badge/release-unreleased-6b7280?logo=github&logoColor=white)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Watch Video](https://img.shields.io/badge/%E2%96%B6_Watch-3--min_demo-FF0000?logo=youtube&logoColor=white)](#live--interactive-demo)

[![Python](https://img.shields.io/badge/Python-3.14-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.139-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![pgvector](https://img.shields.io/badge/pgvector-0.5.0-336791?logo=postgresql&logoColor=white)](https://github.com/pgvector/pgvector)
[![OpenAI](https://img.shields.io/badge/OpenAI-SDK-412991?logo=openai&logoColor=white)](https://platform.openai.com/)
[![Ruff](https://img.shields.io/badge/Ruff-lint%20%2B%20format-D7FF64?logo=ruff&logoColor=111827)](https://docs.astral.sh/ruff/)

[![Next.js](https://img.shields.io/badge/Next.js-16.2.10-000000?logo=nextdotjs&logoColor=white)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-19.2.7-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![Node.js](https://img.shields.io/badge/Node.js-22-339933?logo=nodedotjs&logoColor=white)](https://nodejs.org/)
[![Railway](https://img.shields.io/badge/Railway-backend-0B0D0E?logo=railway&logoColor=white)](https://railway.app/)
[![Vercel](https://img.shields.io/badge/Vercel-frontend-000000?logo=vercel&logoColor=white)](https://vercel.com/)

---

## What Is This?

DRIFT is release intelligence for GPU and AI-infrastructure teams. It turns
upstream release-note noise into a cited, engineer-ready answer:

> **What changed? Why does it matter to my workload? What should I check?**

The first vertical slice is fixture-first and deterministic. The target system
will watch primary release feeds, rank meaningful changes, explain workload
impact, and return a bounded next engineering check without presenting model
output as a deployment verdict.

Built for **OpenAI Build Week 2026 · Developer Tools**.

---

## The Problem

GPU and AI platforms depend on fast-moving projects such as PyTorch, TensorRT,
Triton, vLLM, Transformers, CUTLASS, JAX, and NCCL. A small upstream change can
alter an image, benchmark, CUDA assumption, or deployment template, but release
review is usually a stream of links and scattered human memory.

DRIFT keeps the useful middle layer visible: source evidence, a plain-language
summary, workload relevance, confidence, severity, and one concrete action to
check. It does not certify compatibility, replace release notes, or authorize
production changes.

---

## How It Works

1. **Scout** reads configured primary release feeds and normalizes source items.
2. **Synthesizer** will deduplicate, embed, cluster, and classify substantive
   changes.
3. **Insight** will produce a structured explanation with citations, confidence,
   severity, and a bounded `what_to_check` action.
4. **Briefing** ranks the useful changes and grounds search/chat in retrieved
   DRIFT evidence.
5. **FastAPI** exposes the briefing, search, chat, health, and generated OpenAPI
   contract.

The currently working path substitutes committed examples for the unfinished
live stages:

```text
backend/fixtures/insights.json → InsightStore → FastAPI → briefing/search/chat
```

Fixture records are explicitly labelled examples. They are never described as
fresh live release analysis.

---

## Architecture

<p align="center">
  <a href="assets/architecture/architecture-diagram-light.svg" target="_blank" rel="noopener noreferrer">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="assets/architecture/architecture-diagram-dark.svg">
      <source media="(prefers-color-scheme: light)" srcset="assets/architecture/architecture-diagram-light.svg">
      <img width="900" src="assets/architecture/architecture-diagram-light.svg"
           alt="DRIFT architecture — primary release feeds through Scout, Synthesizer, Insight, and Briefing into FastAPI"/>
    </picture>
  </a>
</p>

<sub>Click to enlarge: <a href="assets/architecture/architecture-diagram-light.svg">light SVG</a> / <a href="assets/architecture/architecture-diagram-dark.svg">dark SVG</a> · Downloadable <a href="assets/architecture/architecture-diagram-light.png">light PNG</a> / <a href="assets/architecture/architecture-diagram-dark.png">dark PNG</a> · Source: <a href="assets/architecture/architecture-diagram.mmd"><code>architecture-diagram.mmd</code></a></sub>

**In short:** the fixture path is complete and no-key; the feed, Postgres,
pgvector, embedding, and model stages are explicit implementation boundaries,
not hidden claims of production readiness.

> **Deep dive** → [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — runtime paths, stage
> ownership, provenance, retrieval, safety invariants, failure handling, and
> the Vercel/Railway deployment topology.

### Codex project initiatives

The initial baseline is tied to two project initiatives:

| Initiative | Session ID | Focus |
| --- | --- | --- |
| Foundation and inspectable vertical slice | `019f61e7-1ea1-7742-9acc-99d62f39b888` | Fixture API, typed contracts, agent boundaries, safety invariants, tests |
| Publication and judge-readiness baseline | `019f61fc-c32e-7d92-9d2e-0bd9083d08e7` | Documentation, architecture assets, CI/Codecov, deployment and submission surfaces |

See the full [project initiative record](docs/INITIATIVES.md).

### Architecture Decision Records

Seven decisions currently constrain the implementation. They are intentionally
short; the architecture document explains how they compose.

| ADR | Decision |
| --- | --- |
| [001](docs/adr/001-fixture-first-judge-path.md) | Fixture-first judge path with an honest live boundary |
| [002](docs/adr/002-typed-agents-no-framework.md) | Typed hand-rolled stages instead of a heavyweight agent framework |
| [003](docs/adr/003-citations-and-visible-uncertainty.md) | Citations, confidence, audit labels, and uncertainty are visible |
| [004](docs/adr/004-local-budget-guard.md) | Local spend guard around live iteration |
| [005](docs/adr/005-postgres-pgvector-live-store.md) | PostgreSQL + pgvector for the live store |
| [006](docs/adr/006-ci-quality-gates.md) | CI gates with an 81% floor and a 99–100% target |
| [007](docs/adr/007-vercel-railway-deployment.md) | Vercel frontend + Railway API/database deployment shape |

---

## Model Router & Safety Boundary

Provider calls belong behind [model_router.py](backend/core/model_router.py).
Agent code must not hard-code provider model names. The intended tiers are:

| Tier | Intended job | Status |
| --- | --- | --- |
| `dev` / Luna | Classification, clustering, and prompt iteration | Routed boundary prepared |
| `live` / Terra | Retrieve-first grounded chat | Target path |
| `final` / Sol | Three to five reviewed demo insights | Target path |

Every live insight must preserve:

- at least one canonical primary-source citation;
- confidence in `[0, 1]`;
- the exact model identifier or an explicit fixture audit label; and
- a concrete, bounded `what_to_check` action.

Release text is untrusted data. It can be summarized and reasoned over, but it
must never become model instructions or authorization to act on infrastructure.
`breaking` and `security` are review priorities, not automation triggers.

The local [SpendGuard](backend/core/budget.py) is a development safeguard;
provider-side limits remain required for a deployed service.

---

## Tech Stack

| Layer | Technology | Role |
| --- | --- | --- |
| **Backend** | [![FastAPI](https://img.shields.io/badge/FastAPI-0.139-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/) [![Python](https://img.shields.io/badge/Python-3.14-3776AB?logo=python&logoColor=white)](https://www.python.org/) | Typed HTTP API and explicit pipeline stages |
| **Contracts** | [![Pydantic](https://img.shields.io/badge/Pydantic-2.13-E92063?logo=pydantic&logoColor=white)](https://docs.pydantic.dev/) | Typed raw-item, insight, briefing, and chat contracts |
| **Agent Pattern** | [![asyncio](https://img.shields.io/badge/asyncio-typed%20stages-3776AB?logo=python&logoColor=white)](backend/agents/base.py) | Small lifecycle-wrapped functions; no orchestration framework |
| **Release Feeds** | [![feedparser](https://img.shields.io/badge/feedparser-Atom%20%2F%20RSS-3776AB?logo=python&logoColor=white)](https://feedparser.readthedocs.io/) [![PyYAML](https://img.shields.io/badge/PyYAML-sources-3776AB?logo=python&logoColor=white)](https://pyyaml.org/) | Configured primary-source feed definitions and parsing |
| **Live Store** | [![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/) [![pgvector](https://img.shields.io/badge/pgvector-0.5.0-336791?logo=postgresql&logoColor=white)](https://github.com/pgvector/pgvector) | Durable raw items, insights, and vector retrieval |
| **Model Boundary** | [![OpenAI](https://img.shields.io/badge/OpenAI-SDK-412991?logo=openai&logoColor=white)](https://platform.openai.com/) | Provider isolation, model tiers, and budget control |
| **Quality** | [![Ruff](https://img.shields.io/badge/Ruff-0.15.21-D7FF64?logo=ruff&logoColor=111827)](https://docs.astral.sh/ruff/) [![pytest](https://img.shields.io/badge/pytest-9.1-0A9EDC?logo=pytest&logoColor=white)](https://docs.pytest.org/) [![Codecov](https://img.shields.io/badge/Codecov-pytest-f01f7a?logo=codecov&logoColor=white)](https://codecov.io/) | Lint, types, tests, coverage evidence, and CI enforcement |
| **Frontend** | [![Next.js](https://img.shields.io/badge/Next.js-16.2.10-000000?logo=nextdotjs&logoColor=white)](https://nextjs.org/) [![React](https://img.shields.io/badge/React-19.2.7-61DAFB?logo=react&logoColor=black)](https://react.dev/) [![TypeScript](https://img.shields.io/badge/TypeScript-5.9-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/) | Operator-facing briefing view |
| **Hosting** | [![Railway](https://img.shields.io/badge/Backend-Railway-0B0D0E?logo=railway&logoColor=white)](https://railway.app/) [![Vercel](https://img.shields.io/badge/Frontend-Vercel-000000?logo=vercel&logoColor=white)](https://vercel.com/) | Railway API/database; Vercel Next.js frontend |
| **Observability** | [![structlog](https://img.shields.io/badge/structlog-JSON-4A90E2)](https://www.structlog.org/) | Structured logs and explicit request/stage boundaries |

Python dependencies are declared in [pyproject.toml](pyproject.toml), resolved
in [uv.lock](uv.lock), and mirrored for container deployment in
[backend/requirements.txt](backend/requirements.txt). JavaScript dependencies
are locked in [frontend/package-lock.json](frontend/package-lock.json).

---

## Live & Interactive Demo

| | |
| --- | --- |
| **Mode** | `fixture` — deterministic, no credentials, no network, no database |
| **API** | `http://127.0.0.1:8000` after the local start command |
| **Swagger** | [`/docs`](http://127.0.0.1:8000/docs) |
| **OpenAPI** | [`/openapi.json`](http://127.0.0.1:8000/openapi.json) |
| **Briefing** | [`/briefing`](http://127.0.0.1:8000/briefing) |
| **Frontend** | `http://localhost:3000` after `npm --prefix frontend run dev` |
| **Demo Video** | [`https://youtu.be/TBD`](https://youtu.be/TBD) *(≤ 3 min, record before submission)* |
| **Public demo** | Not deployed yet; GitHub + Codecov + Railway/Vercel setup is next |

The live feed → Postgres → embedding → model path is not yet claimed as
working. The fixture path is the reproducible demo for reviewers today.

---

## Screenshots & Evidence

The architecture assets are the current visual evidence and are available in
both SVG and PNG formats:

| Light | Dark |
| --- | --- |
| [![DRIFT architecture light](assets/architecture/architecture-diagram-light.png)](assets/architecture/architecture-diagram-light.svg) | [![DRIFT architecture dark](assets/architecture/architecture-diagram-dark.png)](assets/architecture/architecture-diagram-dark.svg) |

The Next.js briefing view is intentionally small while the live pipeline is
being built; it is verified by the production build gate rather than presented
as a completed hosted product.

---

## Quick Start

Requirements: Python 3.14, `uv`, and Node.js 22 for the frontend.

```powershell
# 1. Clone after the GitHub repository is published
git clone <DRIFT-GITHUB-URL>
cd drift

# 2. Configure the no-key fixture path
Copy-Item .env.example .env

# 3. Install locked Python dependencies
uv venv .venv
uv sync --group dev

# 4. Start the API
uv run uvicorn backend.main:app --reload
```

Open <http://127.0.0.1:8000/docs>, or try:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/briefing
Invoke-RestMethod http://127.0.0.1:8000/search?q=vllm
Invoke-RestMethod http://127.0.0.1:8000/chat `
  -Method Post -ContentType application/json `
  -Body '{"question":"What should I check for vLLM?"}'
```

Run the frontend in another terminal:

```powershell
npm --prefix frontend ci
npm --prefix frontend run dev
```

Set `NEXT_PUBLIC_API_URL` in `frontend/.env.local` if the API is not on
`http://localhost:8000`.

---

## Synthetic Fixture Data

The fixture path uses [`backend/fixtures/insights.json`](backend/fixtures/insights.json).
These records are committed examples for deterministic development and judging;
they are not current release analysis. Each record preserves the contract that
the live path must also satisfy:

| Field | Purpose |
| --- | --- |
| `citations` | Source URLs supporting the insight |
| `confidence` | Visible certainty in `[0, 1]` |
| `model_used` | Fixture audit label or exact live model identifier |
| `what_to_check` | Bounded engineering action |
| `severity` | Review priority, never an automation trigger |

---

## Project Structure

```text
drift/
├── backend/
│   ├── agents/          # Base, Scout, Synthesizer, Insight, and Briefing stages
│   ├── core/            # Settings, model router, fixture store, and SpendGuard
│   ├── fixtures/        # Deterministic citation-backed example insights
│   ├── models/           # Pydantic domain and API contracts
│   ├── main.py           # FastAPI app: health, briefing, search, chat
│   ├── sources.yaml      # Primary release-feed configuration
│   └── requirements.txt  # Runtime-only container requirements
├── frontend/             # Next.js + React + TypeScript briefing view
├── assets/
│   ├── architecture/     # Mermaid source plus themed SVG/PNG renders
│   └── brand/            # Repository-native DRIFT hero banners
├── tests/
│   ├── unit/              # Agent, budget, and configuration tests
│   └── integration/       # API and lifespan tests
├── docs/
│   ├── ARCHITECTURE.md    # Runtime and deployment deep dive
│   ├── INITIATIVES.md      # Codex project initiative/session records
│   ├── BUILD_SEQUENCE.md  # Implementation sequence and GitHub/Codecov setup
│   ├── RUNBOOK.md         # Fixture/live demo procedure
│   └── adr/               # Architecture Decision Records 001–007
├── submission/            # Developer Tools handoff, checklist, and demo script
├── Dockerfile             # Railway-compatible FastAPI image
├── docker-compose.yml     # Local API + PostgreSQL + frontend wiring
├── railway.json           # Railway build and health-check configuration
├── pyproject.toml         # Python project, Ruff, mypy, pytest, coverage
├── uv.lock                # Reproducible Python dependency resolution
└── .github/workflows/     # CI quality gate and tagged release workflow
```

---

## Production & Quality

```text
push → Ruff → mypy → pytest (≥81% coverage gate) → Codecov → frontend build → docs hygiene
```

The current local result is **19 tests passed and 81.25% coverage**. The
enforceable floor is **81%**, deliberately above 80%; the engineering target is
**99–100% line coverage** for implemented behavior, with branch-critical error
paths covered explicitly. The floor will ratchet upward as live stages land.

Run the gates locally:

```powershell
uv run ruff check backend tests
uv run mypy backend
uv run pytest tests --cov=backend --cov-report=term-missing --cov-fail-under=81
npm --prefix frontend ci
npm --prefix frontend run build
```

Pytest writes `coverage.xml`. CI uploads it with [codecov.yml](codecov.yml).
The repository-specific [Codecov report](https://codecov.io/gh/iarjunganesh/drift)
is ready to show the first uploaded run once the repository is activated in
Codecov.

### Load & Resilience

Load tests are not yet represented as complete. The next reliability slice is
to add bounded feed retries, provider timeout tests, Postgres failure behavior,
and a small HTTP smoke test before making production-readiness claims.

---

## GitHub + Codecov Setup

The remaining publication steps are documented in
[docs/BUILD_SEQUENCE.md](docs/BUILD_SEQUENCE.md#github-and-codecov-setup):

1. push the initial `main` baseline and verify the CI workflow;
2. activate `iarjunganesh/drift` in Codecov and confirm the `pytest` upload;
3. enable branch protection requiring the CI quality gate; and
4. only then deploy the fixture API to Railway and the frontend to Vercel.

---

## Future Roadmap

**Working now:** fixture API, typed contracts, model-router boundary,
architecture evidence, CI gates, Codecov upload configuration, and a local
Next.js briefing view.

**Next implementation slices:**

- implement Scout feed retrieval with bounded retries and source telemetry;
- add Alembic migrations and async PostgreSQL/pgvector persistence;
- implement embeddings, deduplication, clustering, and retrieval;
- implement structured Insight generation with mocked provider tests;
- raise coverage toward 99–100% as each stage becomes real;
- publish the repository, activate Codecov, and deploy fixture mode;
- capture reproducible live-path evidence before enabling model-backed claims.

Full decisions and sequencing live in [docs/adr/](docs/adr/),
[docs/BUILD_SEQUENCE.md](docs/BUILD_SEQUENCE.md),
[docs/INITIATIVES.md](docs/INITIATIVES.md), and [CHANGELOG.md](CHANGELOG.md).

---

## Disclaimer

Fixture records are synthetic examples and are not live release analysis. DRIFT
does not certify compatibility, replace upstream release notes, or authorize
changes to production infrastructure. Any live insight must remain cited,
confidence-labelled, model/audit-labelled, and paired with a bounded
`what_to_check` action.

> Built for the [OpenAI Build Week 2026](https://openai.com/) Developer Tools
> track. Human review remains required for source fidelity, prompt iteration,
> final examples, and breaking or security-labelled results.

See [LICENSE](LICENSE) for the MIT license.

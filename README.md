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
[![Codecov](https://codecov.io/gh/iarjunganesh/drift/graph/badge.svg)](https://codecov.io/gh/iarjunganesh/drift)
[![Release](https://img.shields.io/badge/release-latest-2ea44f?logo=github&logoColor=white)](https://github.com/iarjunganesh/drift/releases)
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
[![Node.js](https://img.shields.io/badge/Node.js-24-339933?logo=nodedotjs&logoColor=white)](https://nodejs.org/)
[![Railway](https://img.shields.io/badge/Railway-backend-0B0D0E?logo=railway&logoColor=white)](https://drift-api-prod.up.railway.app/docs)
[![Vercel](https://img.shields.io/badge/Vercel-frontend-000000?logo=vercel&logoColor=white)](https://dr1ftless.vercel.app)

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

**In short:** the fixture path is complete and no-key; a bounded local
model-backed chat path is available over its cited evidence. Scout ingestion,
Day 2 embedding/clustering/classification, and the database foundation exist;
feed scheduling, live-store integration, embedding persistence, and generated
Insight stages remain explicit implementation boundaries.

> **Deep dive** → [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — runtime paths, stage
> ownership, provenance, retrieval, safety invariants, failure handling, and
> the Vercel/Railway deployment topology.

### Codex project initiatives

The baseline, publication follow-up, release candidate, and documentation
follow-up are tied to five project initiatives. The grounded live-chat row is
the primary implementation session for this release candidate.

| Initiative | Session ID | Focus |
| --- | --- | --- |
| Foundation and inspectable vertical slice | `019f61e7-1ea1-7742-9acc-99d62f39b888` | Fixture API, typed contracts, agent boundaries, safety invariants, tests |
| Publication and judge-readiness baseline | `019f61fc-c32e-7d92-9d2e-0bd9083d08e7` | Documentation, architecture assets, CI/Codecov, deployment and submission surfaces |
| Hosted deployment and README follow-up | `019f6253-ddfc-7272-8077-e34dfb3aee84` | Railway/Vercel URLs, release badges, and public demo documentation |
| Day 1/Day 2 implementation follow-up | `019f62e8-6715-70e2-a92a-fe28254f7b71` | Scout feeds, async PostgreSQL/pgvector foundation, Tier.DEV embeddings/clustering/classification, session instructions, and status cleanup |
| Grounded live chat, resilience, and locked delivery | `019f62b9-10b7-7d82-a463-e6eb1192141c` | Primary `0.2.0` candidate work: local live chat, async safeguards, locked delivery, and full implemented-code coverage |

See the full [project initiative record](docs/INITIATIVES.md).

### How Codex and GPT-5.6 were used

Codex was used to build and audit the typed FastAPI stages, fixture contracts,
tests, deployment files, architecture records, and the bounded async
model-call path. The primary core-functionality session is
`019f62b9-10b7-7d82-a463-e6eb1192141c`; the Day 1/Day 2 implementation
follow-up session is `019f62e8-6715-70e2-a92a-fe28254f7b71`. The earlier
initiative records preserve the foundation, publication, and hosted-demo work.

GPT-5.6 is used only when an operator explicitly enables `DRIFT_MODE=live` and
provides an API key; the hosted Railway service was last verified in that mode
on 2026-07-15. The `live` tier receives at most three retrieved,
citation-bearing fixture insights as untrusted data and answers only from that
evidence. Fixture mode makes no provider call. This is not live release
analysis, and scheduled Scout persistence, embedding persistence, generated
Insight records, and pgvector retrieval remain explicit implementation
boundaries.

### Architecture Decision Records

Nine decisions currently constrain the implementation. They are intentionally
short; the architecture document explains how they compose.

| ADR | Decision |
| --- | --- |
| [001](docs/adr/001-fixture-first-judge-path.md) | Fixture-first judge path with an honest live boundary |
| [002](docs/adr/002-typed-agents-no-framework.md) | Typed hand-rolled stages instead of a heavyweight agent framework |
| [003](docs/adr/003-citations-and-visible-uncertainty.md) | Citations, confidence, audit labels, and uncertainty are visible |
| [004](docs/adr/004-local-budget-guard.md) | Local spend guard around live iteration |
| [005](docs/adr/005-postgres-pgvector-live-store.md) | PostgreSQL + pgvector for the live store |
| [006](docs/adr/006-ci-quality-gates.md) | CI gates with a 100% implemented-code floor |
| [007](docs/adr/007-vercel-railway-deployment.md) | Vercel frontend + Railway API/database deployment shape |
| [008](docs/adr/008-live-grounded-chat.md) | Live grounded chat over the cited fixture store |
| [009](docs/adr/009-bounded-model-resilience-and-locked-delivery.md) | Bounded model resilience and locked delivery |

---

## Model Router & Safety Boundary

Provider calls belong behind [model_router.py](backend/core/model_router.py).
Agent code must not hard-code provider model names. The intended tiers are:

| Tier | Intended job | Status |
| --- | --- | --- |
| `dev` / Luna | Classification, clustering, and prompt iteration | Embeddings, deterministic clustering, and narrow severity classification implemented and mocked |
| `live` / Terra | Retrieve-first grounded chat | Bounded local live path |
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

Live model requests are additionally bounded by a queue timeout and concurrency
bulkhead, a per-attempt timeout, transient-failure retries with jitter, and a
closed/open/half-open circuit breaker. A cancelled or uncertain provider attempt
is accounted for conservatively; it is never silently treated as free.

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

Python dependencies are declared in [pyproject.toml](pyproject.toml) and
resolved once in [uv.lock](uv.lock); local, CI, and container installs all use
that frozen lockfile. JavaScript dependencies are locked in
[frontend/package-lock.json](frontend/package-lock.json).

---

## Live & Interactive Demo

The Railway API and Vercel frontend are live. The Vercel project deploys from
`frontend/` using its checked-in build configuration. The hosted API was last
verified on 2026-07-15 in bounded `DRIFT_MODE=live`; live mode applies only to
grounded `/chat` over fixture evidence. The briefing remains fixture-backed.

| | |
| --- | --- |
| **Mode** | `live` — bounded grounded chat over cited fixture evidence |
| **Frontend** | [https://dr1ftless.vercel.app](https://dr1ftless.vercel.app) |
| **API** | [https://drift-api-prod.up.railway.app](https://drift-api-prod.up.railway.app) |
| **Swagger** | [`/docs`](https://drift-api-prod.up.railway.app/docs) |
| **OpenAPI** | [`/openapi.json`](https://drift-api-prod.up.railway.app/openapi.json) |
| **Briefing** | [`/briefing`](https://drift-api-prod.up.railway.app/briefing) |
| **Demo Video** | [`https://youtu.be/TBD`](https://youtu.be/TBD) *(≤ 3 min, record before submission)* |
| **Public demo** | Vercel frontend and Railway API are live; Vercel-to-Railway CORS was verified on 2026-07-15 |

The live feed → Postgres → embedding → model path is not yet claimed as
working. The fixture path is the reproducible demo for reviewers today.

The Swagger contract groups the backend into **System**, **Briefing**,
**Search**, and **Chat** sections so reviewers can navigate the API by job.

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

Requirements: Python 3.14, `uv`, and Node.js 24.x for the frontend.

```powershell
# 1. Clone after the GitHub repository is published
git clone <DRIFT-GITHUB-URL>
cd drift

# 2. Configure the no-key fixture path
Copy-Item .env.example .env

# 3. Install locked Python dependencies
uv venv .venv
uv sync --locked --group dev

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

For the durable PostgreSQL path, start the configured database and run
`make migrate` (or `uv run alembic upgrade head`) before connecting a live
store. The fixture path does not require a database.

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
├── frontend/             # Next.js + React + TypeScript briefing view
│   ├── .nvmrc            # Node.js 24.x local/runtime selection
│   └── vercel.json       # Vercel build settings and Railway API URL
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
│   └── adr/               # Architecture Decision Records 001–009
├── submission/            # Developer Tools handoff, checklist, and demo script
├── Dockerfile             # Railway image built from frozen uv.lock
├── docker-compose.yml     # Local API + PostgreSQL + frontend wiring
├── railway.json           # Railway build and health-check configuration
├── pyproject.toml         # Python project, Ruff, mypy, pytest, coverage
├── uv.lock                # Reproducible Python dependency resolution
└── .github/workflows/     # CI quality gate and tagged release workflow
```

---

## Production & Quality

```text
push → Ruff → mypy → pytest (100% coverage gate) → Codecov → frontend build → docs hygiene
```

The current local result is **80 tests passed and 100.00% coverage**. The
enforceable floor is **100% for implemented code**, including branch-critical
error paths. Explicit, documented live-pipeline stubs remain visible and are
excluded only at their `NotImplementedError` boundary.

Run the gates locally:

```powershell
uv run ruff check backend tests
uv run mypy backend
uv run pytest tests --cov=backend --cov-report=term-missing --cov-fail-under=100
npm --prefix frontend ci
npm --prefix frontend run build
```

Pytest writes `coverage.xml`. CI uploads it with [codecov.yml](codecov.yml) to
the repository-specific [Codecov report](https://codecov.io/gh/iarjunganesh/drift).

### Load & Resilience

The live-chat boundary has deterministic timeout, retry, capacity, circuit, and
provider-failure tests. Load testing, feed retry behavior, PostgreSQL failure
behavior, and a hosted HTTP smoke test remain future work before any
production-readiness claim.

---

## GitHub + Codecov Operations

GitHub `main`, the Railway API, and the Vercel frontend are published.
The remaining hosted verification operations are documented in
[docs/BUILD_SEQUENCE.md](docs/BUILD_SEQUENCE.md#github-and-codecov-setup):

1. confirm the `pytest` upload in Codecov; and
2. enable branch protection requiring the CI quality gate.

Hosted CORS and browser connectivity were verified on 2026-07-15. The
briefing is intentionally still fixture-backed; this is not live release
analysis.

---

## Future Roadmap

**Working now:** hosted bounded live-chat API over fixture evidence, deployed
Vercel frontend, typed contracts, model-router boundary, architecture evidence,
CI gates, Codecov upload configuration, and a local Next.js briefing view.

**Next implementation slices:**

- add scheduled Scout execution with durable raw-item telemetry;
- exercise the Alembic migration against a clean PostgreSQL instance and add
  async live-store integration coverage;
- persist Day 2 embeddings and connect clustering to live-store retrieval;
- implement structured Insight generation with mocked provider tests;
- maintain 100% implemented-code coverage as each live stage becomes real;
- run and record one hosted live `/chat` provider smoke test;
- capture reproducible live-release-analysis evidence before broadening the
  bounded model-backed chat claim.

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

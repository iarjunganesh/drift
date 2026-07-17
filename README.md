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
[![Watch Video](https://img.shields.io/badge/%E2%96%B6_Watch-3--min_demo-FF0000?logo=youtube&logoColor=white)](#try-drift-in-60-seconds)

<!-- Row 2 — AI & agent core -->
[![Agent Pattern](https://img.shields.io/badge/Agent_Pattern-asyncio_typed_stages-3776AB?logo=python&logoColor=white)](backend/agents/base.py)
[![GPT-5.6 Luna](https://img.shields.io/badge/GPT--5.6-Luna-412991?logo=openai&logoColor=white)](https://developers.openai.com/api/docs/models/gpt-5.6-luna)
[![GPT-5.6 Terra](https://img.shields.io/badge/GPT--5.6-Terra-412991?logo=openai&logoColor=white)](https://developers.openai.com/api/docs/models/gpt-5.6-terra)
[![GPT-5.6 Sol](https://img.shields.io/badge/GPT--5.6-Sol-412991?logo=openai&logoColor=white)](https://developers.openai.com/api/docs/models/gpt-5.6-sol)
[![Pydantic](https://img.shields.io/badge/Pydantic-2.13_contracts-E92063?logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![structlog](https://img.shields.io/badge/structlog-JSON_observability-4A90E2)](https://www.structlog.org/)

<!-- Row 3 — Frontend + live Vercel app -->
[![Next.js](https://img.shields.io/badge/Next.js-16.2.10-000000?logo=nextdotjs&logoColor=white)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-19.2.7-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.9-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Node.js](https://img.shields.io/badge/Node.js-24-339933?logo=nodedotjs&logoColor=white)](https://nodejs.org/)
[![Vercel Hobby](https://img.shields.io/badge/Vercel-Hobby-000000?logo=vercel&logoColor=white)](https://vercel.com)

<!-- Row 4 — Backend -->
[![Python](https://img.shields.io/badge/Python-3.14-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.139-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Ruff](https://img.shields.io/badge/Ruff-lint%20%2B%20format-D7FF64?logo=ruff&logoColor=111827)](https://docs.astral.sh/ruff/)
[![pytest](https://img.shields.io/badge/pytest-9.1-0A9EDC?logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![Railway Hobby](https://img.shields.io/badge/Railway-Hobby-0B0D0E?logo=railway&logoColor=white)](https://railway.com)

<!-- Row 5 — Live store -->
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![pgvector](https://img.shields.io/badge/pgvector-0.5.0-336791?logo=postgresql&logoColor=white)](https://github.com/pgvector/pgvector)

<!-- Row 6 — Hosting (live deployments) -->
[![Vercel live frontend](https://img.shields.io/badge/Vercel-live_frontend-000000?logo=vercel&logoColor=white)](https://dr1ftless.vercel.app)
[![Railway live API](https://img.shields.io/badge/Railway-live_API-0B0D0E?logo=railway&logoColor=white)](https://drift-api-prod.up.railway.app/docs)

---

## The Problem

GPU and AI platforms depend on fast-moving projects such as PyTorch, TensorRT,
Triton, vLLM, Transformers, CUTLASS, JAX, and NCCL. A small upstream change can
alter an image, benchmark, CUDA assumption, or deployment template — but release
review is usually a stream of links and scattered human memory. The signal that
matters is buried: *what changed, whether it touches your workload, and what to
check before rollout.*

## What DRIFT Does

DRIFT is release intelligence for GPU and AI-infrastructure teams. It turns
upstream release-note noise into a cited, engineer-ready answer:

> **What changed? Why does it matter to my workload? What should I check?**

Every answer keeps the useful middle layer visible: a frozen primary-source
span, a plain-language summary, workload relevance, confidence, severity, and
one bounded action to check. Direct facts stay separate from interpretation, and
nothing reaches a live endpoint until a human reviews it.

Built for **OpenAI Build Week 2026 · Developer Tools**.

## Try DRIFT in 60 Seconds

**Hosted — nothing to install.** The live briefing serves four human-reviewed
Insights from one real bounded capture (Transformers v5.14.1, vLLM v0.25.1,
NCCL v2.30.7-1, TensorRT 11.1); `/briefing`, `/search`, and `/chat` were verified
provider-backed on 2026-07-16.

| Surface | Link |
| --- | --- |
| **Frontend** — briefing with inspectable claim evidence | <https://dr1ftless.vercel.app> |
| **API docs** — `/health`, `/briefing`, `/search`, `/chat`, `/openapi.json` | <https://drift-api-prod.up.railway.app/docs> |
| **Grounded chat** — cited answer over reviewed evidence (verified provider-backed) | [`POST /chat` in the API docs](https://drift-api-prod.up.railway.app/docs) |
| **Demo video** — 3-min narrated walkthrough (Codex + GPT-5.6) | [▶ Watch on YouTube](https://youtu.be/TBD) *(recording before submission)* |

**Local — one command, no API key.** The deterministic fixture path brings up the
API, PostgreSQL, and the frontend — including the in-app **Ask DRIFT**
grounded-chat box — together:

```bash
git clone https://github.com/iarjunganesh/drift.git
cd drift
docker compose up
```

Open <http://localhost:3000> for the frontend and
<http://localhost:8000/docs> for the API. No OpenAI key is required, and every
record is clearly labelled example data. Full setup, cross-platform commands,
and the live capture path are in [Quick Start](#quick-start).

---

## How It Works

1. **Scout** reads configured primary release feeds and normalizes source items.
2. **Synthesizer** deduplicates, embeds, clusters, and classifies substantive
   changes.
3. **Insight** extracts typed direct facts, inferences, and recommended checks
   with exact source spans.
4. **Verifier** separately rejects unsupported or misclassified claims.
5. **Human review** promotes only verifier-passed drafts with recorded notes.
6. **Briefing** ranks reviewed changes and grounds search/chat in retrieved
   DRIFT evidence.
7. **FastAPI** exposes the briefing, search, chat, health, and generated OpenAPI
   contract.

The currently working path substitutes committed examples for the unfinished
live stages:

```text
backend/fixtures/source_evidence/*.txt + insights.json → InsightStore → FastAPI → briefing/search/chat
```

Fixture records are explicitly labelled examples, backed by checked-in
synthetic source text whose hashes and spans are verified in tests. They are
never described as fresh live release analysis.

---

## Architecture

<p align="center">
  <a href="assets/architecture/arch-light.svg" target="_blank" rel="noopener noreferrer">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="assets/architecture/arch-dark.svg">
      <source media="(prefers-color-scheme: light)" srcset="assets/architecture/arch-light.svg">
      <img width="960" src="assets/architecture/arch-light.svg"
           alt="DRIFT trust boundary — untrusted release feeds pass through machine claim extraction and a separate verifier into quarantined drafts; a human review gate is the only bridge to the trusted, published briefing an engineer sees."/>
    </picture>
  </a>
</p>

<p align="center"><sub><b>The trust boundary at a glance.</b> Everything left of the gate is untrusted machine output; a human reviewer is the only path to what an engineer sees. · <a href="assets/architecture/arch-light.svg">light SVG</a> / <a href="assets/architecture/arch-dark.svg">dark SVG</a></sub></p>

<details>
<summary><b>Detailed pipeline diagram</b> — the same six typed stages, as the maintainable Mermaid source of truth</summary>

<p align="center">
  <a href="assets/architecture/arch-pipeline-light.svg" target="_blank" rel="noopener noreferrer">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="assets/architecture/arch-pipeline-dark.svg">
      <source media="(prefers-color-scheme: light)" srcset="assets/architecture/arch-pipeline-light.svg">
      <img width="900" src="assets/architecture/arch-pipeline-light.svg"
           alt="DRIFT architecture — primary release feeds through Scout, Synthesizer, claim extraction, a separate verifier, a human review gate, and Briefing into FastAPI"/>
    </picture>
  </a>
</p>

<sub>Click to enlarge: <a href="assets/architecture/arch-pipeline-light.svg">light SVG</a> / <a href="assets/architecture/arch-pipeline-dark.svg">dark SVG</a> · Downloadable <a href="assets/architecture/arch-pipeline-light.png">light PNG</a> / <a href="assets/architecture/arch-pipeline-dark.png">dark PNG</a> · Source: <a href="assets/architecture/arch-pipeline.mmd"><code>arch-pipeline.mmd</code></a></sub>

</details>

**In short:** the fixture path is complete and no-key. The local live path now
persists source evidence, generates and separately verifies claim-grounded
drafts, embeds them, and retains two model-run audits. Drafts are quarantined;
only a human reviewer can publish them, and live read paths filter to reviewed,
verifier-passed records. On 2026-07-15, the prior hosted `v0.5.1` deployment
migrated Railway PostgreSQL and served one bounded, unreviewed vLLM capture
through `/briefing`. On 2026-07-16, Railway PostgreSQL was verified through
`0003_claim_evidence_review_gate` using its public TCP proxy. Later that day,
the hosted `v0.6.1` app passed `/health`, an empty fail-closed `/briefing`,
`/docs`, Vercel canonical-banner source, and Vercel-to-Railway CORS checks. It
then published four human-reviewed Insights (Transformers v5.14.1, vLLM v0.25.1,
NCCL v2.30.7-1, TensorRT 11.1) through the review gate, and hosted `/briefing`,
`/search`, and `/chat` were verified provider-backed — `/chat` returning a
grounded `gpt-5.6-terra` answer with primary-source citations. This is a small,
bounded reviewed set, not a broad live-release-analysis claim.

> **Deep dive** → [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — runtime paths, stage
> ownership, provenance, retrieval, safety invariants, failure handling, and
> the Vercel/Railway deployment topology.

### Codex project initiatives

The baseline, publication follow-up, bounded release milestones, and
documentation follow-up are tied to ten project initiatives. The grounded
live-chat row remains the primary v0.4.0 implementation session; v0.5.0 adds
the bounded local capture path.

| Initiative | Session ID | Focus |
| --- | --- | --- |
| Foundation and inspectable vertical slice | `019f61e7-1ea1-7742-9acc-99d62f39b888` | Fixture API, typed contracts, agent boundaries, safety invariants, tests |
| Publication and judge-readiness baseline | `019f61fc-c32e-7d92-9d2e-0bd9083d08e7` | Documentation, architecture assets, CI/Codecov, deployment and submission surfaces |
| Hosted deployment and README follow-up | `019f6253-ddfc-7272-8077-e34dfb3aee84` | Railway/Vercel URLs, release badges, and public demo documentation |
| Grounded live chat, resilience, and locked delivery | `019f62b9-10b7-7d82-a463-e6eb1192141c` | Primary `0.2.0` candidate work: local live chat, async safeguards, locked delivery, and full implemented-code coverage |
| Day 1/Day 2 implementation follow-up | `019f62e8-6715-70e2-a92a-fe28254f7b71` | Scout feeds, async PostgreSQL/pgvector foundation, Tier.DEV embeddings/clustering/classification, session instructions, and status cleanup |
| Day 3/Day 4 Insight structured output | `019f6336-3690-7022-a8ef-c8c0947e240f` | Standalone `generate_insight()` structured parsing, strict validation, citations, confidence, and model provenance |
| Bounded capture, provenance, and status cleanup | `019f66b4-78b8-7943-a41d-91e836d28f00` | One-shot persisted capture, all-call budget/retry controls, live briefing adapter, evidence UI, and documentation synchronization |
| Grounding guardrails and capture readiness | `019f6773-0e96-7363-9657-0e0531c3d594` | Claim spans/hashes, separate verifier, review-gated publication, cross-references, calibration cases, manual notebook, and all-source capture preflight |
| Submission audit and frontend evidence presentation | `019f6a46-e3eb-7de2-81b1-91515ae80043` | Handwritten-next-step audit, explicit briefing states, system-theme presentation, canonical API-served banners, and status synchronization |
| Reviewed-evidence release hardening and hosted verification | `019f6a78-6fa2-7121-9059-85ac8ceb9904` | Evidence-byte integrity, database-only review notes, display-only results artifact, `v0.7.0` hosted verification, and the `v0.8.0` grounded-chat / verifiable-fixture hosted release |

See the full [project initiative record](docs/INITIATIVES.md).

### How Codex and GPT-5.6 were used

Codex was used to build and audit the typed FastAPI stages, fixture contracts,
tests, deployment files, architecture records, and the bounded async
model-call path. The primary core-functionality session is
`019f62b9-10b7-7d82-a463-e6eb1192141c`; the Day 1/Day 2 implementation
follow-up session is `019f62e8-6715-70e2-a92a-fe28254f7b71`. The earlier
initiative records preserve the foundation, publication, and hosted-demo work;
the Day 3/Day 4 Insight implementation session is
`019f6336-3690-7022-a8ef-c8c0947e240f`; the grounding guardrail and
capture-readiness follow-up is `019f6773-0e96-7363-9657-0e0531c3d594`; and the
submission-audit/frontend-presentation follow-up is
`019f6a46-e3eb-7de2-81b1-91515ae80043`; the reviewed-evidence hardening,
hosted-verification, and `v0.8.0` release session is
`019f6a78-6fa2-7121-9059-85ac8ceb9904`.

GPT-5.6 is used only when an operator explicitly enables `DRIFT_MODE=live` and
provides an API key. The local capture job routes embeddings, classification,
claim drafting, and a separate verifier through the bounded provider boundary;
it records source hashes, exact evidence spans, upstream references, and both
model-run audits. The verifier is model-aided screening, not proof: a human
must review and publish the draft before it can appear in live endpoints.
Fixture mode makes no provider call. One paid, unreviewed vLLM capture is
recorded as historical scrubbed evidence from the previous hosted deployment;
it is not broad live-release analysis or evidence that the new gate is hosted.

### Architecture Decision Records

Ten decisions currently constrain the implementation. They are intentionally
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
| [010](docs/adr/010-claim-evidence-and-review-gate.md) | Claim-level evidence, separate verification, and review-first publication |

---

## Model Router & Safety Boundary

Provider calls belong behind [model_router.py](backend/core/model_router.py).
Agent code must not hard-code provider model names. The intended tiers are:

| Tier | Intended job | Status |
| --- | --- | --- |
| `dev` / Luna | Classification, clustering, and prompt iteration | Produced the four reviewed Insights published 2026-07-16; run only with an explicit live key |
| `live` / Terra | Retrieve-first grounded chat | Serves hosted grounded chat over reviewed pgvector rows; verified provider-backed 2026-07-16 |
| `final` / Sol | Three to five reviewed demo insights | Reserved; the 2026-07-16 demo set was captured at the `dev`/Luna tier to bound cost |

Every live insight must preserve:

- one or more typed claims with frozen exact primary-source excerpts, offsets,
  and source hashes;
- direct facts distinct from inferences and recommended checks;
- confidence in `[0, 1]`;
- the exact model identifier or an explicit fixture audit label; and
- a concrete, bounded `what_to_check` action.

Release text is untrusted data. It can be summarized and reasoned over, but it
must never become model instructions or authorization to act on infrastructure.
`breaking` and `security` are review priorities, not automation triggers.
Upstream release type is separate from potential operator risk; neither is a
compatibility verdict.

The local [SpendGuard](backend/core/budget.py) is a development safeguard;
provider-side limits remain required for a deployed service.

Live model requests are additionally bounded by a retry envelope, local spend
reservation, configured client timeout, and a closed/open/half-open circuit
breaker. Interactive chat also has a queue timeout and concurrency bulkhead. A
cancelled, failed, or usage-unknown provider attempt is accounted for
conservatively; it is never silently treated as free.

---

## Tech Stack

| Layer | Technology | Role |
| --- | --- | --- |
| **Backend** | [![Python](https://img.shields.io/badge/Python-3.14-3776AB?logo=python&logoColor=white)](https://www.python.org/) [![FastAPI](https://img.shields.io/badge/FastAPI-0.139-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/) | Typed HTTP API and explicit pipeline stages |
| **Contracts** | [![Pydantic](https://img.shields.io/badge/Pydantic-2.13-E92063?logo=pydantic&logoColor=white)](https://docs.pydantic.dev/) | Typed raw-item, insight, briefing, and chat contracts |
| **Agent Pattern** | [![asyncio](https://img.shields.io/badge/asyncio-typed%20stages-3776AB?logo=python&logoColor=white)](backend/agents/base.py) | Small lifecycle-wrapped functions; no orchestration framework |
| **Release Feeds** | [![feedparser](https://img.shields.io/badge/feedparser-Atom%20%2F%20RSS-3776AB?logo=python&logoColor=white)](https://feedparser.readthedocs.io/) [![PyYAML](https://img.shields.io/badge/PyYAML-sources-3776AB?logo=python&logoColor=white)](https://pyyaml.org/) | Configured primary-source feed definitions and parsing |
| **Live Store** | [![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/) [![pgvector](https://img.shields.io/badge/pgvector-0.5.0-336791?logo=postgresql&logoColor=white)](https://github.com/pgvector/pgvector) | Durable raw items, insights, and vector retrieval |
| **Model Boundary** | [![GPT-5.6](https://img.shields.io/badge/OpenAI-GPT--5.6_tiers-412991?logo=openai&logoColor=white)](https://developers.openai.com/api/docs/models) | Provider isolation, GPT-5.6 Luna/Terra/Sol tiers, and budget control |
| **Quality** | [![Codecov](https://img.shields.io/badge/Codecov-pytest-f01f7a?logo=codecov&logoColor=white)](https://codecov.io/) [![pytest](https://img.shields.io/badge/pytest-9.1-0A9EDC?logo=pytest&logoColor=white)](https://docs.pytest.org/) [![Ruff](https://img.shields.io/badge/Ruff-0.15.21-D7FF64?logo=ruff&logoColor=111827)](https://docs.astral.sh/ruff/) | Lint, types, tests, coverage evidence, and CI enforcement |
| **Frontend** | [![Next.js](https://img.shields.io/badge/Next.js-16.2.10-000000?logo=nextdotjs&logoColor=white)](https://nextjs.org/) [![React](https://img.shields.io/badge/React-19.2.7-61DAFB?logo=react&logoColor=black)](https://react.dev/) [![TypeScript](https://img.shields.io/badge/TypeScript-5.9-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/) [![Node.js](https://img.shields.io/badge/Node.js-24-339933?logo=nodedotjs&logoColor=white)](https://nodejs.org/) | Operator-facing briefing view |
| **Hosting** | [![Railway](https://img.shields.io/badge/Backend-Railway-0B0D0E?logo=railway&logoColor=white)](https://railway.app/) [![Vercel](https://img.shields.io/badge/Frontend-Vercel-000000?logo=vercel&logoColor=white)](https://vercel.com/) | Railway API/database; Vercel Next.js frontend |
| **Observability** | [![structlog](https://img.shields.io/badge/structlog-JSON-4A90E2)](https://www.structlog.org/) | Structured logs and explicit request/stage boundaries |

Python dependencies are declared in [pyproject.toml](pyproject.toml) and
resolved once in [uv.lock](uv.lock); local, CI, and container installs all use
that frozen lockfile. JavaScript dependencies are locked in
[frontend/package-lock.json](frontend/package-lock.json).

---

## Deployment status

Both tiers are live and `v0.8.0` was verified on 2026-07-17 — the live links live up top
in [Try DRIFT in 60 Seconds](#try-drift-in-60-seconds):

| Surface | Status |
| --- | --- |
| **Current hosted release** | `v0.8.0` `live` — `/health` reports `0.8.0`, `/docs` returns `200`, the public Vercel page renders Ask DRIFT, and Vercel-origin CORS allows `GET, POST` |
| **Prior hosted release** | `v0.7.0` `live` — `/briefing` (four reviewed Insights, review notes redacted), `/openapi.json`, and the deployed Vercel bundle's `top_n=10` request were verified |
| **Grounded retrieval** | `/briefing`, `/search`, and `/chat` verified provider-backed from an eight-source capture — six verifier-passed drafts, four published after human review |
| **Database schema** | Railway PostgreSQL at `0003_claim_evidence_review_gate`, verified through its public TCP proxy |
| **Branding** | Swagger banner frame and canonical API-served banner pair follow the same system light/dark preference |
| **Historical** | `v0.5.1` served one unreviewed vLLM Insight through `/briefing` on 2026-07-15 — retained as pre-gate evidence only |

This is a small, bounded reviewed set, not broad live-release analysis. The
Swagger contract groups the backend into **System**, **Briefing**, **Search**,
and **Chat** sections so reviewers can navigate the API by job.

---

## Screenshots & Evidence

These are live-state captures of the hosted app after four human-reviewed
Insights were published — not mockups. Click any image to open it full size.

| Briefing — four reviewed Insights | Inspecting frozen claim evidence |
| --- | --- |
| [![DRIFT briefing showing four reviewed Insights](assets/screenshots/03-briefing.png)](assets/screenshots/03-briefing.png) | [![DRIFT briefing expanded to show each claim's primary-source excerpt](assets/screenshots/04-briefing-claim-evidence.png)](assets/screenshots/04-briefing-claim-evidence.png) |

The Next.js briefing view exposes each record's status label, confidence,
model/audit label, rationale, bounded action, source links, and—when present—
claim-type evidence. On 2026-07-16, the hosted UI was verified against the
review-gated API; reviewed evidence has since been published, so `/briefing`
now serves four reviewed Insights instead of the intentional empty state.
`v0.7.0` deployed the review-note redaction and ten-item briefing request;
Railway, CORS, public-contract, and Vercel-bundle checks are recorded in the
changelog. `v0.8.0` deployed the grounded Ask DRIFT UI and tag-pinned synthetic
fixture evidence; Railway health/docs, the public UI, and CORS were verified.
Neither rollout re-ran paid provider chat.

The branded Swagger contract and the themed architecture assets are also
available as visual evidence:

| API documentation | Architecture (light / dark) |
| --- | --- |
| [![DRIFT branded Swagger API documentation](assets/screenshots/02-api-docs.png)](assets/screenshots/02-api-docs.png) | [![DRIFT architecture light](assets/architecture/arch-pipeline-light.png)](assets/architecture/arch-pipeline-light.svg)<br/>[![DRIFT architecture dark](assets/architecture/arch-pipeline-dark.png)](assets/architecture/arch-pipeline-dark.svg) |

The scrubbed hosted capture evidence is stored separately in
[`assets/evidence/`](assets/evidence/), including the verified unreviewed vLLM
briefing response and its explicit operational limitations. After a human
publishes a new notebook capture, its archive cell writes a new dated reviewed
record and SHA-256 manifest there without including review notes or secrets.

---

## Quick Start

### One command (recommended)

The fastest judge path brings up the API, PostgreSQL, and the frontend together
in fixture mode — no OpenAI key, identical on macOS, Linux, and Windows:

```bash
git clone https://github.com/iarjunganesh/drift.git
cd drift
docker compose up
```

Open <http://localhost:3000> for the frontend and <http://localhost:8000/docs>
for the API. Every record is labelled example data.

### Manual setup

Requirements: Python 3.14, `uv`, and Node.js 24.x for the frontend. Every
command below is shown for both shells; run whichever matches your platform.

#### bash — macOS / Linux

```bash
# 1. Clone the public repository
git clone https://github.com/iarjunganesh/drift.git
cd drift

# 2. Configure the no-key fixture path
cp .env.example .env

# 3. Install locked Python dependencies
uv venv .venv
uv sync --locked --group dev

# 4. Start the API
uv run uvicorn backend.main:app --reload
```

#### PowerShell — Windows

```powershell
# 1. Clone the public repository
git clone https://github.com/iarjunganesh/drift.git
cd drift

# 2. Configure the no-key fixture path
Copy-Item .env.example .env

# 3. Install locked Python dependencies
uv venv .venv
uv sync --locked --group dev

# 4. Start the API
uv run uvicorn backend.main:app --reload
```

Open <http://127.0.0.1:8000/docs>, or try the endpoints:

#### bash / curl

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/briefing
curl "http://127.0.0.1:8000/search?q=vllm"
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"What should I check for vLLM?"}'
```

#### PowerShell

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/briefing
Invoke-RestMethod http://127.0.0.1:8000/search?q=vllm
Invoke-RestMethod http://127.0.0.1:8000/chat `
  -Method Post -ContentType application/json `
  -Body '{"question":"What should I check for vLLM?"}'
```

Run the frontend in another terminal (same command on every platform). This is
also where the in-app **Ask DRIFT** box calls `/chat` for a grounded, cited
answer:

```bash
npm --prefix frontend ci
npm --prefix frontend run dev
```

Set `NEXT_PUBLIC_API_URL` in `frontend/.env.local` if the API is not on
`http://localhost:8000`.

For the durable PostgreSQL path, start the configured database and run
`make migrate` (or `uv run alembic upgrade head`) before connecting a live
store. The fixture path does not require a database.

For a judge-ready all-source demonstration, use the **DRIFT Manual Run** in
[`notebooks/drift_manual_run.ipynb`](notebooks/drift_manual_run.ipynb). It makes
the proof chain visible—source roster, spend-gated capture, frozen evidence,
human review, and immutable archive—while starting with one item per configured
source (at most eight). It creates drafts only and has a separate
empty-by-default human publication cell. It needs local
PostgreSQL or an operator-provided public/tunneled database URL; Railway's
private `postgres.railway.internal` hostname cannot be resolved from a local
notebook. When Railway provides a public TCP proxy, retain its complete private
`DATABASE_URL` and set `DRIFT_DATABASE_PUBLIC_HOST`/
`DRIFT_DATABASE_PUBLIC_PORT`; DRIFT replaces only the host and port locally.
Launch it with
`uv run --with jupyterlab jupyter lab notebooks/drift_manual_run.ipynb`.

The underlying capture command is also draft-only. Enable live mode, provide
an API key, and select a deliberately small source set. Start with `dev` for
prompt iteration and use `final` only for selected, already-reviewed sources:

```bash
# bash — macOS / Linux
export DRIFT_MODE=live
uv run python -m backend.pipeline --source vllm --source tensorrt --source pytorch --tier dev
```

```powershell
# PowerShell — Windows
$env:DRIFT_MODE='live'
uv run python -m backend.pipeline --source vllm --source tensorrt --source pytorch --tier dev
```

This command makes paid provider calls and writes quarantined draft rows. It is
not a scheduled feed service and does not publish or verify the hosted deployment.

---

## Synthetic Fixture Data

The fixture path uses [`backend/fixtures/insights.json`](backend/fixtures/insights.json).
These records are committed examples for deterministic development and judging;
they are not current release analysis. Each record carries typed `claims` with
frozen example excerpts, offsets, and source hashes, so the **Inspect claim
evidence** panel renders in no-key fixture mode exactly as it does for a reviewed
live capture. Each record preserves the contract that the live path must also
satisfy:

| Field | Purpose |
| --- | --- |
| `citations` | Source URLs supporting the insight |
| `claims` | Typed `direct_fact` / `inference` / `recommended_check` statements, each with a frozen example evidence span |
| `confidence` | Visible certainty in `[0, 1]` |
| `model_used` | Fixture audit label or exact live model identifier |
| `what_to_check` | Bounded engineering action |
| `severity` | Review priority, never an automation trigger |

---

## Project Structure

```text
drift/
├── backend/
│   ├── agents/               # base, scout, synthesizer, insight, briefing stages
│   ├── core/                 # config, model_router, store, live_store, budget, resilience
│   ├── models/schema.py      # Pydantic domain, claim-evidence, and API contracts
│   ├── fixtures/insights.json # deterministic example insights with claim evidence
│   ├── main.py               # FastAPI app: health, briefing, search, chat, /brand
│   ├── pipeline.py           # bounded one-shot live capture CLI (draft-only)
│   ├── review.py             # explicit human publication gate
│   ├── evidence_archive.py   # reviewed-evidence archive + SHA-256 manifest writer
│   └── sources.yaml          # primary release-feed configuration
├── frontend/                 # Next.js + React + TypeScript briefing view
│   ├── app/                  # page.tsx, layout.tsx, AskDrift.tsx (grounded chat box)
│   ├── .nvmrc                # Node.js 24.x local/runtime selection
│   └── vercel.json           # Vercel build settings and Railway API URL
├── assets/
│   ├── architecture/         # arch-* presentation (build_arch.py) + arch-pipeline-* Mermaid
│   ├── brand/                # DRIFT brand banners (build_banner.py); API-served
│   ├── evidence/             # scrubbed hosted-capture records + SHA-256 manifests
│   └── screenshots/          # live-state UI captures used in the README
├── tests/
│   ├── unit/                 # agent, budget, resilience, and configuration tests
│   └── integration/          # API, lifespan, and evidence-boundary tests
├── docs/
│   ├── ARCHITECTURE.md       # runtime and deployment deep dive
│   ├── INITIATIVES.md        # Codex project initiative/session records
│   ├── BUILD_SEQUENCE.md     # implementation sequence and GitHub/Codecov setup
│   ├── RUNBOOK.md · CODEX_PROMPTS.md  # demo procedure and prompt records
│   └── adr/                  # Architecture Decision Records 001–010
├── notebooks/                # local bounded capture/review workflow + results record
├── scripts/                  # check_openai_spend.py (read-only spend reconciliation)
├── migrations/               # Alembic env + versions (schema and provenance revisions)
├── submission/               # Developer Tools handoff, checklist, Devpost, demo script
├── Dockerfile · docker-compose.yml   # Railway image + local API/PostgreSQL/frontend
├── alembic.ini · Makefile · railway.json · codecov.yml  # tooling and deploy config
├── pyproject.toml · uv.lock  # Python project + reproducible dependency lock
├── .gitattributes            # pins evidence JSON to LF for byte-exact manifests
└── .github/workflows/        # CI quality gate and tagged release workflow
```

---

## Production & Quality

```text
push → Ruff → mypy → pytest (100% coverage gate) → Codecov → frontend build → docs hygiene
```

The current local result is **150 tests passed and 100.00% backend coverage**.
The
enforceable floor is **100% for implemented code**, including branch-critical
error paths. Explicit, documented live-pipeline boundaries remain visible while
the fixture and standalone Insight stages are covered with tests.

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

The live-chat boundary and synchronous capture calls have deterministic budget,
retry, circuit, and provider-failure coverage. The initial reviewed PostgreSQL
capture and provider-backed hosted `/search`/`/chat` smoke tests were completed
on 2026-07-16; a larger reviewed capture and load testing remain future work
before any production-readiness claim.

---

## GitHub + Codecov Operations

GitHub `main`, the Railway API, and the Vercel frontend are published. The two
repository-operations steps documented in
[docs/BUILD_SEQUENCE.md](docs/BUILD_SEQUENCE.md#github-and-codecov-setup) are now
complete:

1. the `pytest` upload is confirmed on Codecov — the repository and `flag=pytest`
   coverage badges both resolve to 100%; and
2. `main` branch protection is enabled, requiring the five CI quality-gate checks
   (Ruff lint, Mypy type check, Tests and coverage, Frontend build, Documentation
   hygiene) to pass, with strict up-to-date merges.

The earlier populated `v0.5.1` `/briefing` response was verified on 2026-07-15.
On 2026-07-16, hosted `v0.6.1` health, `/briefing` (four reviewed Insights),
`/docs`, Vercel canonical-banner source, CORS, and Railway PostgreSQL migration
`0003` were verified, and hosted provider-backed `/search`/`/chat` were
smoke-tested. The API-docs banner frame follows the selected system theme.

---

## Future Roadmap

**Working locally:** a bounded one-shot capture path from primary release feed
to frozen claim evidence, separate verification, pgvector embedding, two
model-run audit rows, and a human publication gate before live
briefing/search/chat retrieval; the fixture demo, evidence UI, typed contracts,
model-router boundary, architecture evidence, CI gates, and deployed Vercel
frontend.

**Next implementation slices:**

- expand beyond the initial reviewed capture (the first eight-source run
  produced six verifier-passed drafts and four reviewed Insights on 2026-07-16);
- exercise the Alembic migration and capture path against a clean PostgreSQL
  instance, then add a real integration run to delivery verification;
- add scheduled Scout execution only after the reviewed capture path is proven;
- maintain 100% implemented-code coverage as each live stage becomes real;
- schedule a repeatable reviewed-capture cadence (the first reviewed
  database-backed capture and its hosted search/chat smoke tests are complete);
- record and submit the public narrated demo.

Full decisions and sequencing live in [docs/adr/](docs/adr/),
[docs/BUILD_SEQUENCE.md](docs/BUILD_SEQUENCE.md),
[docs/INITIATIVES.md](docs/INITIATIVES.md), and [CHANGELOG.md](CHANGELOG.md).

---

## Trust Model

Release notes are **untrusted input**, and DRIFT treats them that way. That
constraint is the product: it is what makes every answer inspectable instead of
a black-box verdict.

- **Frozen source span.** Every factual claim carries an exact primary-source
  excerpt with character offsets and a source SHA-256 hash, so reasoning is
  always traceable back to what the release actually said.
- **Separate verifier pass.** A second, independently routed model call rejects
  unsupported or misclassified claims — model-aided screening, not proof.
- **Human review gate.** Verifier-passed drafts stay private until a person
  reviews the evidence and records notes; only then can a claim reach
  `/briefing`, `/search`, or `/chat`.
- **Facts kept separate from interpretation.** Direct facts, inferences, and
  recommended checks are labelled distinctly, and confidence plus the
  model/audit label are always visible.

Because of that boundary, DRIFT deliberately does **not** certify compatibility,
replace upstream release notes, or authorize changes to production
infrastructure. Fixture records are synthetic, clearly labelled examples and are
never presented as live release analysis. `breaking` and `security` are review
priorities, not automation triggers.

> Built for the [OpenAI Build Week 2026](https://openai.com/) Developer Tools
> track. Human review remains required for source fidelity, prompt iteration,
> final examples, and breaking or security-labelled results.

See [LICENSE](LICENSE) for the MIT license.

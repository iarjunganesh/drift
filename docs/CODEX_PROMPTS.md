# Codex / GPT-5.6 Terra build prompts

Ordered for a two-day push. Feed these one at a time to Codex (Terra tier).
Each prompt is self-contained — paste as-is into a fresh Codex session, or
chain them in one session if context allows.

These historical prompts are self-contained. They describe patterns for DRIFT's
typed pipeline, structured logging, coverage gate, and provenance manifest;
do not treat any legacy reference-repository paths or media-stack examples in
later prompts as DRIFT dependencies.

> Execution status (2026-07-15): the Day 1 Scout/database, Day 2 Synthesizer,
> Day 3/4 structured Insight, Day 5 pgvector retrieval, and bounded one-shot
> capture/provenance path are implemented locally. The prompts remain an
> historical build specification; current completion status is maintained in
> `docs/BUILD_SEQUENCE.md`. ADR-010 supersedes the older Insight contract with
> claim spans, separate verification, and review-first publication—do not use
> these historical prompts to remove those guards. Railway PostgreSQL has been
> migrated and one unreviewed vLLM capture was served through the prior hosted
> `/briefing`; its `0003` schema and hosted `v0.6.1` empty briefing were
> verified on 2026-07-16; four human-reviewed Insights were then published and
> hosted `/briefing`, `/search`, and `/chat` verified provider-backed.

---

## Day 1 — get the pipeline actually running

### Prompt 1 — Base agent pattern + Scout

```
Working in C:\ws\drift. Read backend/agents/base.py if it exists (it may not
yet — create it). I want a hand-rolled async agent base class, no external
agent framework: an abstract BaseAgent with an async run(self, input_data)
method that subclasses implement, and a __call__ wrapper that logs agent.start
/ agent.complete / agent.error via structlog around the call. Add structlog to
pyproject.toml if missing, then refresh uv.lock.

Then implement backend/agents/scout.py fully. Requirements:
- fetch_source() uses feedparser against a source's feed_url from
  backend/sources.yaml
- store_raw_items() persists fetched items via the DB session (models will
  be wired in a later step — for now assume an async SQLAlchemy session is
  passed in or accessible via backend/models/schema.py's session factory)
- run_scout() iterates all sources in sources.yaml, calling fetch_source()
  with bounded retry/backoff through backend/core/resilience.py. Keep timeout,
  cancellation, and failure classification explicit; do not add a second retry
  framework.
- Every fetch logs source name, item count, and duration via structlog,
  following the BaseAgent pattern above.

Keep it scoped to Scout only — do not touch synthesizer.py, insight.py, or
briefing.py in this pass.
```

### Prompt 2 — DB schema wiring

```
Working in C:\ws\drift. Verify and extend the SQLAlchemy Base/engine/session
wiring in backend/models/schema.py as needed. Implement it fully:
- Async SQLAlchemy 2.0 style (AsyncEngine, async_sessionmaker) reading
  DATABASE_URL from backend/core/config.py
- Keep the existing model field definitions (including the insights table's
  why_it_matters, model_used, and source_citations fields — these already
  exist as placeholders, do not rename them) but make sure they're on
  properly declared SQLAlchemy ORM classes with pgvector's Vector column
  type for the insights embedding column (add pgvector to
  pyproject.toml if missing, then refresh uv.lock)
- Add a get_session() async context manager / dependency for FastAPI to use
- Add an Alembic migration setup (alembic.ini + migrations/ dir) with one
  initial migration that creates all tables, including the pgvector
  extension (CREATE EXTENSION IF NOT EXISTS vector)

Use an async session-per-request lifecycle adapted to DRIFT's PostgreSQL and
pgvector storage boundary.
```

### Prompt 3 — Synthesizer + Insight agents

```
Working in C:\ws\drift. Using the BaseAgent pattern from
backend/agents/base.py (built in a previous step) and the now-wired DB
session from backend/models/schema.py, implement:

1. backend/agents/synthesizer.py — implement or verify the Day 2
   `embed_items()`, clustering, and classification stages. The current
   repository has the routed implementation; preserve its explicit provider
   boundary and mocked-test shape. The original requirements were:
   - embed_items(): call OpenAI's embeddings API (text-embedding-3-small —
     already set as EMBEDDING_MODEL in backend/core/model_router.py) on raw
     item text, store the vector on the item/insight row.
   - The GPT-5.6 clustering call: run on Tier.DEV (Luna) via
     get_model(Tier.DEV) from backend/core/model_router.py, per the existing
     comment "Run on Tier.DEV (Luna) while iterating." Cluster embedded
     items into candidate insight groups.

2. backend/agents/insight.py — implement run_insight_batch() and replace the
   original `NotImplementedError` function boundary. Build the user prompt from
   cluster contents, call get_model(tier) with INSIGHT_SYSTEM_PROMPT (already
   defined in the file), parse structured output into an Insight object.
   Populate source_citations from the cluster's item URLs and model_used
   from the resolved model name returned by get_model() — this is the audit
   trail. Retain model name, provider, and latency per call, but keep DRIFT's
   provenance focused on model_used, source_citations, and latency rather than
   a media-oriented multi-artifact manifest.

Wrap both agents' run() methods with the BaseAgent __call__ structlog
lifecycle logging already established for Scout.
```

### Prompt 4 — Briefing agent + FastAPI wiring

```
Working in C:\ws\drift. Implement backend/agents/briefing.py (currently a
stub) — it should take a batch of Insight objects and produce a
digestible briefing (grouped by source/library, ranked by confidence/
recency). Use BaseAgent as the other agents do.

Then wire backend/main.py's three endpoints against the agent modules in
backend/agents/:
- GET /search?q=... — semantic search over accumulated insights using
  pgvector cosine similarity against the query's embedding
- POST /chat — chat-over-knowledge using Tier.LIVE (get_model(Tier.LIVE)),
  retrieving relevant insights via the same pgvector search and grounding
  the response in them
- GET /health — simple liveness check (DB connectivity ping is enough)

Add a background-task or simple script entrypoint that runs
Scout → Synthesizer → Insight → Briefing end to end against
backend/sources.yaml, so `python -m backend.main` or a documented command
produces at least one real briefing from real fetched data. This is the
critical path — after this prompt, the pipeline must actually run,
not just import cleanly.
```

---

## Day 2 — harden, package for judges, finish docs

### Prompt 5 — Tests + CI

```
Working in C:\ws\drift. Add a pytest test suite under tests/unit and
tests/integration. At minimum:
- Unit tests for scout.py (mock feedparser/HTTP), synthesizer.py (mock
  OpenAI embeddings + chat calls), insight.py (mock get_model output,
  assert model_used and source_citations are populated correctly),
  briefing.py (grouping/ranking logic)
- One integration test hitting /health and /search against a test DB
  (use an in-memory or throwaway Postgres/pgvector — sqlite won't support
  pgvector, so either spin up a test Postgres via testcontainers or mark
  these tests to skip if no DATABASE_URL is set)
- Add pytest-asyncio, pytest-mock, pytest-cov to pyproject.toml's dev group
  and refresh uv.lock

Then add .github/workflows/ci.yml: install deps, ruff check, mypy
backend/, pytest with --cov=backend --cov-fail-under=<pick a realistic
number, e.g. 60> --cov-report=xml. Use DRIFT's frozen dependency stack and
make sure the coverage number in the workflow matches the README.
```

### Prompt 6 — Docker + judge demo path

```
Working in C:\ws\drift. Add:
- a root Dockerfile (python slim base, install from frozen `uv.lock`, run
  uvicorn)
- docker-compose.yml at repo root with three services: backend, a
  pgvector/pgvector Postgres service (with a volume + the vector extension
  pre-enabled), and frontend (once frontend has real source — if frontend
  is still just package.json with no pages, skip the frontend service for
  now and note that in a comment). Keep the services scoped to DRIFT's
  PostgreSQL + pgvector storage boundary; do not add a media service.
- A `make demo` target (Makefile at repo root) that: brings up
  docker-compose, waits for Postgres to be healthy, runs the Alembic
  migration, then runs the Scout→Synthesizer→Insight→Briefing pipeline
  against backend/sources.yaml (or a small fixture sources file with 1-2
  fast, reliable feeds) so a judge can run one command and see a real
  briefing produced without needing their own OpenAI key for anything
  beyond what's in .env. Keep the path one-command and independent of an
  external account where feasible.
- Update README.md's setup section to lead with `make demo` as the
  fastest path, keeping the manual venv/npm steps below it as the
  from-scratch alternative.
```

### Prompt 7 — Docs, license, submission finalization

```
Working in C:\ws\drift. Do the following, all documentation-only, no code
changes:

1. Add a LICENSE file at repo root — MIT license — with the correct copyright
   holder and year for this project.

2. Fill in README.md's "How Codex and GPT-5.6 were used" section with an
   honest, specific account: which parts Codex built end-to-end (typed agents,
   bounded live chat, CI, Docker, and documentation), where GPT-5.6 tiers
   were used and why, and what key decisions were made
   (e.g. why a hand-rolled agent pipeline instead of a framework, why
   pgvector over a separate vector DB). Base this on the actual git
   history/diffs once Prompts 1-6 have been run — don't fabricate specifics.

3. Record all project initiative Session IDs in `docs/INITIATIVES.md` and the
   README. The supplied initiative IDs are:
   - `019f61e7-1ea1-7742-9acc-99d62f39b888` — foundation and vertical slice
   - `019f61fc-c32e-7d92-9d2e-0bd9083d08e7` — publication and judge readiness
   - `019f6253-ddfc-7272-8077-e34dfb3aee84` — hosted deployment and README
     follow-up
   - `019f62b9-10b7-7d82-a463-e6eb1192141c` — primary core-functionality
     session for the `0.2.0` release
   - `019f62e8-6715-70e2-a92a-fe28254f7b71` — Day 1/Day 2 implementation
     follow-up
   - `019f6336-3690-7022-a8ef-c8c0947e240f` — Day 3/Day 4 Insight structured
     output
   - `019f66b4-78b8-7943-a41d-91e836d28f00` — bounded capture/provenance and
     documentation cleanup
   - `019f6773-0e96-7363-9657-0e0531c3d594` — grounding guardrails and capture
     readiness
   - `019f6a46-e3eb-7de2-81b1-91515ae80043` — submission audit and frontend
     evidence presentation

4. Leave the Demo video line as-is (placeholder) — recording is a human
   task, not a Codex task.

5. Check off any now-completed items in docs/BUILD_SEQUENCE.md.

Do not touch submission/DEVPOST.md — that file is the hackathon's own
rules/FAQ reference copy, not drift's submission draft.
```

---

## What's left for a human after all 7 prompts

- Record and upload the demo video (<3 min, narrated, covers Codex + GPT-5.6 usage)
- Confirm which supplied initiative is the primary `/feedback` session for the
  Devpost form; retain all nine IDs in the README, changelog, and submission
   notes.
- Verify branch protection and the Codecov upload on the published GitHub
  repository.
- Use `notebooks/drift_manual_run.ipynb` against a reachable database to create
  and review a small draft store, then smoke-test hosted `/search` and `/chat`
  against that reviewed, cited evidence. Railway PostgreSQL schema `0003`,
  hosted `v0.6.1` health/docs routes, Vercel canonical-banner source, and CORS
  were verified on 2026-07-15/16; on 2026-07-16 four human-reviewed Insights were
  published and hosted `/briefing`/`/search`/`/chat` verified provider-backed.
  This bounded reviewed set does not establish broad live-release analysis.

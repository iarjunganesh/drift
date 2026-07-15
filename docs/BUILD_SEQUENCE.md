# DRIFT — Build Sequence

This sequence records DRIFT's staged implementation path for GPU and
AI-infrastructure release intelligence.

## Day 1 — Scaffolding + Scout
- [x] Repo structure, model router, config, schema
- [x] sources.yaml (8 real GitHub release feeds)
- [x] Codex: implement `fetch_source()` in `scout.py` with feedparser,
      bounded retries, normalization, duplicate suppression, and persistence
- [x] Codex: async SQLAlchemy models and initial Alembic migration for
      sources, raw_items, and insights with pgvector support

## Day 2 — Dedup + Synthesizer
- [x] Codex: `embed_items()`, `cluster_items()`, `classify_change()`
- [x] Model tier: dev (Luna), routed through `model_router.py`

## Day 3-4 — Insight agent (the differentiation core)
- [x] Codex: `generate_insight()` — structured output parsing
- [x] Codex: bounded one-shot `backend.pipeline` capture path — persists and
      reloads source IDs, generates Insights, embeds and stores them, and
      records source-content hashes, model-run audit data, and optional human
      review notes
- [ ] YOU: run and review 3-5 primary-source captures through that exact path;
      use Luna for prompt iteration and Sol only for selected final examples.
      Do not mark a generated record reviewed until its release text and action
      are checked by a human.

## Day 5 — Briefing + search + chat
- [x] Codex: deterministic `build_daily_briefing()`, fixture search, and
      fixture-mode `/chat`; local `DRIFT_MODE=live` now retrieves cited
      evidence from the live store before chat
- [x] Codex: pgvector search and live-store retrieval for local live
      `/search` and `/chat`; the one-shot capture job now populates cited
      Insight rows and live `/briefing` reads that store
- [ ] YOU: apply the migration to a clean PostgreSQL instance, execute one
      reviewed capture, and deploy/verify the resulting live store
- [x] Model tier: live (Terra) for bounded local grounded chat

## Day 6-7 — Frontend
- [x] Codex: fixture briefing hero screen with severity, confidence, and
      source-aware presentation; each card now exposes summary, rationale,
      bounded check, confidence, model label, and clickable citations
- [x] No new model calls — the current UI remains presentation-only

## Day 8 — Final content + docs
- [ ] Re-run the best 3-5 reviewed primary-source examples on Tier.FINAL (Sol),
      save their persisted output and human review notes
- [x] Fill in README's "How Codex and GPT-5.6 were used" section —
      required for submission, judged under Technological Implementation
- [x] Record the primary `/feedback` Codex Session ID:
      `019f62b9-10b7-7d82-a463-e6eb1192141c`
- [x] Record the additive Day 1/Day 2 implementation follow-up session:
      `019f62e8-6715-70e2-a92a-fe28254f7b71`
- [x] Record the additive Day 3/Day 4 Insight implementation session:
      `019f6336-3690-7022-a8ef-c8c0947e240f`
- [x] Record the bounded capture/provenance and documentation-cleanup session:
      `019f66b4-78b8-7943-a41d-91e836d28f00`
- [x] docs/ARCHITECTURE.md polish, screenshots

## Day 9 — Record, submit
- [ ] Demo video (<3 min, public YouTube, must narrate Codex AND
      GPT-5.6 usage per submission requirements)
- [ ] Submit under Developer Tools track
- [ ] Repo public (with license) OR shared with testing@devpost.com
      and build-week-event@openai.com
- [ ] Submit early

## GitHub and Codecov setup

The public repository is `iarjunganesh/drift`, and the README already points
to its repository-specific Codecov badge.

1. GitHub `main` is published; continue verifying `.github/workflows/ci.yml`.
2. Confirm the `pytest` upload appears in Codecov.
3. Confirm the README badge resolves to the project report:

   ```markdown
   [![Codecov](https://codecov.io/gh/iarjunganesh/drift/graph/badge.svg)](https://codecov.io/gh/iarjunganesh/drift)
   ```

4. Protect the default branch and require the CI quality gate.
5. The Railway API is live at `https://drift-api-prod.up.railway.app`, and the
   Vercel frontend is live at `https://dr1ftless.vercel.app`. Keep the Vercel
   Root Directory set to `frontend/`; its checked-in configuration supplies
   `NEXT_PUBLIC_API_URL`. As of 2026-07-15, Railway is verified in bounded
   `DRIFT_MODE=live` with CORS allowing the Vercel origin. On 2026-07-15,
   Railway PostgreSQL migrations and one unreviewed vLLM capture were verified
   through hosted `/briefing`; hosted `/search`/`/chat` remain to be smoke-tested.

The checked-in `codecov.yml` defines the pytest project, report path, and a
100% project/patch floor for implemented code. Explicit live-stage boundaries
remain visible until each stage is implemented and tested; the standalone
Insight stage now has structured-output coverage.

## Codex project initiatives

The baseline, hosted-deployment follow-up, bounded v0.4.0 baseline, v0.5.0
capture-path release, and
implementation follow-ups are supported by seven project initiatives:

- Foundation and inspectable vertical slice —
  `019f61e7-1ea1-7742-9acc-99d62f39b888`
- Publication and judge-readiness baseline —
  `019f61fc-c32e-7d92-9d2e-0bd9083d08e7`
- Hosted deployment and README follow-up —
  `019f6253-ddfc-7272-8077-e34dfb3aee84`
- Day 1/Day 2 implementation follow-up —
  `019f62e8-6715-70e2-a92a-fe28254f7b71`
- Grounded live chat, resilience, and locked delivery (primary candidate
  initiative) — `019f62b9-10b7-7d82-a463-e6eb1192141c`
- Day 3/Day 4 Insight structured output —
  `019f6336-3690-7022-a8ef-c8c0947e240f`
- Bounded capture/provenance and documentation cleanup —
  `019f66b4-78b8-7943-a41d-91e836d28f00`

See [`INITIATIVES.md`](INITIATIVES.md) for scope and submission usage.

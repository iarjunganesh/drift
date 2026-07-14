# DRIFT — Build Sequence

Adapted from the original SIGNPOST hero sequence — same architecture,
GPU/infra sources instead of regulatory ones, Developer Tools track
instead of Work & Productivity.

## Day 1 — Scaffolding + Scout (mostly done — this scaffold)
- [x] Repo structure, model router, config, schema
- [x] sources.yaml (8 real GitHub release feeds)
- [ ] Codex: implement `fetch_source()` in `scout.py` with feedparser
- [ ] Codex: DB migrations for raw_items/insights tables

## Day 2 — Dedup + Synthesizer
- [ ] Codex: `embed_items()`, `cluster_items()`, `classify_change()`
- [ ] Model tier: dev (Luna)

## Day 3-4 — Insight agent (the differentiation core)
- [ ] Codex: `generate_insight()` — structured output parsing
- [ ] YOU: hand-iterate the prompt against 3-5 real recent releases
      (e.g. a real vLLM or TensorRT breaking change) until the
      reasoning is genuinely sharp. Don't fully delegate this step.

## Day 5 — Briefing + search + chat
- [x] Codex: deterministic `build_daily_briefing()`, fixture search, and
      `/chat`; local `DRIFT_MODE=live` is retrieve-first chat over cited
      fixture evidence
- [ ] Codex: pgvector search and live-store retrieval
- [x] Model tier: live (Terra) for bounded local grounded chat

## Day 6-7 — Frontend
- [x] Codex: fixture briefing hero screen with severity, confidence, and
      source-aware presentation
- [ ] No new model calls — UI wiring only

## Day 8 — Final content + docs
- [ ] Re-run best 3-5 real examples on Tier.FINAL (Sol), save outputs
- [ ] Fill in README's "How Codex and GPT-5.6 were used" section —
      required for submission, judged under Technological Implementation
- [x] Record the primary `/feedback` Codex Session ID:
      `019f62b9-10b7-7d82-a463-e6eb1192141c`
- [ ] docs/ARCHITECTURE.md polish, screenshots

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
5. The Railway fixture API is live at
   `https://drift-api-prod.up.railway.app`, and the Vercel frontend is live at
   `https://dr1ftless.vercel.app`. Keep the Vercel Root Directory set to
   `frontend/`; its checked-in configuration supplies `NEXT_PUBLIC_API_URL`.
   Verify Railway CORS allows the Vercel origin before treating the hosted
   briefing as browser-connected.

The checked-in `codecov.yml` defines the pytest project, report path, and a
100% project/patch floor for implemented code. Explicit live-stage stubs keep
their `NotImplementedError` boundary visible while excluding only that boundary
until the stage is implemented and tested.

## Codex project initiatives

The baseline, hosted-deployment follow-up, and current release candidate are
supported by four project initiatives:

- Foundation and inspectable vertical slice —
  `019f61e7-1ea1-7742-9acc-99d62f39b888`
- Publication and judge-readiness baseline —
  `019f61fc-c32e-7d92-9d2e-0bd9083d08e7`
- Hosted deployment and README follow-up —
  `019f6253-ddfc-7272-8077-e34dfb3aee84`
- Grounded live chat, resilience, and locked delivery (primary candidate
  initiative) — `019f62b9-10b7-7d82-a463-e6eb1192141c`

See [`INITIATIVES.md`](INITIATIVES.md) for scope and submission usage.

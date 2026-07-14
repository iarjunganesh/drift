# DRIFT project initiatives

These are the four Codex project initiatives associated with the DRIFT baseline,
publication follow-up, and `0.2.0` release candidate. They are submission
evidence pointers for the build work; they are not model-run provenance and do
not turn fixture records into live analysis.

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

This is the primary implementation initiative for the current release
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

## Submission usage

All four IDs should be retained in the project README and submission notes. If
Devpost requires one primary `/feedback` session, use Initiative 04:
`019f62b9-10b7-7d82-a463-e6eb1192141c`. List the earlier sessions as the
foundation, publication, and hosted-demo follow-up initiatives.

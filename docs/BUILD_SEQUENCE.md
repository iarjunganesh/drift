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
      reloads source IDs, creates claim-grounded drafts, separately verifies
      them, embeds/stores them, and records source hashes plus both model-run
      audits
- [x] Codex: claim evidence spans/offsets/hashes, `direct_fact`/`inference`/
      `recommended_check` labels, upstream PR/commit references, review-first
      live-store filtering, calibration fixtures, and manual capture notebook
- [x] Operator: ran the manual notebook against eight primary-release sources;
      six drafts passed verification and four were human-reviewed/published
      (Transformers, vLLM, NCCL, TensorRT) with recorded notes. The `dev`/Luna
      tier bounded the first pass; the later Sol final pass is archived below.

## Day 5 — Briefing + search + chat
- [x] Codex: deterministic `build_daily_briefing()`, fixture search, and
      fixture-mode `/chat`; local `DRIFT_MODE=live` now retrieves cited
      evidence from the live store before chat
- [x] Codex: pgvector search and live-store retrieval for local live
      `/search` and `/chat`; the one-shot capture job now populates cited
      Insight rows and live `/briefing` reads that store
- [x] Operator: Railway PostgreSQL schema verified through
      `0003_claim_evidence_review_gate` via its public TCP proxy (2026-07-16)
- [x] Operator: hosted `v0.6.1` `/health`, empty fail-closed `/briefing`,
      `/docs`, Vercel canonical-banner source, and CORS verified (2026-07-16)
- [x] Operator: smoke-tested hosted provider-backed `/briefing`, `/search`, and
      `/chat` against the four reviewed Insights on 2026-07-16
- [x] Model tier: live (Terra) for bounded local grounded chat

## Day 6-7 — Frontend
- [x] Codex: fixture briefing hero screen with severity, confidence, and
      source-aware presentation; explicit loading, empty, and error states;
      system-theme-aware canonical banners; live cards expose review status,
      claim types, exact evidence links, risk labels, bounded check, and model label
- [x] Codex: released `v0.6.1` frontend/documentation changes; Railway and
      Vercel source deployment were verified, including the API-docs
      system-theme-aware banner frame
- [x] Operator: deployed `v0.7.0`; Railway `/health`/`/docs`, Vercel CORS,
      review-note redaction in `/briefing` and `/openapi.json`, and the deployed
      frontend's `top_n=10` request were verified
- [x] Codex: released and hosted-verified `v0.8.0` — Ask DRIFT validates the public
      `/chat` boundary, and no-key fixture claims point to checked-in synthetic
      source text with verified offsets and hashes; Railway `/health` reported
      `0.8.0`, `/docs` returned `200`, the public Vercel page rendered Ask DRIFT,
      and Vercel CORS passed (paid `/search` and `/chat` were not re-invoked)
- [x] Source patch `v0.8.1`: structured live-chat grounding IDs now restrict
      question citations to the Insights actually used; tests cover subset,
      malformed-response, blank-answer, and router-schema behavior. This patch
      is tagged on `feature/v0.9.0-final-evidence`; hosted verification remains
      pending.
- [x] No new model calls — the current UI remains presentation-only

## Day 8 — Final content + docs
- [x] Targeted `v0.9.0` evidence pass: eight Tier.FINAL (Sol) drafts were
      captured and verified; five were human-reviewed and published to the live
      Railway store (IDs 10, 11, 13, 15, and 16), while Luna IDs 3, 6, 7, and 8
      were retracted to draft.
- [x] Freeze-boundary review: no optional polish was added beyond the focused
      evidence and grounding work recorded below.
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
- [x] Demo video (<3 min, public YouTube, must narrate Codex AND
      GPT-5.6 usage per submission requirements) — published at
      <https://youtu.be/6sbIz0ZR8Hw>, 2:45 runtime.
- [ ] Submit under Developer Tools track
- [x] Repo public (with license) OR shared with testing@devpost.com
      and build-week-event@openai.com — verified via `gh repo view`:
      `isPrivate: false`, MIT license.
- [ ] Submit early

## Targeted release path — after the current hosted `v0.10.0`

- [x] `v0.9.0`: publish verified Tier.FINAL evidence and selected,
      independently verified polish; the source/evidence release is prepared,
      while the deployed app was still `v0.8.0` at that point.
- [x] Record the v0.9.0 evidence-cleanup and session-synchronization session:
      `019f7213-be19-7e50-92ac-a48bd5ecaacb`
- [x] `v0.9.1`: run and independently verify bounded Terra (`gpt-5.6-terra`)
      grounded-run evidence, archive the true retrieve-first grounding, and
      synchronize the source release boundary. The refreshed nine-image
      screenshot gallery is committed as bounded visual evidence. The `v0.9.1`
      build was subsequently deployed and verified on 2026-07-18 (`/health` and
      `/` report `0.9.1`, `/briefing` returns the five reviewed Insights).
- [x] Record the v0.9.1 evidence and screenshot synchronization session:
      `019f7278-ee77-7f02-bafd-6eba8bf046d2`
- [x] `v0.10.0`: implement the thin-client MCP integration (`integrations/mcp/`,
      ADR-011) — three stdio tools over the existing public API, no credentials,
      nothing changed under `backend/`; verified end-to-end against a
      fixture-mode API at $0 with 40 mocked-HTTP tests at 100% `integrations/`
      coverage. Ruff/mypy/test targets extend to `integrations/`. The `v0.10.0`
      build was subsequently deployed and verified on 2026-07-18 (`/health` and
      `/` report `0.10.0`, `/briefing` returns the five reviewed Insights).
- [x] Record the v0.10.0 MCP thin-client implementation session:
      `019f7607-aa5a-79b2-8101-4cd634495fbe`
- [x] `v0.10.1`: commit the VS Code MCP client evidence (four gallery captures
      plus the credential-free `.vscode/mcp.json`), renumber the screenshot
      gallery, remove the superseded internal freeze plan, and synchronize every
      current-state record with the hosted `v0.10.0` verification. The bounded
      scrubbed MCP response archive remains the pending MCP operator gate.
- [x] `v0.10.2`: add a deterministic `upstream_release_type` classification
      (`backend/core/versioning.py`, ADR-012) and apply it to the three
      reviewed Insights with no self-declared source statement (JAX, NCCL,
      TensorRT), written directly to the live database. Not yet wired into
      `backend.pipeline` for future captures — deliberately out of scope.
- [ ] `v1.0.0`: freeze the final judge path and finish the Devpost submission
      records. The under-three-minute public demo video is done — published
      at <https://youtu.be/6sbIz0ZR8Hw> (2:45), and the placeholder is
      replaced everywhere.

See the planned-release record in [`CHANGELOG.md`](../CHANGELOG.md). These are
targets, not current version claims.

## GitHub and Codecov setup

The public repository is `iarjunganesh/drift`, and the README already points
to its repository-specific Codecov badge.

1. GitHub `main` is published; continue verifying `.github/workflows/ci.yml`.
2. The `pytest` upload is confirmed on Codecov (2026-07-17) — the repository and
   `flag=pytest` coverage badges both resolve to 100%.
3. The README badge resolves to the project report:

   ```markdown
   [![Codecov](https://codecov.io/gh/iarjunganesh/drift/graph/badge.svg)](https://codecov.io/gh/iarjunganesh/drift)
   ```

4. The default branch is protected (2026-07-17): `main` requires the five CI
   quality-gate checks (Ruff lint, Mypy type check, Tests and coverage, Frontend
   build, Documentation hygiene) with strict up-to-date merges; admins retain a
   bypass for pre-deadline hotfixes.
5. The Railway API is live at `https://drift-api-prod.up.railway.app`, and the
   Vercel frontend is live at `https://dr1ftless.vercel.app`. Keep the Vercel
   Root Directory set to `frontend/`; its checked-in configuration supplies
   `NEXT_PUBLIC_API_URL`. As of 2026-07-15, Railway is verified in bounded
   `DRIFT_MODE=live` with CORS allowing the Vercel origin. On 2026-07-15,
   Railway PostgreSQL migrations and one unreviewed vLLM capture were verified
   through the prior hosted `/briefing`; the review-gate schema and hosted
   `v0.6.0` empty briefing are now verified. On 2026-07-16, four human-reviewed
   Insights were published and hosted `/briefing`, `/search`, and `/chat` were
   verified provider-backed.

The checked-in `codecov.yml` defines the pytest project, report path, and a
100% project/patch floor for implemented code. Explicit live-stage boundaries
remain visible until each stage is implemented and tested; the standalone
Insight stage now has structured-output coverage.

## Codex project initiatives

The baseline, hosted-deployment follow-up, bounded v0.4.0 baseline, v0.5.0
capture-path release, and
implementation follow-ups are supported by fourteen project initiatives:

- Foundation and inspectable vertical slice —
  `019f61e7-1ea1-7742-9acc-99d62f39b888`
- Publication and judge-readiness baseline —
  `019f61fc-c32e-7d92-9d2e-0bd9083d08e7`
- Hosted deployment and README follow-up —
  `019f6253-ddfc-7272-8077-e34dfb3aee84`
- Grounded live chat, resilience, and locked delivery (primary candidate
  initiative) — `019f62b9-10b7-7d82-a463-e6eb1192141c`
- Day 1/Day 2 implementation follow-up —
  `019f62e8-6715-70e2-a92a-fe28254f7b71`
- Day 3/Day 4 Insight structured output —
  `019f6336-3690-7022-a8ef-c8c0947e240f`
- Bounded capture/provenance and documentation cleanup —
  `019f66b4-78b8-7943-a41d-91e836d28f00`
- Grounding guardrails and capture readiness —
  `019f6773-0e96-7363-9657-0e0531c3d594`
- Submission audit and frontend evidence presentation —
  `019f6a46-e3eb-7de2-81b1-91515ae80043`
- Reviewed-evidence hardening and `v0.8.0` hosted verification —
  `019f6a78-6fa2-7121-9059-85ac8ceb9904`
- Freeze-plan audit and documentation synchronization —
  `019f7190-912d-70e3-be6d-fcc81bf8e203`
- v0.9.0 evidence cleanup and session synchronization —
  `019f7213-be19-7e50-92ac-a48bd5ecaacb`
- v0.9.1 evidence and screenshot synchronization —
  `019f7278-ee77-7f02-bafd-6eba8bf046d2`
- v0.10.0 MCP thin-client implementation —
  `019f7607-aa5a-79b2-8101-4cd634495fbe`

See [`INITIATIVES.md`](INITIATIVES.md) for scope and submission usage.

# DRIFT demo runbook

This is the repeatable operator path for the current fixture demo and the
recording path for the future live demo. It deliberately mirrors the product
truth boundary in [`ARCHITECTURE.md`](ARCHITECTURE.md).

## Fixture demo — current judge path

1. Create a virtual environment and synchronize the locked development group:
   `uv venv .venv` followed by `uv sync --locked --group dev`.
2. Copy `.env.example` to `.env`; leave `DRIFT_MODE=fixture`.
3. Start `uv run uvicorn backend.main:app --reload` from the repository root.
4. Open `/docs` and point out the same paired, system-theme-aware DRIFT banners
   used in the README and frontend, then inspect `/briefing`, search `vllm`, and
   send a chat question.
5. Point out the source links, confidence, and `fixture-curated` audit label;
   each link opens checked-in synthetic source text rather than an upstream
   release note.
6. If showing the frontend, run `npm --prefix frontend ci` and
   `npm --prefix frontend run dev` in a second terminal.

This path uses committed example data and makes no external calls.

## Local capture-path verification

1. Start the local PostgreSQL/pgvector service from `docker-compose.yml`.
2. Run `make migrate` to apply the initial `sources`, `raw_items`, and
   `insights` migration.
3. Run `uv run python -m backend.agents.scout` to fetch and normalize the
   configured primary release feeds. Source failures are bounded and logged;
   no model call or database write is made by this inspection command.
4. After reviewing source candidates, set `DRIFT_MODE=live` and open the
   **DRIFT Manual Run** in
   [`notebooks/drift_manual_run.ipynb`](../notebooks/drift_manual_run.ipynb). It
   presents the source roster, spend-gated capture, frozen claim evidence,
   review decision, and immutable archive as one visible proof chain. It
   persists/reloads raw items, generates claim-grounded drafts, runs a separate
   verifier, embeds the results, and writes two model-run/source-hash audits.
   Full raw evidence is retained; only the derived text sent for clustering
   embeddings is bounded. The notebook begins with one item per configured
   source (at most eight) and never publishes automatically:

   ```powershell
   uv run --with jupyterlab jupyter lab notebooks/drift_manual_run.ipynb
   ```

5. The notebook refuses Railway's private `postgres.railway.internal` address;
   use local PostgreSQL, a public/tunneled `DATABASE_URL`, or Railway's public
   TCP proxy. For the proxy, retain the complete private `DATABASE_URL` and set
   `DRIFT_DATABASE_PUBLIC_HOST` plus `DRIFT_DATABASE_PUBLIC_PORT`; only the
   endpoint is replaced locally, so credentials do not enter the notebook.
   Inspect every frozen excerpt, claim type, upstream reference, risk label, and
   bounded action. A verifier pass is model-aided screening, not proof. Enter
   only human-reviewed IDs and meaningful notes in the final publication cell.
   Then use the notebook's archive cell to write the reviewed public evidence
   and SHA-256 manifest to `assets/evidence/`; it excludes review notes and
   secrets and refuses overwrites. Re-run only selected examples on `Tier.FINAL`;
   this is a paid provider operation bounded by the local spend ledger.

## Live grounded-chat demo — local live store, real model response

1. Copy `.env.example` to `.env`; keep the file untracked. On Railway, bind
   the API service directly to the database service's complete native
   `DATABASE_URL`; the application normalizes its `postgres://` or
   `postgresql://` prefix for asyncpg.
2. Add `OPENAI_API_KEY` locally. Do not send it through chat, issues, or commits.
3. Set `DRIFT_MODE=live`, then confirm `DRIFT_MAX_SPEND_USD=10`, alert `$5`,
   and per-attempt reservation `$1`. Keep
   `DRIFT_MAX_CALL_USD * DRIFT_MODEL_MAX_ATTEMPTS` within the project spend
   ceiling.
4. Apply migrations through `0003_claim_evidence_review_gate`, then use the
   manual notebook to create a deliberately small **draft** capture. It writes
   `insights` rows with 1536-value embeddings, frozen claim spans, and linked
   generation/verifier `model_runs`. Inspect the draft before using the explicit
   publication cell. Only then start the API and inspect live `/briefing`,
   `/search`, and one matching chat question. Inspect `.drift/spend-ledger.json`;
   chat should report `gpt-5.6-terra` and preserve source citations.
5. The request is queue-bounded and uses a per-attempt timeout, jittered
   transient retry, and a circuit breaker. A `503` with `Retry-After` means
   model capacity is busy or the circuit is open; retry later. A `429` means
   the local spend guard blocked the request.
6. Local live `/briefing`, `/search`, and `/chat` read only reviewed,
   verifier-passed records; drafts are intentionally invisible. On 2026-07-15,
   Railway PostgreSQL migrations and one unreviewed vLLM capture were verified
   through the prior hosted `/briefing` and the Vercel CORS preflight. The new
   gate's `0003` schema was verified through Railway's public TCP proxy on
   2026-07-16; hosted `v0.6.1` then passed `/health`, `/briefing`, `/docs`, and
   CORS checks. After four human-reviewed Insights were published that day,
   hosted `/briefing`, `/search`, and `/chat` were verified provider-backed over
   that reviewed set. The Vercel HTML references the canonical API-served banner
   pair. The `v0.7.0` deployment adds evidence-byte integrity, database-only
   review notes, and a ten-item frontend request; Railway `/health`/`/docs`,
   CORS, public redaction, and the Vercel bundle were verified after rollout.
   On 2026-07-17, `v0.8.0` Railway `/health` reported `0.8.0`, `/docs` returned
   `200`, the public Vercel page rendered Ask DRIFT, and Vercel CORS passed.
   Paid `/search` and `/chat` were not re-invoked for this rollout.
   Scheduled population and a larger reviewed capture remain future work.

   The source-only `v0.8.1` patch adds structured model grounding IDs so live
   Ask DRIFT citations are limited to the Insights used for the answer. It is
   tagged on `feature/v0.9.0-final-evidence`; do not describe it as hosted until
   Railway/Vercel deployment and `/health` verification are complete.

   The `v0.9.1` Terra evidence pass is archived at
   [`assets/evidence/2026-07-18-all-sources-terra.json`](../assets/evidence/2026-07-18-all-sources-terra.json)
   with its adjacent SHA-256 manifest. It asked eight bounded questions over
   the five reviewed Insights, wrote no database rows, and records Terra's
   actual grounded Insight IDs rather than the UX fallback retrieval window.

## MCP thin client — local fixture run and hosted verification

The `integrations/mcp/` server ([ADR-011](adr/011-mcp-thin-client-layer.md)) is a
thin client over the public API. It reads only `DRIFT_API_URL` (plus an optional
`DRIFT_MCP_TIMEOUT_SECONDS` request timeout) and holds no
credentials, so it is developed and demonstrated entirely against a fixture-mode
API at zero cost.

### Local fixture-mode run ($0)

1. Install the optional SDK group: `uv sync --group integrations`. The core
   install is unchanged; nothing under `backend/` or the Docker image changes.
2. Start a DRIFT API to point at, in the default fixture mode:
   `uv run uvicorn backend.main:app`.
3. Exercise the tools. Either configure a real MCP client (Claude Desktop or
   Cursor) with the snippet in the README's *Use DRIFT inside your AI assistant*
   section, or drive them directly:

   ```powershell
   $env:DRIFT_API_URL = "http://localhost:8000"
   uv run python -m integrations.mcp   # stdio server for a connected client
   ```

4. Verify all three tools: `drift_briefing` ranks the reviewed examples,
   `drift_search` for `vllm` matches, `ask_drift` returns a grounded, cited
   answer, and a question outside the reviewed corpus **declines** rather than
   guessing (the `/chat` 404 is surfaced as a decline).
5. Run the mocked-HTTP suite outside the backend coverage gate:
   `make test-integrations`.

### Hosted verification (pending operator gate)

Point `DRIFT_API_URL` at the hosted API
(`https://drift-api-prod.up.railway.app`) and run one bounded capture: the
briefing, one search, and 3–5 `ask_drift` questions (~$0.10–0.25 total). Archive
the run as `assets/evidence/2026-07-XX-mcp-<model>.json` with a SHA-256 manifest,
and screenshot one real MCP client for the gallery. No hosted MCP claim is
written anywhere until this capture has actually run. The MCP server carries no
credentials; every guarantee (reviewed-only reads, redacted review notes, spend
guards, resilience) is enforced server-side.

## Recording order

1. State the operational problem: release drift reaches production teams late.
2. Show a source-linked briefing and a visible confidence label.
3. Search an affected library and ask a grounded chat question.
4. Show the cited release source.
5. Show the architecture diagram and the relevant ADR boundary.
6. Explain how Codex built the pipeline. Describe GPT-5.6 only according to
   verified live output; do not call fixture-curated text a model run.

The complete shot list and narration timing are in
[`submission/DEMO_SCRIPT.md`](../submission/DEMO_SCRIPT.md).

## Project initiative records

The fourteen Codex initiatives associated with this baseline, deployment follow-up,
the v0.4.0 baseline, v0.5.0 capture-path release, and implementation follow-ups
are listed in
[`INITIATIVES.md`](INITIATIVES.md):

- Foundation: `019f61e7-1ea1-7742-9acc-99d62f39b888`
- Publication/readiness: `019f61fc-c32e-7d92-9d2e-0bd9083d08e7`
- Hosted deployment/README follow-up: `019f6253-ddfc-7272-8077-e34dfb3aee84`
- Primary live-chat/resilience work: `019f62b9-10b7-7d82-a463-e6eb1192141c`
- Day 1/Day 2 implementation follow-up: `019f62e8-6715-70e2-a92a-fe28254f7b71`
- Day 3/Day 4 Insight structured output: `019f6336-3690-7022-a8ef-c8c0947e240f`
- Bounded capture/provenance and documentation cleanup:
  `019f66b4-78b8-7943-a41d-91e836d28f00`
- Grounding guardrails and capture readiness:
  `019f6773-0e96-7363-9657-0e0531c3d594`
- Submission audit and frontend evidence presentation:
  `019f6a46-e3eb-7de2-81b1-91515ae80043`
- Reviewed-evidence hardening and `v0.8.0` hosted verification:
  `019f6a78-6fa2-7121-9059-85ac8ceb9904`
- Freeze-plan audit and documentation synchronization:
  `019f7190-912d-70e3-be6d-fcc81bf8e203`
- v0.9.0 evidence cleanup and session synchronization:
  `019f7213-be19-7e50-92ac-a48bd5ecaacb`
- v0.9.1 evidence and screenshot synchronization:
  `019f7278-ee77-7f02-bafd-6eba8bf046d2`
- v0.10.0 MCP thin-client implementation (ADR-011), recorded in
  [`INITIATIVES.md`](INITIATIVES.md) as Initiative 14:
  `019f7607-aa5a-79b2-8101-4cd634495fbe`

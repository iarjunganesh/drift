# DRIFT demo runbook

This is the repeatable operator path for the current fixture demo and the
recording path for the future live demo. It deliberately mirrors the product
truth boundary in [`ARCHITECTURE.md`](ARCHITECTURE.md).

## Fixture demo — current judge path

1. Create a virtual environment and synchronize the locked development group:
   `uv venv .venv` followed by `uv sync --locked --group dev`.
2. Copy `.env.example` to `.env`; leave `DRIFT_MODE=fixture`.
3. Start `uv run uvicorn backend.main:app --reload` from the repository root.
4. Open `/docs`, inspect `/briefing`, search `vllm`, then send a chat question.
5. Point out the source links, confidence, and `fixture-curated` audit label.
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
4. After reviewing source candidates, set `DRIFT_MODE=live` and run the
   bounded capture command. It persists/reloads raw items, generates and embeds
   Insights, and writes model-run/source-hash provenance:

   ```powershell
   $env:DRIFT_MODE='live'
   uv run python -m backend.pipeline --source vllm --source tensorrt --source pytorch --tier dev
   ```

5. Inspect the stored result and its citations before writing any optional
   `--review-notes`. Re-run only selected examples on `--tier final`; this is a
   paid provider operation bounded by the local spend ledger.

## Live grounded-chat demo — local live store, real model response

1. Copy `.env.example` to `.env`; keep the file untracked.
2. Add `OPENAI_API_KEY` locally. Do not send it through chat, issues, or commits.
3. Set `DRIFT_MODE=live`, then confirm `DRIFT_MAX_SPEND_USD=10`, alert `$5`,
   and per-attempt reservation `$1`. Keep
   `DRIFT_MAX_CALL_USD * DRIFT_MODEL_MAX_ATTEMPTS` within the project spend
   ceiling.
4. Apply the migration, then use `backend.pipeline` to create a deliberately
   small reviewed capture. It writes `insights` rows with 1536-value embeddings
   and linked `model_runs` records. Start the API and inspect live `/briefing`,
   `/search`, and one matching chat question. Inspect `.drift/spend-ledger.json`;
   chat should report `gpt-5.6-terra` and preserve source citations.
5. The request is queue-bounded and uses a per-attempt timeout, jittered
   transient retry, and a circuit breaker. A `503` with `Retry-After` means
   model capacity is busy or the circuit is open; retry later. A `429` means
   the local spend guard blocked the request.
6. Local live `/briefing`, `/search`, and `/chat` now read the captured store.
   This still is not live release analysis until the capture is human-reviewed,
   saved as evidence, deployed, and verified. Scheduled population remains
   future work. The hosted deployment predates this local path until redeployed
   and checked.

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

The seven Codex initiatives associated with this baseline, deployment follow-up,
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

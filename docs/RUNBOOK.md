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

## Day 1 feed and database verification

1. Start the local PostgreSQL/pgvector service from `docker-compose.yml`.
2. Run `make migrate` to apply the initial `sources`, `raw_items`, and
   `insights` migration.
3. Run `uv run python -m backend.agents.scout` to fetch and normalize the
   configured primary release feeds. Source failures are bounded and logged;
   no model call is made.

## Live grounded-chat demo — local live store, real model response

1. Copy `.env.example` to `.env`; keep the file untracked.
2. Add `OPENAI_API_KEY` locally. Do not send it through chat, issues, or commits.
3. Set `DRIFT_MODE=live`, then confirm `DRIFT_MAX_SPEND_USD=10`, alert `$5`,
   and per-attempt reservation `$1`. Keep
   `DRIFT_MAX_CALL_USD * DRIFT_MODEL_MAX_ATTEMPTS` within the project spend
   ceiling.
4. Apply the migration, then ensure the `insights` table contains persisted
   rows with 1536-value embeddings before starting the API. Ask one question
   that matches a stored Insight. Inspect `.drift/spend-ledger.json`; the
   response should report `gpt-5.6-terra` and preserve source citations.
   The repository does not yet provide the scheduled producer that populates
   those rows; use the fixture demo until a prepared live store is available.
5. The request is queue-bounded and uses a per-attempt timeout, jittered
   transient retry, and a circuit breaker. A `503` with `Retry-After` means
   model capacity is busy or the circuit is open; retry later. A `429` means
   the local spend guard blocked the request.
6. Local live `/search` and `/chat` now use pgvector retrieval. This still is
   not live release analysis: scheduled Scout persistence, embedding
   persistence, generated Insight persistence, and end-to-end wiring remain
   future work. The hosted deployment remains on its previously verified
   fixture-backed behavior until redeployed and checked.

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

The six Codex initiatives associated with this baseline, deployment follow-up,
the bounded v0.4.0 release, and Day 1/Day 2 and Day 3/Day 4 implementation
follow-ups are listed in
[`INITIATIVES.md`](INITIATIVES.md):

- Foundation: `019f61e7-1ea1-7742-9acc-99d62f39b888`
- Publication/readiness: `019f61fc-c32e-7d92-9d2e-0bd9083d08e7`
- Hosted deployment/README follow-up: `019f6253-ddfc-7272-8077-e34dfb3aee84`
- Primary live-chat/resilience work: `019f62b9-10b7-7d82-a463-e6eb1192141c`
- Day 1/Day 2 implementation follow-up: `019f62e8-6715-70e2-a92a-fe28254f7b71`
- Day 3/Day 4 Insight structured output: `019f6336-3690-7022-a8ef-c8c0947e240f`

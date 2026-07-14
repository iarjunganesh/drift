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

## Live grounded-chat demo — fixture evidence, real model response

1. Copy `.env.example` to `.env`; keep the file untracked.
2. Add `OPENAI_API_KEY` locally. Do not send it through chat, issues, or commits.
3. Set `DRIFT_MODE=live`, then confirm `DRIFT_MAX_SPEND_USD=10`, alert `$5`,
   and per-attempt reservation `$1`. Keep
   `DRIFT_MAX_CALL_USD * DRIFT_MODEL_MAX_ATTEMPTS` within the project spend
   ceiling.
4. Start the API and ask one question that matches a fixture insight. Inspect
   `.drift/spend-ledger.json`; the response should report `gpt-5.6-terra` and
   preserve the retrieved source citations.
5. The request is queue-bounded and uses a per-attempt timeout, jittered
   transient retry, and a circuit breaker. A `503` with `Retry-After` means
   model capacity is busy or the circuit is open; retry later. A `429` means
   the local spend guard blocked the request.
6. This is model-backed chat over fixture evidence, not live release analysis.
   Scout, Synthesizer, embeddings, and generated Insight records remain future
   work.

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

The four Codex initiatives associated with this baseline, deployment follow-up,
and current release candidate are listed in
[`INITIATIVES.md`](INITIATIVES.md):

- Foundation: `019f61e7-1ea1-7742-9acc-99d62f39b888`
- Publication/readiness: `019f61fc-c32e-7d92-9d2e-0bd9083d08e7`
- Hosted deployment/README follow-up: `019f6253-ddfc-7272-8077-e34dfb3aee84`
- Primary live-chat/resilience work: `019f62b9-10b7-7d82-a463-e6eb1192141c`

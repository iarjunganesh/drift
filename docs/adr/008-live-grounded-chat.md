# ADR-008: Live grounded chat over the fixture store

**Status:** Accepted  
**Date:** 2026-07-15

## Decision

`DRIFT_MODE=live` enables only the retrieve-first `/chat` model call. It reads
the existing cited fixture store, uses the `live` router tier, and enforces the
local `SpendGuard`. Fixture mode remains the default and makes no provider call.

## Context

The fixture API already retrieves cited insights but previously composed its
chat answer deterministically. A local API key should enable a narrowly
scoped, inspectable model path without implying that live feed ingestion,
embedding retrieval, or durable model-run provenance exists.

## Consequences

- The server loads a local, gitignored `.env` without overriding deployed
  environment variables.
- The model receives at most three retrieved insights as explicitly untrusted
  JSON evidence and may answer only from that evidence.
- A missing retrieval match still returns 404; budget exhaustion returns 429;
  capacity exhaustion and an open circuit return retryable 503 responses; and
  provider failures after retries return 502 without exposing provider details.
- The retry, timeout, bulkhead, circuit, and conservative settlement mechanics
  are governed by ADR-009; this ADR remains the scope boundary for live chat.
- Scheduled Scout persistence, live-store population, embedding persistence,
  generated Insight records, and end-to-end Scout/Synthesizer wiring remain
  implementation boundaries.

## Implementation addendum — 2026-07-15

The original hosted/fixture boundary remains the verified deployment behavior.
The current local code additionally supports live `/search` and `/chat` over
populated PostgreSQL/pgvector Insight rows: it embeds the query, retrieves
cited rows by cosine distance, and only then invokes the live chat model. This
local path is not a hosted live-release-analysis claim until the database is
populated, exercised against PostgreSQL, and redeployed/verified.

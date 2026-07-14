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
- Generated Insight records and the Scout/Synthesizer pipeline remain
  implementation boundaries.

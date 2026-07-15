# ADR-009: Bounded model resilience and locked delivery

**Status:** Accepted  
**Date:** 2026-07-15

## Decision

Live model calls use an application-owned retry budget, configured client
timeout, circuit breaker, and conservative spend settlement. Interactive chat
also uses a queue-bounded concurrency bulkhead. Python dependencies have one
resolution authority: `uv.lock`, used unchanged by local development, CI,
release builds, and the Railway image.

## Context

An async request can be cancelled, time out after provider receipt, or be
retried while an upstream provider is unhealthy. SDK-default retries obscure the
number of attempts and make local budget accounting unreliable. The former
Docker build separately installed broad requirement ranges, allowing it to
resolve a different dependency set from CI.

## Consequences

- The OpenAI client disables SDK retries; DRIFT owns bounded retries and
  retryable-error classification.
- The retry envelope must fit the configured project budget. Failed or
  cancelled potentially billable attempts are conservatively charged at the
  configured per-attempt maximum.
- Capacity exhaustion and an open circuit return a retryable `503`; the budget
  is not reserved until a bulkhead slot is acquired.
- Synchronous embeddings, classification, and Insight generation use the same
  retry/circuit and spend-reservation policy as the capture path.
- The Dockerfile installs the application through `uv sync --frozen --no-dev`.
  The obsolete duplicate runtime requirements file is removed.
- These controls are process-local and do not claim multi-instance coordination.

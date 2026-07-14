# ADR-002: Typed hand-rolled agents

**Status:** Accepted  
**Date:** 2026-07-14

## Decision

Each pipeline stage uses a small `BaseAgent` contract with explicit typed input
and output. DRIFT does not adopt a general-purpose agent-orchestration
framework for the four-stage pipeline.

## Context

Scout → Synthesizer → Insight → Briefing is a fixed, inspectable sequence. The
system needs provider boundaries, validation, and observability—not autonomous
planning or dynamic tool routing.

## Rationale

- Plain Python keeps the dependency and upgrade surface small.
- Explicit contracts make provider calls straightforward to mock.
- Lifecycle logging is visible in the code instead of hidden in framework
  callbacks.
- The pipeline can adopt a framework later if dynamic routing becomes a real
  requirement rather than a theoretical possibility.

## Consequences

Composition remains the application's responsibility. That is a small amount
of code to maintain, in exchange for easier testing and clearer failure modes.

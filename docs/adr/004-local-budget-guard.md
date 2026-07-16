# ADR-004: Local budget guard

**Status:** Accepted  
**Date:** 2026-07-14

## Decision

Live development calls use a file-backed `SpendGuard` with a `$10` project
ceiling, a `$5` warning threshold, and a maximum `$1` reservation per call.

## Context

Prompt iteration can consume budget invisibly when multiple agents and tiers are
being tested. The build needs a conservative local brake while humans select the
small set of final examples.

## Consequences

- Estimated cost is reserved before a provider call.
- Actual usage is settled afterward.
- A blocked call must not reach the provider.
- This is a single-process development guard, not a billing or quota system for
  production deployment.

## 2026-07-15 addendum — usage-settled embeddings

`text-embedding-3-small` calls now settle against their returned
`prompt_tokens` at the router's published embedding rate. This replaces the
earlier full-call-cap settlement after successful embeddings, while preserving
the conservative cap for failed or usage-unknown calls. The Scout's complete
raw evidence remains durable; the derived text used only for clustering
embeddings is capped before it reaches the embedding API.

## 2026-07-15 addendum — separate verifier reservation

Each generated Insight draft now makes a separate structured verifier call.
Both the drafting and verification calls pass independently through the same
`SpendGuard`, retry envelope, and ledger, so a reviewer cannot mistake the
drafting reservation for the total provider exposure of a capture.

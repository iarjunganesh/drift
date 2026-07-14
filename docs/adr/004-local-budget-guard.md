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

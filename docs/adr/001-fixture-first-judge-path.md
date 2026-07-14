# ADR-001: Fixture-first judge path

**Status:** Accepted  
**Date:** 2026-07-14

## Decision

DRIFT ships a deterministic fixture API before enabling live feeds, database
startup, or model calls by default.

## Context

A judge should be able to exercise the product without an OpenAI key, a running
Postgres instance, network reliability, or hidden preparation steps. The live
pipeline is valuable, but it is also the part most exposed to credentials,
provider availability, and schema drift.

## Consequences

- `DRIFT_MODE=fixture` is the safe default.
- Fixture records are explicitly labelled as examples.
- The live path must not weaken the fixture path while it is being built.
- A future release can make live mode easier to activate without making it the
  only way to demonstrate the product.

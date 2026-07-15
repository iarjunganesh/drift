# ADR-006: CI quality gates and coverage ratchet

**Status:** Accepted  
**Date:** 2026-07-14

## Decision

Every pull request and protected-branch push runs Ruff, mypy, pytest with
coverage, and repository/documentation hygiene checks. The initial coverage
floor is 81% and must be ratcheted toward 99–100% as live stages gain tests.

## Context

The fixture path is already useful, but much of the live pipeline is still
scaffolded. A high arbitrary threshold would either block honest progress or
encourage meaningless tests; no threshold would let regressions pass silently.

## Consequences

- CI reflects the checks contributors can run locally.
- Coverage is a minimum, not a quality substitute.
- Provider calls must be mocked in unit tests.
- The coverage floor is 100% for implemented and mocked behavior; durable
  persistence, database integration, and end-to-end pipeline work must retain
  that floor as they are added.

## Amendment — 2026-07-15

The implemented fixture and live-grounded-chat paths now run at 100% line
coverage. CI and Codecov enforce a 100% floor. Explicit future boundaries for
scheduled Scout persistence, live-store population, and database integration
remain visible until each stage has real behavior and tests.
The standalone structured Insight generator is now implemented with mocked
provider coverage; durable Insight persistence and end-to-end wiring remain
outside this amendment.

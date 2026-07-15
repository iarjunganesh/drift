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
- The coverage floor should move toward 99–100% once Scout, persistence,
  retrieval, and Insight behavior are implemented and tested.

## Amendment — 2026-07-15

The implemented fixture and live-grounded-chat paths now run at 100% line
coverage. CI and Codecov enforce a 100% floor. Explicit `NotImplementedError`
boundaries for scheduled Scout persistence, live-store retrieval, and generated
Insight output remain visible and are excluded only until each stage has real
behavior and tests.

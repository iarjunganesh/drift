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

The implemented fixture, live-grounded-chat, and bounded local capture paths
run at a 100% line-coverage floor. CI and Codecov enforce that floor. The
capture job has mocked provider/persistence coverage; scheduled population and
real PostgreSQL integration remain explicit verification boundaries.

## 2026-07-15 addendum — claim-grounding calibration

The 100% implemented-code floor now includes claim-span freezing, verifier
rejection, review publication eligibility, and calibration fixtures for
unsupported facts, ambiguous interpretation, and instruction-shaped source
text. The local suite has 133 passing tests; a real database migration and
human-reviewed provider capture remain external gates.

# ADR-003: Citations and visible uncertainty

**Status:** Accepted  
**Date:** 2026-07-14

## Decision

An insight is invalid unless it carries a primary-source citation, confidence,
an audit/model label, and a bounded `what_to_check` action. The UI must expose
confidence and source links.

## Context

An incorrect breaking-change warning can waste an upgrade cycle or cause an
engineer to make an unsafe change. A fluent explanation without a source is not
useful release intelligence.

## Consequences

- Models must reason over supplied source text rather than provide unsupported
  general knowledge.
- Missing citations or invalid confidence are validation failures.
- `breaking` and `security` remain review priorities, never automation triggers.
- Fixture data must be visibly distinguishable from live analysis.

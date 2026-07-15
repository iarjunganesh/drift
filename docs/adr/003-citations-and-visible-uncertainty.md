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

## Implementation addendum — 2026-07-15

`backend/agents/insight.py` now calls the router-owned structured Responses API
and validates the model-owned fields against a strict schema. Raw-item IDs,
severity, source URLs, and the exact routed model identifier are derived from
trusted pipeline inputs rather than accepted from model output. The generator
is covered with mocked provider tests. The local capture path now persists
source-content hashes, model-run audit metadata, generated Insights, and
optional review notes; the frontend exposes confidence, model/audit labels, and
source links. A reviewed real-model capture remains an operator gate.

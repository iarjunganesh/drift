# ADR-012: Deterministic upstream version-bump classification

**Status:** Accepted — implemented in `v0.10.2` (2026-07-19); applied to the
three affected live Insights the same day
**Date:** 2026-07-19

## Decision

`upstream_release_type` (major/minor/patch/pre_release/unknown) stays a
*declared-or-derived* field, never a model guess:

- The Insight-generation instruction is unchanged: the model may set a value
  other than `unknown` only when the upstream release notes themselves state
  their own release shape. A bare version number is not sufficient — this was
  already correct and is not being loosened.
- A new, separate module, `backend/core/versioning.py`, computes the same
  field a different way when the source is silent: it mechanically diffs a
  release's version tag against the immediately prior tag from the same
  repo's public GitHub feed (major differs → `major`, minor differs →
  `minor`, patch/build differs → `patch`, a prerelease token → `pre_release`).
  This is arithmetic on two primary-source facts, not an inference — the same
  category of operation as computing a claim's character offsets.
- `scripts/backfill_upstream_release_type.py` applies this deterministic
  diff to already-reviewed Insights, dry-run by default, and only ever
  writes when the existing value is `unknown` and the diff resolves to
  something else. It never overwrites an explicit source-stated value.

## Context

Three of the five reviewed Insights (JAX v0.11.0, NCCL v2.30.7-1, TensorRT
11.1) showed `upstream_release_type: unknown` on the live briefing, while two
(Transformers v5.14.1, vLLM v0.25.1) showed `patch`. This looked like an
inconsistency but was not: Transformers's and vLLM's own release notes
literally say "this is a patch release," so the model correctly reported
that. JAX's, NCCL's, and TensorRT's notes describe what changed without
stating their own release shape, so `unknown` was the correct, honest output
under the existing instruction — the model is deliberately forbidden from
inferring a release type from the version number alone, the same category of
guess DRIFT refuses everywhere else.

The real gap was that DRIFT had no fallback for the case where the *version
numbers themselves* could honestly answer the question. The capture that
produced the five reviewed Insights only ever persisted the single latest
release per source (`run_capture`'s default `per_source_limit=1`), so no
prior-version data existed anywhere in the database — the ~72 other release
entries GitHub's feed returned for that capture were fetched but never
stored. Re-running a full capture with a higher limit was rejected: it would
mean new model calls, a new review cycle, and would contradict the "one
bounded capture, not continuous monitoring" boundary this release line has
held since `v0.9.0`.

## Consequences

- `backend/core/versioning.py` is pure, dependency-free, and separately
  tested (`tests/unit/test_versioning.py`, 29 tests, 100% coverage of the
  module) — parsing handles vendor build suffixes (NCCL's `v2.30.7-1`),
  short two-component tags (TensorRT's `v11.1`), and prerelease tokens.
- A real bug was found and fixed while building this: some repos tag more
  than one release line in a single feed (NVIDIA/nccl also tags `nccl4py`),
  so the naive "previous chronological entry" paired NCCL's release with an
  unrelated sub-package's tag. `tag_prefix()` restricts candidates to the
  same product line before diffing.
- The backfill script re-fetches each source's public `releases.atom` feed
  fresh at run time (free, no model call, no new capture) rather than
  reconstructing history from anything persisted — it reads exactly the same
  public data a human could open in a browser.
- Applying the backfill is a direct, transparent data patch to three already
  human-reviewed rows' `upstream_release_type` column — no other column is
  touched, no new claim, citation, or evidence is added, and it does not
  reopen the human-review gate. The three writes (JAX → `minor`, NCCL →
  `patch`, TensorRT → `minor`) were applied 2026-07-19 through the public
  database proxy (`DRIFT_DATABASE_PUBLIC_HOST`/`PORT`), independent of the
  code redeploy.
- Trade-off accepted: this is a one-off script, not yet wired into the
  capture pipeline for future releases. A future capture that hits
  `per_source_limit=1` will still show `unknown` for a release whose notes
  don't self-declare, until this is folded into `backend/agents/insight.py`
  as a standing pipeline stage — deliberately out of scope for `v0.10.2`.

## Scope held

No change to the Insight-generation instruction or schema; no new capture,
model call, or review; no change to any other Insight field; not yet wired
into `backend.pipeline` for future captures.

# DRIFT architecture decision records

These records capture decisions that constrain implementation. They are short
by design; [`../ARCHITECTURE.md`](../ARCHITECTURE.md) explains how the
decisions compose.

| ADR | Decision | Status |
| --- | --- | --- |
| [001](001-fixture-first-judge-path.md) | Fixture-first judge path | Accepted |
| [002](002-typed-agents-no-framework.md) | Typed hand-rolled stages | Accepted |
| [003](003-citations-and-visible-uncertainty.md) | Citations and visible uncertainty are mandatory | Accepted |
| [004](004-local-budget-guard.md) | Local hard budget for live iteration | Accepted |
| [005](005-postgres-pgvector-live-store.md) | PostgreSQL + pgvector for the live store | Accepted; implementation in progress |
| [006](006-ci-quality-gates.md) | CI quality gates and coverage ratchet | Accepted |
| [007](007-vercel-railway-deployment.md) | Vercel frontend + Railway API and database | Accepted; hosted fixture endpoints live, browser CORS verification pending |

When implementation invalidates a decision, amend the original record or add a
new ADR. Do not silently rewrite the decision history in code comments or
README prose.

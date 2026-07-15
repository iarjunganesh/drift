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
| [005](005-postgres-pgvector-live-store.md) | PostgreSQL + pgvector for the live store | Accepted; schema and local retrieval implemented, population pending |
| [006](006-ci-quality-gates.md) | CI quality gates and coverage ratchet | Accepted |
| [007](007-vercel-railway-deployment.md) | Vercel frontend + Railway API and database | Accepted; hosted bounded live chat and browser CORS verified, hosted live-store population pending |
| [008](008-live-grounded-chat.md) | Live grounded chat over the fixture store | Accepted |
| [009](009-bounded-model-resilience-and-locked-delivery.md) | Bounded model resilience and locked delivery | Accepted |

When implementation invalidates a decision, amend the original record or add a
new ADR. Do not silently rewrite the decision history in code comments or
README prose.

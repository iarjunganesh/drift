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
| [005](005-postgres-pgvector-live-store.md) | PostgreSQL + pgvector for the live store | Accepted; Railway schema verified; four human-reviewed Insights published 2026-07-16 with hosted `/briefing`/`/search`/`/chat` verified provider-backed |
| [006](006-ci-quality-gates.md) | CI quality gates and coverage ratchet | Accepted |
| [007](007-vercel-railway-deployment.md) | Vercel frontend + Railway API and database | Accepted; hosted `v0.7.0` health/docs/CORS, review-note redaction, and Vercel `top_n=10` bundle verified; reviewed `/briefing`/`/search`/`/chat` were provider-backed verified on 2026-07-16 |
| [008](008-live-grounded-chat.md) | Live grounded chat over the fixture store | Accepted |
| [009](009-bounded-model-resilience-and-locked-delivery.md) | Bounded model resilience and locked delivery | Accepted |
| [010](010-claim-evidence-and-review-gate.md) | Claim-level evidence, separate verification, and review-first publication | Accepted; `v0.8.0` source makes synthetic fixture evidence verifiable without implying upstream provenance, while four human-reviewed Insights remain the bounded hosted set verified 2026-07-16 |

When implementation invalidates a decision, amend the original record or add a
new ADR. Do not silently rewrite the decision history in code comments or
README prose.

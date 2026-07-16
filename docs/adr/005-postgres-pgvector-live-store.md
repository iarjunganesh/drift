# ADR-005: Postgres and pgvector for the live store

**Status:** Accepted; historical Railway PostgreSQL migration and one
unreviewed hosted capture verified; Railway schema verified at `0003`;
review-gated application/empty briefing verified; hosted `/search`/`/chat`
verification after reviewed evidence pending
**Date:** 2026-07-14

## Decision

The target live path stores raw items and insights in Postgres and stores insight
embeddings with pgvector. The fixture path remains an independent in-memory
store.

## Context

DRIFT needs durable source records, structured insight fields, and semantic
retrieval. A separate vector database would add operational surface before the
product has earned that complexity.

## Rationale

- One durable system can own relational data and vector search.
- Postgres is familiar, inspectable, and easy to run locally with pgvector.
- The fixture path remains dependency-free for judges.

## Consequences

The live path requires async SQLAlchemy wiring, migrations, extension setup, and
integration tests. SQLite is not a substitute for pgvector tests; those tests
must use Postgres or be explicitly skipped when no test database is configured.

## Implementation status

As of 2026-07-15, DRIFT has typed async SQLAlchemy metadata, an async session
dependency, a pgvector-backed `insights.embedding` column, three Alembic
revisions, and local async retrieval that embeds a query and orders rows by
pgvector cosine distance. `backend.pipeline` writes raw-item source hashes,
frozen claim evidence, draft Insights, embeddings, and linked generation/verifier
audit data. `0003_claim_evidence_review_gate` adds claim JSON, review and
verification fields, and a second audit pointer; live reads filter to reviewed
verifier-passed records. On 2026-07-15, the earlier Railway migration and one
unreviewed vLLM capture served through hosted `/briefing` were verified; that
predates `0003`. Railway PostgreSQL was verified through `0003` on 2026-07-16
using its public TCP proxy; later that day hosted `v0.6.1` `/health` and its
empty fail-closed `/briefing` were verified. A reviewed capture corpus and
review-gated hosted `/search`/`/chat` smoke tests remain pending.

# ADR-005: Postgres and pgvector for the live store

**Status:** Accepted; schema and migration foundation implemented, retrieval pending
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
dependency, a pgvector-backed `insights.embedding` column, and an initial
Alembic revision that creates `sources`, `raw_items`, and `insights`. A clean
PostgreSQL upgrade and live-store retrieval integration test remain pending.

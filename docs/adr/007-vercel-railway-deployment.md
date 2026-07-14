# ADR-007: Vercel frontend and Railway API deployment

**Status:** Accepted  
**Date:** 2026-07-14

## Decision

Deploy the Next.js frontend as a Vercel project rooted at `frontend/`. Deploy
the FastAPI backend from the repository root to Railway using the root
`Dockerfile` and `railway.json`. Use Railway PostgreSQL with pgvector for the
live store when that stage is implemented.

The first public deployment must use `DRIFT_MODE=fixture`. Live mode is enabled
only after migrations, provider-boundary tests, provenance persistence, and a
reproducible end-to-end run exist.

## Context

DRIFT has two deployable surfaces with different runtime needs. Next.js is a
natural fit for Vercel's managed frontend runtime, while the FastAPI service
and PostgreSQL need a long-running service boundary and private service-to-
database networking. The project already has a Dockerfile, health endpoint,
Postgres compose service, and a frontend environment variable for the API URL.

The available Railway $5 plan is suitable for a small fixture demo subject to
account limits and usage monitoring. It is not a production reliability or
capacity commitment.

## Consequences

- The browser talks to a Railway HTTPS API through `NEXT_PUBLIC_API_URL`.
- CORS remains explicit through `FRONTEND_ORIGIN`; platform URLs must be set as
  deployment secrets or environment variables.
- Railway's private `DATABASE_URL` stays server-side and is never exposed to
  the frontend.
- Fixture mode can be deployed without OpenAI credentials or a database.
- Vercel and Railway have separate logs, deploys, and usage limits to monitor.
- A future alternative may consolidate the frontend and API, but that would
  require a new ADR because it changes operational boundaries.

## References

- [Railway FastAPI deployment guide](https://docs.railway.com/guides/fastapi)
- [Railway PostgreSQL guide](https://docs.railway.com/databases/postgresql)
- [Vercel Next.js framework guide](https://vercel.com/frameworks/nextjs)

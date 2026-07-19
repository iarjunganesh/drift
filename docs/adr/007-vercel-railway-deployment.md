# ADR-007: Vercel frontend and Railway API deployment

**Status:** Accepted  
**Date:** 2026-07-14

## Decision

Deploy the Next.js frontend as a Vercel project rooted at `frontend/`. Deploy
the FastAPI backend from the repository root to Railway using the root
`Dockerfile` and `railway.json`. Use Railway PostgreSQL with pgvector for the
live store when that stage is implemented.

The public Vercel frontend is `https://dr1ftless.vercel.app`. The Vercel
project must keep `frontend/` as its Root Directory. The checked-in
`frontend/vercel.json` defines the Next.js build and points the public
`NEXT_PUBLIC_API_URL` at the verified Railway API:
`https://drift-api-prod.up.railway.app`. The frontend `package.json` and
`.nvmrc` declare Node.js `24.x`, which Vercel, CI, and the frontend container
use consistently.

The first public deployment used `DRIFT_MODE=fixture`. The current hosted
deployment was switched to bounded `DRIFT_MODE=live` on 2026-07-15 after the
live-chat provider-boundary tests and CORS verification were in place. This
does not establish the current capture-path behavior. The local code now has
migrations, provenance persistence, embeddings, and a one-shot capture job, but
the hosted service needed redeployment and verification before `/briefing` could
be described as review-gated. **2026-07-15 addendum:** `v0.5.1` was migrated
against Railway PostgreSQL and served one bounded, unreviewed vLLM Insight
through `/briefing`; Vercel CORS was reverified. This is not broad live release
analysis or hosted `/search`/`/chat` verification.

**2026-07-15 review-gate addendum:** the local code now requires migration
`0003_claim_evidence_review_gate` and filters live reads to human-reviewed,
verifier-passed records. Railway PostgreSQL was verified at that migration
through its public TCP proxy on 2026-07-16. Later that day, the hosted `v0.6.1`
application passed `/health`, `/briefing`, `/docs`, and Vercel CORS checks; after
four human-reviewed Insights were published, hosted `/briefing`, `/search`, and
`/chat` were verified provider-backed over that reviewed set. The prior populated
pre-gate hosted result remains historical evidence only.

**2026-07-16 brand-assets addendum:**
`assets/brand/drift-banner-dark.svg` and
`assets/brand/drift-banner-light.svg` are the canonical theme-aware brand
banners. The Railway Docker image copies the source pair and FastAPI serves
them at `/brand/dark.svg` and `/brand/light.svg`. **2026-07-16 frontend theme
addendum:** the Vercel frontend renders those API-served canonical files through
a `<picture>` element keyed to `prefers-color-scheme`, and the page palette
follows the same system preference. It does not carry a second frontend copy.
The FastAPI documentation banner frame follows the same light/dark preference.
The Git-connected `v0.6.1` deployment subsequently reported `/health` version
`0.6.1`, an empty fail-closed `/briefing`, and a `200` `/docs`; a Vercel-origin
CORS preflight also passed. The Vercel HTML references the canonical API-served
light/dark banner pair. The amended `v0.6.1` release also makes the API-docs
banner frame follow the same system preference.

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
- CORS remains explicit through `FRONTEND_ORIGIN`; the Railway deployment must
  allow `https://dr1ftless.vercel.app` before hosted browser requests are
  considered verified.
- Railway's private `DATABASE_URL` stays server-side and is never exposed to
  the frontend.
- **2026-07-15 addendum:** accept Railway's native `postgres://` or
  `postgresql://` service reference and normalize it internally to
  `postgresql+asyncpg://`; operators must not construct a connection string
  from individual credential variables.
- Fixture mode can be deployed without OpenAI credentials or a database.
- The verified Railway API endpoint is
  `https://drift-api-prod.up.railway.app`; its public health check is
  `/health`.
- As of 2026-07-15, `FRONTEND_ORIGIN=https://dr1ftless.vercel.app` is verified
  through a successful browser CORS preflight.
- Vercel and Railway have separate logs, deploys, and usage limits to monitor.
- **2026-07-16 v0.7.0 addendum:** the Git-connected Railway deployment reports
  `0.7.0`; `/docs` and Vercel CORS remain available, `/briefing` returns four
  reviewed Insights without `human_review_notes`, and `/openapi.json` omits
  that private field. The production Vercel bundle requests `top_n=10`.
- **2026-07-17 v0.8.0 addendum:** the Git-connected Railway deployment reports
  `0.8.0` at `/health` and serves `/docs` with `200`; the public Vercel page
  renders Ask DRIFT and a Vercel-origin CORS preflight allows `GET, POST`.
  Paid `/search` and `/chat` were not re-invoked for this rollout.
- **2026-07-18 v0.9.1 addendum:** the Git-connected Railway deployment now
  reports `0.9.1` at `/health` and `/` in `DRIFT_MODE=live`; `/docs` returns
  `200`, `/briefing?top_n=10` returns the five reviewed Tier.FINAL Insights
  (10, 11, 13, 15, 16) with no `human_review_notes`, and a Vercel-origin CORS
  preflight allows `GET, POST`. Paid `/search` and `/chat` were not re-invoked.
  The `v0.10.0` MCP source was not yet redeployed at that verification.
- **2026-07-18 v0.10.0 addendum:** later the same day, the Git-connected
  Railway deployment reports `0.10.0` at `/health` and `/` in
  `DRIFT_MODE=live`; `/docs` returns `200`, `/briefing?top_n=10` returns the
  five reviewed Tier.FINAL Insights with no `human_review_notes`, and a
  Vercel-origin CORS preflight allows `GET, POST`. Paid `/search` and `/chat`
  were not re-invoked. The MCP thin client adds nothing to this deployment
  shape (it is a separate credential-free consumer of the same public API).
- A future alternative may consolidate the frontend and API, but that would
  require a new ADR because it changes operational boundaries.

## References

- [Railway FastAPI deployment guide](https://docs.railway.com/guides/fastapi)
- [Railway PostgreSQL guide](https://docs.railway.com/databases/postgresql)
- [Vercel Next.js framework guide](https://vercel.com/frameworks/nextjs)

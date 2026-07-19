# ADR-011: MCP integration as a thin client over the reviewed API

**Status:** Accepted — implemented in `v0.10.0` (2026-07-18); hosted evidence pending  
**Date:** 2026-07-18

> The thin-client MCP integration described here shipped in the source release
> `v0.10.0`. It is implemented in `integrations/mcp/` and verified end-to-end
> against a fixture-mode API at zero cost. The hosted evidence capture and a real
> MCP-client screenshot remain operator gates; no hosted MCP claim is made until
> that capture has run. See the dated implementation addendum below.

## Decision

DRIFT's MCP integration is a **separate thin-client process**, not a backend
feature:

- A new top-level package (`integrations/mcp/`) exposes exactly three MCP tools
  — `drift_briefing`, `drift_search`, and `ask_drift` — each a one-to-one HTTP
  call to the existing public `/briefing`, `/search`, and `/chat` endpoints.
- The server is configured with only `DRIFT_API_URL` (hosted Railway API or a
  local instance), plus an optional `DRIFT_MCP_TIMEOUT_SECONDS` request timeout.
  It holds **no OpenAI key, no database URL, and no credentials of any kind**.
- Transport is stdio via the official `mcp` Python SDK, added as an optional
  dependency group so the core **runtime** dependencies, Docker image, and
  Railway deployment are unchanged. (`uv.lock` does record the optional group so
  `--locked` CI installs resolve it, but `uv sync --no-dev` never installs it —
  see the implementation addendum.)
- Nothing under `backend/` changes. The package lives outside the
  `--cov=backend` / 100% coverage gate; lint and type targets are extended to
  cover it, and it carries its own mocked-HTTP tests.

## Context

The submission freeze plan (an internal planning document, since removed)
classified MCP as optional future work and set a bar: an MCP layer must unlock
a new workflow — release intelligence inside the editor or agent loop — not
merely re-expose the HTTP API. At the same time, DRIFT's
safety story depends on every public read passing through the review-gated
API: human-reviewed, verifier-passed records only, spend guards and budget
caps enforced server-side, review notes never serialized.

Two architectures were considered:

1. **In-process MCP inside the backend** (mount MCP alongside FastAPI, or
   import backend modules directly). Rejected: it would require redeploying
   the hosted service, add a second entry point to the trust boundary, give
   the MCP surface a database URL and provider key, and pull the new code
   under the 100% backend coverage gate days before submission.
2. **Thin client over the public API** (chosen). The MCP server sits on the
   untrusted side of the existing boundary, indistinguishable from any other
   API consumer such as the Vercel frontend.

## Consequences

- Every guarantee the API already enforces — reviewed-only reads, redacted
  review notes, `SpendGuard` budgets, retry/circuit resilience — applies to
  MCP traffic automatically, because there is no second path to the store.
- The MCP server cannot draft, verify, publish, or retract an Insight; the
  review gate remains a human, notebook-driven boundary with no MCP tool.
- Client questions outside the reviewed corpus decline rather than
  hallucinate, inheriting the retrieve-first `/chat` behavior verified in the
  Terra evidence pass.
- Per-question model cost stays bounded and server-accounted (~$0.01–0.03 per
  `ask_drift` call; `drift_briefing` is SQL-only; `drift_search` costs one
  query embedding).
- The hosted deployment, backend version metadata, and 160-test backend suite
  are untouched; the integration is developed and tested entirely against
  `DRIFT_MODE=fixture` at zero cost.
- Trade-off accepted: the MCP layer adds one network hop and cannot offer
  capabilities the public API does not expose. That is intentional — new
  capability requires a reviewed API change first, never an MCP side door.

## Implementation addendum — 2026-07-18

The thin-client MCP integration shipped in the source release `v0.10.0`. This
addendum replaces the transient execution plan with verified facts.

### What shipped

- `integrations/mcp/` — a standalone package on the untrusted consumer side of
  the API boundary. `config.py` reads only `DRIFT_API_URL` (and an optional
  `DRIFT_MCP_TIMEOUT_SECONDS`); `client.py` is a one-to-one async wrapper over
  `/briefing`, `/search`, and `/chat`; `formatting.py` renders the API's JSON
  into assistant-readable text; `server.py` registers the three tools on a
  `FastMCP` server; `python -m integrations.mcp` runs it over stdio.
- Exactly three tools, each a one-to-one call: `drift_briefing` → `GET /briefing`,
  `drift_search` → `GET /search`, `ask_drift` → `POST /chat`. The `/chat` 404
  ("no reviewed evidence") is surfaced as a spoken decline, preserving the
  retrieve-first boundary rather than raising.
- The `mcp` SDK is an optional dependency group; the core `[project.dependencies]`
  set is untouched, so the `uv sync --no-dev` Docker install and the Railway
  runtime install the same packages as before. `uv.lock` carries the optional
  group so `--locked` CI installs resolve it.
- Ruff and mypy targets extend to `integrations/` (`Makefile`, `AGENTS.md`,
  `.github/workflows/ci.yml`). A separate `MCP integration tests` CI job runs the
  suite outside the backend `--cov=backend` gate.

### Verification performed

1. Local ($0): all three tools were exercised against a fixture-mode DRIFT API.
   `drift_briefing` ranked the reviewed examples, `drift_search` matched a
   library query, `ask_drift` returned a grounded cited answer, and an unmatched
   question declined instead of guessing.
2. 40 mocked-HTTP tests at 100% coverage of `integrations/`; the backend suite
   is unchanged at 160 tests / 100% backend coverage.

### Operator gates — status 2026-07-19

- **Hosted evidence (still pending):** one bounded scrubbed capture against the
  live Railway API (briefing, search, and 3–5 `ask_drift` questions,
  ~$0.10–0.25), archived as `assets/evidence/2026-07-XX-mcp-<model>.json` with
  a SHA-256 manifest. Beyond the committed client-side captures, no further
  hosted MCP claim is written until this has run.
- **Client evidence (done, 2026-07-18):** a VS Code MCP client was configured
  against the deployed API with only the public `DRIFT_API_URL`
  (`.vscode/mcp.json`); all three tools were discovered and returned hosted
  `200` responses, and the four captures are committed to the README gallery
  (`assets/screenshots/05.0`–`05.3`, `*-mcp-vscode-*`).
- The deployed application is `v0.10.0` (verified 2026-07-18), and the reviewed
  live store still serves exactly the five Tier.FINAL Insights
  (10, 11, 13, 15, 16).

### Branding boundary (unchanged, still binding)

DRIFT's identity does not change with this release. The tagline ("Release
intelligence for GPU and AI infrastructure. Cited, bounded, inspectable."), the
brand banners, the frontend hero, and the FastAPI description stay as they are.
MCP is presented as a **consumption channel** — additive and subordinate, "in
the browser, over HTTP, and inside your AI assistant" — never as the product
definition. The honest capability statement is "DRIFT's reviewed release
intelligence is also available to any MCP-compatible assistant," and DRIFT stays
the subject of every sentence. Copy that leads with the transport ("the release
intelligence backend that any MCP-compatible assistant can use") is rejected.

### Scope held

No `backend/` change; no new captures or Insights (the tools answer only over the
five reviewed Tier.FINAL Insights and decline otherwise); no IDE extension, no
release timeline, no autonomous agents, no additional providers. New capability
still requires a reviewed API change first, never an MCP side door.

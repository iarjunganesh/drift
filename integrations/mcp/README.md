# DRIFT MCP server — thin client over the reviewed API

A standalone [Model Context Protocol](https://modelcontextprotocol.io) server
that makes DRIFT's reviewed release intelligence available to any
MCP-compatible assistant (Claude Desktop, Cursor, VS Code, Windsurf). It is a
**thin client** over the existing public DRIFT HTTP API — see
[ADR-011](../../docs/adr/011-mcp-thin-client-layer.md).

## Tools

| Tool | Calls | Purpose |
| --- | --- | --- |
| `drift_briefing(top_n=5)` | `GET /briefing` | Ranked reviewed release briefing |
| `drift_search(query)` | `GET /search` | Cited reviewed insights matching a query |
| `ask_drift(question)` | `POST /chat` | Grounded, cited answer — or a decline when nothing in the reviewed corpus matches |

Each tool is a one-to-one call to an existing endpoint. The server can offer
nothing the public API does not.

## No credentials

The server reads only:

- `DRIFT_API_URL` — the DRIFT API root (default `http://localhost:8000`); a
  local fixture instance or the hosted Railway API.
- `DRIFT_MCP_TIMEOUT_SECONDS` — optional HTTP timeout (default `30`).

It holds **no OpenAI key, no database URL, and no credential of any kind**. It
sits on the untrusted consumer side of the API boundary, indistinguishable from
the Vercel frontend. Reviewed-only reads, redacted review notes, spend guards,
and resilience are all enforced server-side; there is no second path to the
store, and no MCP tool can draft, verify, publish, or retract an Insight.

## Run

```bash
# Install the optional SDK group (core install is unchanged)
uv sync --group integrations

# Start a DRIFT API to point at (fixture mode, $0)
uv run uvicorn backend.main:app

# Run the MCP server over stdio
DRIFT_API_URL=http://localhost:8000 uv run python -m integrations.mcp
```

## Client configuration (Claude Desktop)

```json
{
  "mcpServers": {
    "drift": {
      "command": "uv",
      "args": ["run", "--group", "integrations", "python", "-m", "integrations.mcp"],
      "env": { "DRIFT_API_URL": "http://localhost:8000" }
    }
  }
}
```

Cursor (`.cursor/mcp.json`) and other stdio clients use the same shape.

## Tests

Mocked-HTTP only; no test performs a real network call or needs a credential.
Run outside the backend coverage gate:

```bash
make test-integrations
# or
uv run --group integrations pytest integrations -o addopts= --cov=integrations --cov-report=term-missing
```

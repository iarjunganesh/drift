"""Run the DRIFT MCP server over stdio: ``python -m integrations.mcp``.

Configure only ``DRIFT_API_URL`` (the hosted Railway API or a local instance).
No other environment variable is read; the server holds no credentials.
"""

from integrations.mcp.config import settings
from integrations.mcp.server import build_server


def main() -> None:
    settings.validate()
    build_server().run("stdio")


if __name__ == "__main__":  # pragma: no cover
    main()

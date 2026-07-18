"""Configuration for the DRIFT MCP thin client.

The only knob that matters is ``DRIFT_API_URL`` — the hosted Railway API or a
local instance. The server deliberately reads no OpenAI key, database URL, or
any other credential: it is indistinguishable from any other public API
consumer, such as the Vercel frontend.
"""

import os
from dataclasses import dataclass

DEFAULT_API_URL = "http://localhost:8000"
DEFAULT_TIMEOUT_SECONDS = 30.0


@dataclass(frozen=True)
class McpSettings:
    """Resolved MCP client settings.

    Defaults target a local DRIFT instance so the integration can be developed
    and exercised entirely against ``DRIFT_MODE=fixture`` at zero cost.

    The field defaults read the environment at import time, mirroring
    ``backend.core.config.Settings``. That is correct for the stdio CLI process,
    whose environment is fixed before ``python -m integrations.mcp`` starts;
    environment changes made after import do not affect the module-level
    ``settings`` singleton. Construct ``McpSettings(...)`` explicitly (as the
    tests do) to override values after import.
    """

    api_url: str = os.environ.get("DRIFT_API_URL", DEFAULT_API_URL)
    timeout_seconds: float = float(
        os.environ.get("DRIFT_MCP_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS))
    )

    @property
    def base_url(self) -> str:
        """The API root without a trailing slash, so path joins stay exact."""
        return self.api_url.rstrip("/")

    def validate(self) -> None:
        if not self.base_url.startswith(("http://", "https://")):
            raise RuntimeError(
                "DRIFT_API_URL must be an http(s) URL to a DRIFT API instance "
                "(hosted Railway API or a local instance)."
            )
        if self.timeout_seconds <= 0:
            raise RuntimeError("DRIFT_MCP_TIMEOUT_SECONDS must be greater than 0.")


settings = McpSettings()

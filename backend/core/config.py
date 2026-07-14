"""Application configuration.

The app deliberately boots in ``fixture`` mode without credentials so judges can
exercise the product locally. Live ingestion and model generation require an
OpenAI API key and are enabled explicitly with ``DRIFT_MODE=live``.
"""

import os
from dataclasses import dataclass
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    openai_api_key: str = os.environ.get("OPENAI_API_KEY", "")
    database_url: str = os.environ.get(
        "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/drift"
    )
    sources_config_path: str = os.environ.get(
        "SOURCES_CONFIG_PATH", str(REPOSITORY_ROOT / "backend" / "sources.yaml")
    )
    fixture_path: str = os.environ.get(
        "FIXTURE_PATH", str(REPOSITORY_ROOT / "backend" / "fixtures" / "insights.json")
    )
    mode: str = os.environ.get("DRIFT_MODE", "fixture")
    frontend_origin: str = os.environ.get("FRONTEND_ORIGIN", "http://localhost:3000")
    max_spend_usd: float = float(os.environ.get("DRIFT_MAX_SPEND_USD", "10"))
    spend_alert_usd: float = float(os.environ.get("DRIFT_SPEND_ALERT_USD", "5"))
    max_call_usd: float = float(os.environ.get("DRIFT_MAX_CALL_USD", "1"))
    spend_ledger_path: str = os.environ.get(
        "DRIFT_SPEND_LEDGER_PATH", str(REPOSITORY_ROOT / ".drift" / "spend-ledger.json")
    )
    app_name: str = "DRIFT"
    app_version: str = "0.1.0"

    def validate(self) -> None:
        if self.mode not in {"fixture", "live"}:
            raise RuntimeError("DRIFT_MODE must be either 'fixture' or 'live'.")
        if not 0 < self.max_spend_usd <= 10:
            raise RuntimeError("DRIFT_MAX_SPEND_USD must be greater than 0 and no more than 10.")
        if not 0 < self.spend_alert_usd <= self.max_spend_usd:
            raise RuntimeError("DRIFT_SPEND_ALERT_USD must be within the configured budget.")
        if not 0 < self.max_call_usd <= self.max_spend_usd:
            raise RuntimeError("DRIFT_MAX_CALL_USD must be within the configured budget.")
        if self.mode == "live" and not self.openai_api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is required when DRIFT_MODE=live. Copy .env.example "
                "to .env and use a key for this project."
            )


settings = Settings()

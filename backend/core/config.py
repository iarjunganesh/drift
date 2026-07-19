"""Application configuration.

The app deliberately boots in ``fixture`` mode without credentials so judges can
exercise the product locally. Live ingestion and model generation require an
OpenAI API key and are enabled explicitly with ``DRIFT_MODE=live``.
"""

import os
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from dotenv import load_dotenv

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

# Local development uses a gitignored .env file. Existing process environment
# variables win so deployed environments retain their secret-management model.
load_dotenv(REPOSITORY_ROOT / ".env", override=False)


def _normalize_database_url(url: str) -> str:
    # Managed Postgres providers (Railway, Heroku, etc.) hand out plain
    # postgres:// / postgresql:// URLs with no driver hint; SQLAlchemy's
    # async engine needs the +asyncpg dialect explicitly.
    if url.startswith("postgres://"):
        return "postgresql+asyncpg://" + url[len("postgres://") :]
    if url.startswith("postgresql://"):
        return "postgresql+asyncpg://" + url[len("postgresql://") :]
    return url


_DATABASE_HOST = re.compile(r"^[A-Za-z0-9.-]+$")


def _replace_database_endpoint(url: str, host: str, port: str) -> str:
    """Retain private credentials/database while opting into a public TCP proxy."""
    if not host and not port:
        return url
    if not host or not port:
        raise RuntimeError("Set both DRIFT_DATABASE_PUBLIC_HOST and DRIFT_DATABASE_PUBLIC_PORT.")
    if not _DATABASE_HOST.fullmatch(host):
        raise RuntimeError("DRIFT_DATABASE_PUBLIC_HOST must be a hostname, not a URL.")
    try:
        numeric_port = int(port)
    except ValueError as exc:
        raise RuntimeError("DRIFT_DATABASE_PUBLIC_PORT must be a number.") from exc
    if not 1 <= numeric_port <= 65_535:
        raise RuntimeError("DRIFT_DATABASE_PUBLIC_PORT must be between 1 and 65535.")

    parsed = urlsplit(url)
    if not parsed.scheme or not parsed.netloc:
        raise RuntimeError("DATABASE_URL must be a complete database URL.")
    userinfo, separator, _ = parsed.netloc.rpartition("@")
    public_netloc = f"{userinfo}@{host}:{numeric_port}" if separator else f"{host}:{numeric_port}"
    return urlunsplit((parsed.scheme, public_netloc, parsed.path, parsed.query, parsed.fragment))


def _database_url_from_environment() -> str:
    """Resolve a private Railway URL or an explicitly configured public proxy URL."""
    url = os.environ.get(
        "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/drift"
    )
    return _normalize_database_url(
        _replace_database_endpoint(
            url,
            os.environ.get("DRIFT_DATABASE_PUBLIC_HOST", ""),
            os.environ.get("DRIFT_DATABASE_PUBLIC_PORT", ""),
        )
    )


@dataclass(frozen=True)
class Settings:
    openai_api_key: str = os.environ.get("OPENAI_API_KEY", "")
    database_url: str = _database_url_from_environment()
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
    model_timeout_seconds: float = float(os.environ.get("DRIFT_MODEL_TIMEOUT_SECONDS", "20"))
    model_queue_timeout_seconds: float = float(
        os.environ.get("DRIFT_MODEL_QUEUE_TIMEOUT_SECONDS", "2")
    )
    model_max_attempts: int = int(os.environ.get("DRIFT_MODEL_MAX_ATTEMPTS", "3"))
    model_retry_base_seconds: float = float(
        os.environ.get("DRIFT_MODEL_RETRY_BASE_SECONDS", "0.25")
    )
    model_retry_max_seconds: float = float(
        os.environ.get("DRIFT_MODEL_RETRY_MAX_SECONDS", "2")
    )
    model_circuit_failure_threshold: int = int(
        os.environ.get("DRIFT_MODEL_CIRCUIT_FAILURE_THRESHOLD", "3")
    )
    model_circuit_reset_seconds: float = float(
        os.environ.get("DRIFT_MODEL_CIRCUIT_RESET_SECONDS", "30")
    )
    model_max_concurrency: int = int(os.environ.get("DRIFT_MODEL_MAX_CONCURRENCY", "2"))
    scout_timeout_seconds: float = float(os.environ.get("DRIFT_SCOUT_TIMEOUT_SECONDS", "15"))
    scout_max_attempts: int = int(os.environ.get("DRIFT_SCOUT_MAX_ATTEMPTS", "3"))
    scout_retry_base_seconds: float = float(
        os.environ.get("DRIFT_SCOUT_RETRY_BASE_SECONDS", "0.5")
    )
    scout_retry_max_seconds: float = float(
        os.environ.get("DRIFT_SCOUT_RETRY_MAX_SECONDS", "4")
    )
    spend_ledger_path: str = os.environ.get(
        "DRIFT_SPEND_LEDGER_PATH", str(REPOSITORY_ROOT / ".drift" / "spend-ledger.json")
    )
    app_name: str = "DRIFT"
    app_version: str = "0.10.2"

    def validate(self) -> None:
        if self.mode not in {"fixture", "live"}:
            raise RuntimeError("DRIFT_MODE must be either 'fixture' or 'live'.")
        if not 0 < self.max_spend_usd <= 10:
            raise RuntimeError("DRIFT_MAX_SPEND_USD must be greater than 0 and no more than 10.")
        if not 0 < self.spend_alert_usd <= self.max_spend_usd:
            raise RuntimeError("DRIFT_SPEND_ALERT_USD must be within the configured budget.")
        if not 0 < self.max_call_usd <= self.max_spend_usd:
            raise RuntimeError("DRIFT_MAX_CALL_USD must be within the configured budget.")
        if not 0 < self.model_timeout_seconds <= 120:
            raise RuntimeError("DRIFT_MODEL_TIMEOUT_SECONDS must be between 0 and 120.")
        if not 0 < self.model_queue_timeout_seconds <= 30:
            raise RuntimeError("DRIFT_MODEL_QUEUE_TIMEOUT_SECONDS must be between 0 and 30.")
        if not 1 <= self.model_max_attempts <= 5:
            raise RuntimeError("DRIFT_MODEL_MAX_ATTEMPTS must be between 1 and 5.")
        if self.max_call_usd * self.model_max_attempts > self.max_spend_usd:
            raise RuntimeError("DRIFT retry envelope must fit within DRIFT_MAX_SPEND_USD.")
        if not 0 < self.model_retry_base_seconds <= self.model_retry_max_seconds <= 30:
            raise RuntimeError("DRIFT model retry delays must be positive and no more than 30 seconds.")
        if not 1 <= self.model_circuit_failure_threshold <= 10:
            raise RuntimeError("DRIFT_MODEL_CIRCUIT_FAILURE_THRESHOLD must be between 1 and 10.")
        if not 1 <= self.model_circuit_reset_seconds <= 300:
            raise RuntimeError("DRIFT_MODEL_CIRCUIT_RESET_SECONDS must be between 1 and 300.")
        if not 1 <= self.model_max_concurrency <= 20:
            raise RuntimeError("DRIFT_MODEL_MAX_CONCURRENCY must be between 1 and 20.")
        if not 0 < self.scout_timeout_seconds <= 120:
            raise RuntimeError("DRIFT_SCOUT_TIMEOUT_SECONDS must be between 0 and 120.")
        if not 1 <= self.scout_max_attempts <= 5:
            raise RuntimeError("DRIFT_SCOUT_MAX_ATTEMPTS must be between 1 and 5.")
        if not 0 < self.scout_retry_base_seconds <= self.scout_retry_max_seconds <= 30:
            raise RuntimeError("DRIFT Scout retry delays must be positive and no more than 30 seconds.")
        if self.mode == "live" and not self.openai_api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is required when DRIFT_MODE=live. Copy .env.example "
                "to .env and use a key for this project."
            )


settings = Settings()

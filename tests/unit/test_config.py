from dataclasses import replace

import pytest

from backend.core.config import _normalize_database_url, settings


@pytest.mark.parametrize(
    ("provided", "expected"),
    [
        (
            "postgres://user:password@db.internal:5432/drift",
            "postgresql+asyncpg://user:password@db.internal:5432/drift",
        ),
        (
            "postgresql://user:password@db.internal:5432/drift",
            "postgresql+asyncpg://user:password@db.internal:5432/drift",
        ),
        (
            "postgresql+asyncpg://user:password@db.internal:5432/drift",
            "postgresql+asyncpg://user:password@db.internal:5432/drift",
        ),
    ],
)
def test_normalize_database_url_adds_asyncpg_driver_when_needed(
    provided: str, expected: str
) -> None:
    assert _normalize_database_url(provided) == expected


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("mode", "unknown", "DRIFT_MODE"),
        ("max_spend_usd", 0, "DRIFT_MAX_SPEND_USD"),
        ("max_spend_usd", 10.01, "DRIFT_MAX_SPEND_USD"),
        ("spend_alert_usd", 0, "DRIFT_SPEND_ALERT_USD"),
        ("spend_alert_usd", 11, "DRIFT_SPEND_ALERT_USD"),
        ("max_call_usd", 0, "DRIFT_MAX_CALL_USD"),
        ("max_call_usd", 11, "DRIFT_MAX_CALL_USD"),
        ("model_timeout_seconds", 0, "DRIFT_MODEL_TIMEOUT_SECONDS"),
        ("model_queue_timeout_seconds", 31, "DRIFT_MODEL_QUEUE_TIMEOUT_SECONDS"),
        ("model_max_attempts", 6, "DRIFT_MODEL_MAX_ATTEMPTS"),
        ("model_retry_base_seconds", 3, "retry delays"),
        ("model_circuit_failure_threshold", 0, "DRIFT_MODEL_CIRCUIT_FAILURE_THRESHOLD"),
        ("model_circuit_reset_seconds", 301, "DRIFT_MODEL_CIRCUIT_RESET_SECONDS"),
        ("model_max_concurrency", 21, "DRIFT_MODEL_MAX_CONCURRENCY"),
        ("scout_timeout_seconds", 0, "DRIFT_SCOUT_TIMEOUT_SECONDS"),
        ("scout_max_attempts", 6, "DRIFT_SCOUT_MAX_ATTEMPTS"),
        ("scout_retry_base_seconds", 5, "Scout retry delays"),
    ],
)
def test_settings_reject_invalid_budget_configuration(
    field: str, value: object, message: str
) -> None:
    candidate = replace(settings, **{field: value})
    with pytest.raises(RuntimeError, match=message):
        candidate.validate()


def test_live_mode_requires_an_api_key() -> None:
    candidate = replace(settings, mode="live", openai_api_key="")
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        candidate.validate()


def test_retry_envelope_must_fit_project_budget() -> None:
    candidate = replace(
        settings,
        max_spend_usd=1,
        spend_alert_usd=1,
        max_call_usd=1,
        model_max_attempts=2,
    )
    with pytest.raises(RuntimeError, match="retry envelope"):
        candidate.validate()


def test_fixture_settings_are_valid() -> None:
    replace(settings, mode="fixture").validate()

from dataclasses import replace

import pytest

from backend.core.config import settings


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


def test_fixture_settings_are_valid() -> None:
    replace(settings, mode="fixture").validate()

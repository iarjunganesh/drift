import json

import pytest

from backend.core.budget import BudgetExceededError, SpendGuard


def test_spend_guard_reserves_settles_and_blocks_overrun(tmp_path) -> None:
    ledger = tmp_path / "spend-ledger.json"
    guard = SpendGuard(ledger, limit_usd=10, alert_usd=5)

    guard.reserve(4, "embedding batch")
    guard.settle(4, 3.25, "embedding batch")
    guard.reserve(1, "insight")
    guard.reserve(2, "alert-threshold")

    recorded = json.loads(ledger.read_text(encoding="utf-8"))
    assert recorded == {"settled_usd": 3.25, "reserved_usd": 3.0}

    with pytest.raises(BudgetExceededError):
        guard.reserve(6.01, "too-expensive request")


def test_spend_guard_rejects_invalid_costs(tmp_path) -> None:
    guard = SpendGuard(tmp_path / "spend-ledger.json", limit_usd=10, alert_usd=5)

    with pytest.raises(ValueError, match="reservation estimate"):
        guard.reserve(0, "invalid reservation")

    with pytest.raises(ValueError, match="Actual cost"):
        guard.settle(1, -0.01, "invalid settlement")

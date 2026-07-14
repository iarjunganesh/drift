"""A local, conservative spend guard for live OpenAI calls.

The guard uses reservations before a request and settles the recorded cost after
the response. It is intentionally file-backed and single-process: it protects
the hackathon demo workflow, not a horizontally scaled production deployment.
"""

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import structlog

log = structlog.get_logger(__name__)


class BudgetExceededError(RuntimeError):
    """Raised before a model call that would exceed the local budget."""


@dataclass
class SpendLedger:
    settled_usd: float = 0.0
    reserved_usd: float = 0.0


class SpendGuard:
    """Persist and enforce a dollar cap across the live demo's model calls."""

    def __init__(self, path: str | Path, limit_usd: float, alert_usd: float) -> None:
        self.path = Path(path)
        self.limit_usd = limit_usd
        self.alert_usd = alert_usd

    def _read(self) -> SpendLedger:
        if not self.path.exists():
            return SpendLedger()
        return SpendLedger(**json.loads(self.path.read_text(encoding="utf-8")))

    def _write(self, ledger: SpendLedger) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(asdict(ledger), indent=2), encoding="utf-8")

    def reserve(self, estimate_usd: float, operation: str) -> None:
        if estimate_usd <= 0:
            raise ValueError("A reservation estimate must be positive.")
        ledger = self._read()
        projected = ledger.settled_usd + ledger.reserved_usd + estimate_usd
        if projected > self.limit_usd:
            raise BudgetExceededError(
                f"Blocked {operation}: estimated ${estimate_usd:.4f} would exceed "
                f"the ${self.limit_usd:.2f} DRIFT budget (currently ${ledger.settled_usd:.4f} settled)."
            )
        ledger.reserved_usd += estimate_usd
        self._write(ledger)
        if projected >= self.alert_usd:
            log.warning("budget.alert", projected_usd=projected, limit_usd=self.limit_usd)

    def settle(self, reserved_usd: float, actual_usd: float, operation: str) -> None:
        if actual_usd < 0:
            raise ValueError("Actual cost cannot be negative.")
        ledger = self._read()
        ledger.reserved_usd = max(0.0, ledger.reserved_usd - reserved_usd)
        ledger.settled_usd += actual_usd
        self._write(ledger)
        log.info("budget.settled", operation=operation, actual_usd=actual_usd,
                 total_usd=ledger.settled_usd, limit_usd=self.limit_usd)

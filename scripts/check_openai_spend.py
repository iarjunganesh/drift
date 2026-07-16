#!/usr/bin/env python3
"""One-off OpenAI platform verification for DRIFT.

Reports real billed spend from the OpenAI Admin Costs API, grouped by project,
and reconciles it against DRIFT's local spend ledger. Use it to answer one
question: how much of the ~$9 shared OpenAI budget has actually been spent, and
how does that compare to the local guard's `.drift/spend-ledger.json` tally.

This needs a TEMPORARY OpenAI *Admin* key with the `api.usage.read` scope. A
normal project/app key cannot read billing (it returns HTTP 403). The admin key
is read from the OPENAI_ADMIN_KEY environment variable, or from a gitignored
`.env.admin` file at the repository root. Its value is never printed, and this
script only performs read-only GET requests.

Create the key at https://platform.openai.com/settings/organization/admin-keys
and delete it when you are done.

Usage:
    # Option A: environment variable
    OPENAI_ADMIN_KEY=sk-admin-... python scripts/check_openai_spend.py

    # Option B: gitignored file at repo root (.env.admin is ignored by .gitignore)
    echo 'OPENAI_ADMIN_KEY=sk-admin-...' > .env.admin
    python scripts/check_openai_spend.py --days 90

Note: remaining prepaid *balance* and *alert* thresholds are not exposed by the
API. Check those on the dashboard:
    balance -> https://platform.openai.com/settings/organization/billing/overview
    limits  -> https://platform.openai.com/settings/organization/limits
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ADMIN_ENV_FILE = REPO_ROOT / ".env.admin"
LOCAL_LEDGER = REPO_ROOT / ".drift" / "spend-ledger.json"
API_BASE = "https://api.openai.com/v1/organization"


def load_admin_key() -> str:
    """Load the admin key from the environment or a gitignored file, silently."""
    import os

    key = os.environ.get("OPENAI_ADMIN_KEY", "").strip()
    if key:
        return key
    if ADMIN_ENV_FILE.exists():
        for line in ADMIN_ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("OPENAI_ADMIN_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit(
        "No admin key found. Set OPENAI_ADMIN_KEY, or write it to .env.admin as\n"
        "  OPENAI_ADMIN_KEY=sk-admin-...\n"
        "Create one at https://platform.openai.com/settings/organization/admin-keys"
    )


def api_get(path: str, key: str, params: dict[str, object]) -> dict:
    """Perform one read-only Admin API GET and return the parsed JSON body."""
    url = f"{API_BASE}/{path}?" + urllib.parse.urlencode(params, doseq=True)
    request = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", "replace")
        if error.code == 403:
            sys.exit(
                "HTTP 403 from the Admin API. This key lacks the 'api.usage.read' "
                "scope.\nUse an Admin key (sk-admin-...), not a project/app key.\n"
                f"Server said: {body}"
            )
        if error.code == 401:
            sys.exit(f"HTTP 401 — the admin key is invalid or revoked.\nServer said: {body}")
        sys.exit(f"HTTP {error.code} from {path}.\nServer said: {body}")
    except urllib.error.URLError as error:
        sys.exit(f"Network error reaching the OpenAI API: {error.reason}")


def fetch_costs_by_project(key: str, start_time: int) -> dict[str, float]:
    """Sum billed USD per project id across all cost buckets in the window."""
    totals: dict[str, float] = {}
    page: str | None = None
    while True:
        params: dict[str, object] = {
            "start_time": start_time,
            "limit": 180,
            "group_by": "project_id",
        }
        if page:
            params["page"] = page
        payload = api_get("costs", key, params)
        for bucket in payload.get("data", []):
            for result in bucket.get("results", []):
                project_id = result.get("project_id") or "(unattributed)"
                amount = (result.get("amount") or {}).get("value", 0.0) or 0.0
                totals[project_id] = totals.get(project_id, 0.0) + float(amount)
        if payload.get("has_more") and payload.get("next_page"):
            page = payload["next_page"]
            continue
        return totals


def fetch_project_names(key: str) -> dict[str, str]:
    """Best-effort map of project id -> human name; empty if the scope is missing."""
    try:
        payload = api_get("projects", key, {"limit": 100})
    except SystemExit:
        return {}
    return {item["id"]: item.get("name", item["id"]) for item in payload.get("data", [])}


def read_local_ledger() -> float | None:
    """Return the local DRIFT guard's settled USD, or None if no ledger exists."""
    if not LOCAL_LEDGER.exists():
        return None
    try:
        return float(json.loads(LOCAL_LEDGER.read_text(encoding="utf-8")).get("settled_usd", 0.0))
    except (ValueError, OSError):
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--days", type=int, default=90, help="Look-back window in days (default 90).")
    args = parser.parse_args()
    if args.days < 1:
        sys.exit("--days must be at least 1.")

    key = load_admin_key()
    start_time = int(time.time() - args.days * 86_400)

    names = fetch_project_names(key)
    costs = fetch_costs_by_project(key, start_time)

    total = sum(costs.values())
    width = max([len(names.get(pid, pid)) for pid in costs] + [len("TOTAL real spend")])

    print(f"OpenAI real spend - last {args.days} days")
    print("=" * 48)
    if not costs:
        print("No billed usage recorded in this window.")
    else:
        for project_id, amount in sorted(costs.items(), key=lambda kv: kv[1], reverse=True):
            label = names.get(project_id, project_id)
            print(f"  {label:<{width}}  ${amount:>9.4f}")
    print("-" * 48)
    print(f"  {'TOTAL real spend':<{width}}  ${total:>9.4f}")

    ledger = read_local_ledger()
    print()
    print("Reconciliation vs local DRIFT guard")
    print("=" * 48)
    if ledger is None:
        print("  Local ledger: (none found at .drift/spend-ledger.json)")
    else:
        print(f"  Local ledger 'settled_usd' : ${ledger:>9.4f}")
        print(f"  Real spend (all projects)  : ${total:>9.4f}")
        gap = ledger - total
        note = "ledger OVER-counts real spend" if gap > 0 else "ledger under real spend"
        print(f"  Difference (ledger - real) : ${gap:>9.4f}  ({note})")

    print()
    print("Balance & alerts are dashboard-only:")
    print("  balance -> https://platform.openai.com/settings/organization/billing/overview")
    print("  limits  -> https://platform.openai.com/settings/organization/limits")


if __name__ == "__main__":
    main()

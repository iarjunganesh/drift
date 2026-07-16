#!/usr/bin/env python3
"""One-off OpenAI platform verification for DRIFT.

Reports real billed spend from the OpenAI Admin Costs API, grouped by project,
and reconciles the DRIFT project's spend against DRIFT's local spend ledger. The
local guard only tallies DRIFT's own calls, so reconciliation is scoped to a
single explicit project id (`--project-id` / `DRIFT_OPENAI_PROJECT_ID`), not the
organization total; the org-wide breakdown is still printed as context.

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
    python scripts/check_openai_spend.py --days 90 --project-id proj_...

Pass --project-id (or set DRIFT_OPENAI_PROJECT_ID) to reconcile the local ledger
against DRIFT's project spend. Without it, only the org-wide breakdown is shown.

Note: remaining prepaid *balance* and *alert* thresholds are not exposed by the
API. Check those on the dashboard:
    balance -> https://platform.openai.com/settings/organization/billing/overview
    limits  -> https://platform.openai.com/settings/organization/limits
"""

from __future__ import annotations

import argparse
import json
import os
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


def fetch_costs_by_project(
    key: str, start_time: int, *, project_ids: list[str] | None = None
) -> dict[str, float]:
    """Sum billed USD per project id across all cost buckets in the window.

    The Costs API defines `group_by` and `project_ids` as arrays. Passing a
    `project_ids` filter scopes the response to those projects server-side, which
    is how the DRIFT-only reconciliation isolates a single project's spend.
    """
    totals: dict[str, float] = {}
    page: str | None = None
    while True:
        params: dict[str, object] = {
            "start_time": start_time,
            "limit": 180,
            "group_by": ["project_id"],
        }
        if project_ids:
            params["project_ids"] = project_ids
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
    parser.add_argument(
        "--project-id",
        default=os.environ.get("DRIFT_OPENAI_PROJECT_ID") or os.environ.get("OPENAI_PROJECT_ID"),
        help=(
            "DRIFT's OpenAI project id (proj_...) used for ledger reconciliation. "
            "Defaults to $DRIFT_OPENAI_PROJECT_ID or $OPENAI_PROJECT_ID. The local "
            "ledger tracks only DRIFT's spend, so reconciliation needs one project."
        ),
    )
    args = parser.parse_args()
    if args.days < 1:
        sys.exit("--days must be at least 1.")

    key = load_admin_key()
    start_time = int(time.time() - args.days * 86_400)
    drift_project_id = (args.project_id or "").strip() or None

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
        print(f"  Org-wide real spend (context) : ${total:>9.4f}")
    elif drift_project_id is None:
        print(f"  Local ledger 'settled_usd'    : ${ledger:>9.4f}")
        print(f"  Org-wide real spend (context) : ${total:>9.4f}")
        print("  Skipped exact reconciliation: the local ledger tallies only DRIFT's")
        print("  project spend, so it must be compared against that single project —")
        print("  not the organization total. Re-run with --project-id proj_... (or set")
        print("  DRIFT_OPENAI_PROJECT_ID).")
    else:
        drift_spend = sum(fetch_costs_by_project(key, start_time, project_ids=[drift_project_id]).values())
        drift_label = names.get(drift_project_id, drift_project_id)
        gap = ledger - drift_spend
        note = "ledger OVER-counts real spend" if gap > 0 else "ledger at or under real spend"
        print(f"  DRIFT project                 : {drift_label}")
        print(f"  Local ledger 'settled_usd'    : ${ledger:>9.4f}")
        print(f"  DRIFT project real spend      : ${drift_spend:>9.4f}")
        print(f"  Difference (ledger - DRIFT)   : ${gap:>9.4f}  ({note})")
        print(f"  Org-wide real spend (context) : ${total:>9.4f}")

    print()
    print("Balance & alerts are dashboard-only:")
    print("  balance -> https://platform.openai.com/settings/organization/billing/overview")
    print("  limits  -> https://platform.openai.com/settings/organization/limits")


if __name__ == "__main__":
    main()

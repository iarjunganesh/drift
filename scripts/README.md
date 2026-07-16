# scripts/

One-off operational scripts. Not part of the app or the test suite.

## check_openai_spend.py

Reports real billed OpenAI spend (grouped by project) and reconciles **DRIFT's
project spend** against the local `.drift/spend-ledger.json` guard. The local
guard tallies only DRIFT's own calls, so reconciliation is scoped to a single
project id — not the organization total (which is shown separately as context).
Answers: *how much has DRIFT's project actually spent, and how inflated is the
local ledger?*

Requires a **temporary** OpenAI **Admin** key with the `api.usage.read` scope — a
normal project/app key returns HTTP 403. The key value is never printed and only
read-only GET requests are made.

```bash
# Option A: environment variable
OPENAI_ADMIN_KEY=sk-admin-... python scripts/check_openai_spend.py --project-id proj_...

# Option B: gitignored file at repo root (.env.admin is ignored by .gitignore)
echo 'OPENAI_ADMIN_KEY=sk-admin-...' > .env.admin
DRIFT_OPENAI_PROJECT_ID=proj_... python scripts/check_openai_spend.py --days 90
```

Pass `--project-id proj_...` (or set `DRIFT_OPENAI_PROJECT_ID`) to reconcile
against DRIFT's project. Without it, only the org-wide breakdown is printed.

Create the key at <https://platform.openai.com/settings/organization/admin-keys>
and **delete it when done**.

Remaining prepaid *balance* and *alert thresholds* are not exposed by the API —
check those on the dashboard:

- balance — <https://platform.openai.com/settings/organization/billing/overview>
- limits — <https://platform.openai.com/settings/organization/limits>

# scripts/

One-off operational scripts. Not part of the app or the test suite.

## generate_demo_voiceover.py

Generates the nine per-beat narration clips and the continuous reference track
for the submission video (see [`submission/DEMO_SCRIPT.md`](../submission/DEMO_SCRIPT.md))
into [`assets/demo-voiceover/`](../assets/demo-voiceover/), using OpenAI TTS
(`tts-1`, voice `nova` by default). The narration text is embedded verbatim
from the demo script — keep the two in sync.

Reads `OPENAI_API_KEY` from the environment or the gitignored `.env`; the key
is never printed. A full run is ~4.3K input characters ≈ **$0.07** at `tts-1`
rates — a direct provider call outside the DRIFT `SpendGuard`/ledger, and the
DRIFT project must have the TTS model enabled. Existing clips are never
overwritten unless `--force` is passed.

```bash
uv run python scripts/generate_demo_voiceover.py
uv run python scripts/generate_demo_voiceover.py --voice onyx --force
```

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

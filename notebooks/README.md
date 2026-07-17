# DRIFT Manual Run notebook

[`drift_manual_run.ipynb`](drift_manual_run.ipynb) is DRIFT's judge-ready
**Manual Run**: a guided operator workflow for a small, review-first capture
without opening a Railway shell. It calls the same
`backend.pipeline` and `backend.review` functions used by the application; it
does not contain a separate, less-guarded execution path.

From the repository root, create an untracked `.env` with `DRIFT_MODE=live`,
`OPENAI_API_KEY`, and a reachable `DATABASE_URL`, then launch it with:

```powershell
uv run --with jupyterlab jupyter lab notebooks/drift_manual_run.ipynb
```

Apply `alembic upgrade head` once to that database before the first capture.
Railway's native `postgres.railway.internal` database hostname is private to
Railway, so it cannot be used directly from a local notebook. Use local
PostgreSQL or an operator-provided public/tunneled connection string. For a
Railway TCP proxy, keep the complete private `DATABASE_URL` in `.env` and set
`DRIFT_DATABASE_PUBLIC_HOST` plus `DRIFT_DATABASE_PUBLIC_PORT`; the application
preserves the credentials/database name and replaces only the endpoint. Never
place a connection string or API key in the notebook itself.

The notebook starts at one item per configured source (at most eight) on Luna.
It creates verifier-passed **drafts** only. A separate, empty-by-default cell
requires the reviewer to enter the selected IDs and meaningful review notes;
only then can live briefing, search, and chat return those records.

After publication, the notebook has a second empty-by-default archive cell.
It writes the selected reviewed Insights to `assets/evidence/` with capture
counts and frozen claim evidence, omitting review notes and secrets, plus a
SHA-256 manifest. Use a new lowercase dated name for each archive; it refuses
to overwrite an existing record.

## Section 7 — Terra grounded-chat capture

A later section (`## 7. Terra grounded-chat capture`) exercises the same
retrieval and grounded-answer code paths as the live `/chat` endpoint —
`Tier.LIVE` / `gpt-5.6-terra` — against whatever is currently in the
**reviewed** store. It writes nothing to the database: it asks one bounded
question per configured source, and sources without a published Insight are
expected to return no match. This is distinct from the draft-capture pipeline
above (Scout → Synthesizer → draft → verifier), which Terra does not run.
Like the draft capture, it stays paused until `CONFIRM_CHAT_CAPTURE = "RUN"`
is set explicitly.

## Rendered snapshots

[`drift_manual_run.luna.results.ipynb`](drift_manual_run.luna.results.ipynb) and
[`drift_manual_run.sol.results.ipynb`](drift_manual_run.sol.results.ipynb) are frozen,
Markdown-only records of completed draft-capture runs. They have no executable cells,
operator database host, provider/budget logs, or internal review notes. The executable
notebook above is the clean template; keep it output-free when committing, and
create a new results record only from a completed, reviewed run.

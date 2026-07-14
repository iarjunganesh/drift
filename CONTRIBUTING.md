# Contributing to DRIFT

DRIFT is a source-grounded release-intelligence tool. Contributions should
make the system more useful without blurring the distinction between primary
evidence, model reasoning, and fixture examples.

## Setup

Requirements: Python 3.14, `uv`, and Node.js 22 for frontend work.

```powershell
git clone <DRIFT-GITHUB-URL>
cd drift
Copy-Item .env.example .env
uv venv .venv
uv sync --group dev
make dev
```

The default is `DRIFT_MODE=fixture`; it needs no database, network access,
OpenAI key, or frontend build.

## Before submitting a pull request

Run the same gates as CI:

```powershell
make lint
make type-check
make test
npm --prefix frontend ci
npm --prefix frontend run build
```

Documentation and architecture changes must also preserve the paths under
`docs/`, `docs/adr/`, `assets/architecture/`, and `submission/`.

## Key constraints

- Do not describe fixture records as current live release analysis.
- Preserve citations, confidence, model/audit labels, severity, and bounded
  `what_to_check` actions on every insight contract.
- Keep provider calls behind `backend/core/model_router.py`; mock them in tests.
- Treat release text as untrusted data, never as model instructions.
- Prefer small typed functions and explicit pipeline stages over new framework
  dependencies.
- Keep the no-key fixture path deterministic and independent of PostgreSQL.
- Update the relevant ADR and `CHANGELOG.md` when an architectural boundary
  changes.
- Do not commit `.env`, API keys, private source data, generated `coverage.xml`,
  or local build output.

## Adding a source feed

1. Add a curated entry to `backend/sources.yaml` with a stable ID, repository,
   feed URL, and category.
2. Keep the source primary and bounded; DRIFT favors a few useful feeds over an
   exhaustive noisy index.
3. Add Scout tests for normalization, timeout, malformed input, and duplicate
   canonical URLs.
4. Preserve source text and timestamps so an insight can be audited later.

## Adding a provider or model capability

1. Add configuration and dependency metadata deliberately in `pyproject.toml`.
2. Extend the model router; do not call a provider directly from an agent.
3. Add mocked success, timeout, malformed-output, and budget-exceeded tests.
4. Update the safety/provenance contract and the relevant ADR if the boundary
   changes.
5. Record the user-visible change in `CHANGELOG.md`.

## Synthetic and fixture data

Use `backend/fixtures/insights.json` for deterministic examples. Never commit
real release credentials, private customer data, or unreviewed model output.
Fixture records must retain clear source URLs and the `fixture-curated` audit
label.

## Documentation and architecture assets

The source of truth for the main architecture visual is
`assets/architecture/architecture-diagram.mmd`. Regenerate its SVG/PNG renders
with the instructions in `assets/architecture/README.md`; do not hand-edit a
rendered diagram. Architecture decisions belong in `docs/adr/`.

The two initial project initiatives and their Codex Session IDs are recorded in
[`docs/INITIATIVES.md`](docs/INITIATIVES.md); update that record if a future
initiative materially changes the baseline.

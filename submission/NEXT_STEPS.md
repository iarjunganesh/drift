# DRIFT — Focused next steps (audit follow-up, 2026-07-16)

**Deadline:** Devpost submission closes **Tue Jul 21, 5:00 PM PT**. Today is Wed Jul 16 — 5 working days.
**Codex budget:** about 500 of 2,500 credits remain (~20%). Spend it on P0/P1
release and submission work only; do P2 polish by hand where possible.
**OpenAI API budget (separate from Codex credits):** capture runs and hosted smoke tests draw on the `drift` project key, bounded by `DRIFT_MAX_SPEND_USD=10`. That is enough for several capture runs; do not raise the cap.

Audit verdict: hosted `v0.7.0` is verified; the `v0.8.0` source release has
150 tests and 100% backend coverage, verifiable synthetic fixture evidence, and
the grounded Ask DRIFT UI, but must not be called hosted until deployment is
observed. `v0.7.0` includes evidence-byte integrity, public review-note
redaction, and the ten-item frontend request. Railway `/health`/`/docs`, Vercel CORS,
`/briefing` (four records with no review notes), `/openapi.json` (no review-note
field), and the deployed Vercel bundle were checked on 2026-07-16. The
reviewed-output blocker is cleared; the demo video remains the final submission
blocker.

---

## P0 — Blockers (Jul 16–18). Submission fails without these.

### 1. Publish 3–5 human-reviewed live captures  *(unblocks everything else)*
- [x] Ran `notebooks/drift_manual_run.ipynb` against Railway PostgreSQL via the public
      TCP proxy (`DRIFT_DATABASE_PUBLIC_HOST` / `DRIFT_DATABASE_PUBLIC_PORT`).
- [x] Captured one item per source (8 total), tier `dev` (`gpt-5.6-luna`); the demo
      set stayed at `dev` to bound cost, with `final`/Sol reserved.
- [x] Human-reviewed and published Insight IDs 3, 6, 7, 8 via
      `backend.review.publish_verified_insights()` with real review notes.
- [x] Archived the reviewed evidence records + SHA-256 manifest to
      `assets/evidence/2026-07-16-all-sources-reviewed.json`.
- [x] Verified hosted output afterwards (all provider-backed):
  ```
  curl https://drift-api-prod.up.railway.app/briefing        # non-empty
  curl "https://drift-api-prod.up.railway.app/search?q=vllm" # non-empty
  curl -X POST https://drift-api-prod.up.railway.app/chat \
    -H "Content-Type: application/json" \
    -d '{"question":"What should I check for vLLM?"}'        # grounded answer + citations
  ```
- [x] Recorded reviewed-evidence hosted smoke-test results in CHANGELOG (Unreleased).
      Empty-store responses are not evidence of provider-backed retrieval or grounded chat.

### 2. Deploy the reviewed-evidence frontend and redaction fix
- [x] `frontend/app/page.tsx`: separate **loading**, **empty**, and **error**
      states; local `v0.6.1` also renders canonical light/dark API-served
      banners without frontend SVG copies.
- [x] Deployed `v0.7.0` to Railway and Vercel; `/health` reports `0.7.0`,
      `/briefing` and `/openapi.json` omit `human_review_notes`, CORS allows
      Vercel, and the deployed frontend requests `top_n=10`.

### 3. Record and publish the demo video  *(≤ 3 min, public YouTube, English voiceover)*
- [ ] Follow `submission/DEMO_SCRIPT.md`, updated for the now-populated hosted app:
      lead with real reviewed insights, the claim-evidence panel, and grounded chat.
- [ ] Show the Codex interface on screen at least once (strengthens Technical
      Implementation per Devpost guidance).
- [ ] Narration must explicitly cover: what DRIFT does, how **Codex** built it,
      how **GPT-5.6** is integrated (claim extraction + separate verifier + chat).
- [ ] Replace `https://youtu.be/TBD` in README.md, `submission/SUBMISSION.md`,
      and `submission/DEMO_SCRIPT.md`.

---

## P1 — High leverage (Jul 18–19). Largest scoring uplift per hour.

### 4. Restructure README top (Potential Impact / first impression)
- [x] First screen: problem → what DRIFT does → live demo links (now showing real
      content) → 60-second judge path (`docker compose up` + hosted URLs).
- [x] Move the boundary/disclaimer material lower and reframe it as the trust
      model — "release notes are untrusted input; every claim carries a frozen
      source span, a separate verifier pass, and a human review gate" — not as
      an apology.
- [x] Keep the Codex/GPT-5.6 usage section prominent (judges are told to look for it).

### 5. Add a minimal grounded-chat box to the frontend (Design)
- [x] One component (`AskDrift`) against the retrieve-first `/chat` endpoint;
      shows the grounded answer with source citations. The separate `/search`
      endpoint remains available in the API rather than duplicating live
      retrieval in the browser. This is the single biggest demo-video uplift.
- [x] If credits run short, cut this before cutting anything in P0.

### 6. Cross-platform judge path
- [x] Add bash/curl equivalents beside every PowerShell command in Quick Start
      (judges will likely test on macOS/Linux).
- [x] Promote `docker compose up` as the one-command local path.

---

## P2 — Polish (Jul 20). Hand-edit; do not spend Codex credits here.

- [x] README quality result — updated to 150 tests after a verified pytest run.
- [x] README clone URL — replaced `git clone <DRIFT-GITHUB-URL>` with:
      `https://github.com/iarjunganesh/drift.git`.
- [x] Scrubbed `bankers-wrapped` references from public surfaces:
      `backend/main.py` docstring, `.env.example`, `docs/CODEX_PROMPTS.md` intro.
- [x] Give the 3 fixture records `claims` arrays so the "Inspect claim evidence"
      panel renders in no-key mode; retitle them to read like realistic examples
      (still labelled fixtures), then backed them with checked-in synthetic
      source text and an integrity regression test. Validated against the
      `Insight` model; 150 tests still pass at 100% coverage.
- [x] Enable branch protection requiring the CI quality gate (main: 5 required
      checks — Ruff lint, Mypy type check, Tests and coverage, Frontend build,
      Documentation hygiene; strict up-to-date; admins retain bypass).
- [x] Confirm the Codecov `pytest` upload appears on the dashboard (tokenless
      OIDC upload queued and processed; repo and `flag=pytest` badges both 100%).

---

## Submission form (Jul 20, submit a day early — no edits allowed after close)

- [ ] Category: **Developer Tools** (single track).
- [ ] Text description: adapt the restructured README top.
- [ ] Video URL: final public YouTube link.
- [ ] Repo URL: `https://github.com/iarjunganesh/drift` (public, MIT — already verified).
- [ ] Primary `/feedback` Session ID: `019f62b9-10b7-7d82-a463-e6eb1192141c`
      (all 10 initiative IDs stay documented in README/`docs/INITIATIVES.md`).
- [ ] Judge testing path: hosted frontend + API links, plus `docker compose up`.
- [ ] Re-run the "Do not claim until verified" checklist in `SUBMISSION.md` —
      after P0 lands, most of those claims become safely claimable.

## Credit allocation guide (750 remaining)

| Work | Credits |
| --- | --- |
| P0.1 notebook run support / capture debugging | ~150 |
| P0.2 frontend empty state + redeploy | ~75 |
| P1.4 README restructure | ~100 |
| P1.5 chat/search UI component | ~200 |
| P1.6 cross-platform Quick Start | ~50 |
| Reserve for video-day fixes and re-verification | ~175 |

If anything overruns, protect the reserve — a working demo on video beats one more feature.

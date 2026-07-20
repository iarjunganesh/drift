# Demo Video — Shooting Script (≤ 3 min)

> **Target 2:50–2:55** (hard cap 3:00) · public on YouTube · **no copyrighted
> music** · 1080p screen capture.
> Four OBS recordings, not one — two short **paid** takes (each Ask is a real
> `gpt-5.6-terra` call, ~$0.01 per question based on the archived Terra run:
> ~$0.076 across eight questions) and two **free** takes (Codex session +
> main take) you can redo endlessly. The edit assembles clips from all four
> under a separately recorded narration track.
> **Published:** `https://youtu.be/6sbIz0ZR8Hw` — set in the README and
> submission documents.

**Every criterion is earned on screen** — the mapping to the Devpost stage-two
criteria:

| Beat | Criterion it scores |
| --- | --- |
| Cold open on a real release + bounded `what_to_check` cards | Potential Impact (real problem, specific audience) |
| Claim-evidence panel · grounded Ask · the decline | Quality of the Idea (evidence-bounded grounding, refusal over guessing) |
| Architecture diagram · Codex + GPT-5.6 narration · 200 tests / 100% coverage | Technological Implementation (hard requirement: narration must cover **both** Codex and GPT-5.6 — carried by `vo_05` and `vo_08`) |
| Landing hero · briefing cards · Ask DRIFT UX · MCP inside VS Code | Design (complete product experience, not a proof of concept) |

---

## Why four recordings

Live `/chat` answers take a few seconds to render and each one costs real
money. Sitting through that inside one continuous take risks awkward pauses
and paid retakes of everything. Instead:

- **Recording #1 — Ask DRIFT Live (paid)**: one short take capturing the two
  real chat calls — the grounded NCCL answer and the Kubernetes decline.
  Retakes are cheap (~$0.01 per ask) but bounded: keep spend-guard headroom
  for 4–6 calls total including rehearsal.
- **Recording #2 — VS Code MCP (paid)**: one short take of the `ask_drift`
  tool call against the hosted API, plus the MCP server log. One paid call.
- **Recording #3 — Codex Session (free)**: a real Codex session, scrolled
  through for beat 10. No provider calls, just viewing history, redo freely.
- **Recording #4 — Main Take (free)**: everything else — release-note scroll,
  landing hero, `/health`, briefing cards, claim evidence, citation
  click-through. No provider calls, redo freely — record this last, right
  before assembly, since it's the biggest take and the one most likely to
  need a reshoot.

**Shared OBS settings for all four** — Base + Output **1920×1080**, **30 fps**,
cursor **visible**; Display Capture (or Window Capture of the browser);
**microphone OFF and speakers/system audio OFF** for every take. Nothing in
DRIFT autoplays audio, so all four takes are pure silent visual capture; the
narration is the pre-generated OpenAI TTS `vo_NN` clips
(`assets/demo-voiceover/`), laid under the picture in the editor.

**Mouse discipline** — move deliberately, click confidently, pause on anything
a judge should read. No rapid scrolling, no hovering, no repeated
tab-switching.

**Theme discipline** — pick dark **or** light and keep it for every take, then
use the matching `-dark`/`-light` card variants in the editor.

---

## Step 0 — one-time prep, before recording anything

1. **Verify the hosted state fresh**: `GET /health` must return
   `{"status":"ok","mode":"live","version":"0.10.2"}` — this exact JSON is
   filmed in Recording #4.
2. **Pre-warm `/chat` once off camera** so the first on-camera ask does not
   absorb cold-start latency. Confirm spend-guard headroom for 4–6 paid calls.
3. **Pre-test the Kubernetes decline off camera.** On the hosted live path,
   retrieval has no distance cutoff, so the decline may arrive as a *spoken*
   answer that cites nothing (like the archived PyTorch decline) rather than
   the frontend's "No matching insights" state (fixture mode's 404). **Both are
   the boundary working** — record whichever form actually occurs and narrate
   it as a decline. If the spoken form is visually weak, plan a zoom on the
   absence of citations. (Confirm no stray "Source" links render alongside a
   decline — `backend/main.py` no longer falls back to citing every retrieved
   insight when the model reports zero `grounded_insight_ids`.)
4. **Editor cards are already built** — opening/closing card
   `assets/brand/drift-banner-light-1920x1080.png`, architecture cards
   `assets/architecture/arch-light-1920x1080.png` and
   `assets/architecture/arch-pipeline-light-1920x1080.png`, and two repo
   screenshots: `assets/screenshots/00-drift-github-repo.png` (README view —
   banner, badges, "The Problem," "What DRIFT Does" — for beat 1) and
   `assets/screenshots/00-drift-github-repo-tree.png` (file-tree/About
   view — Public badge, MIT license, live Deployments — for beat 4). All
   five are plain RGB, true 1920×1080 (no alpha channel, no corrupted `pHYs`
   metadata — both caused a black-import bug in Clipchamp) — use these exact
   files, not the raw `arch-{dark,light}.png` / `drift-banner-{dark,light}.png`
   brand-asset originals. No live OBS scroll of the GitHub repo is needed for
   either beat. These are inserted directly in the editor as images — **do
   not record them in OBS** (browser chrome would show).
5. **Generate the narration with OpenAI TTS** (explicitly allowed by the
   rules: "text-to-speech and AI narration tools are acceptable"): run
   `uv run python scripts/generate_demo_voiceover.py` — the eleven `vo_NN`
   clips plus a full reference track go to `assets/demo-voiceover/`
   (`tts-1`, voice `nova`, ~$0.08; a direct provider call outside the DRIFT
   spend guard — see `assets/demo-voiceover/README.md`). Measure each clip's
   real length before the edit.
6. Clean browser profile, 100% zoom (bump to 110% if card text reads small at
   1080p), bookmarks bar hidden, notifications off, no personal tabs.
7. VS Code: only the `drift` MCP server configured, unrelated panels and
   repos closed, editor font ≥ 14.
8. Nothing sensitive anywhere on screen: no `.env`, keys, database URLs,
   private Railway URLs, spend ledger, or local paths with usernames.

---

## Recording #1 — Ask DRIFT Live (paid — record this first, by itself)

1. Open `https://dr1ftless.vercel.app`, scrolled to the **Ask DRIFT** box,
   nothing typed yet.
2. Start OBS recording.
3. Type naturally (typing reads as authentic — don't paste):
   `What operator checks are recommended for the NCCL release?`
4. Click **Ask**. Leave the cursor still while it loads.
5. When the grounded answer renders, hold ~6s: the answer text, the
   **Source** link, the `gpt-5.6-terra` model label, and the grounded insight
   ID must all be on screen.
6. Clear the box and type: `What changed recently in Kubernetes?`
7. Click **Ask**. Hold ~5s on the decline (either honest form — see Step 0.3).
8. Stop OBS recording. Save as `ask-drift-take.mp4`.

This is the take that spends money — but at ~$0.01 per ask, a bad take is
re-recordable. Never splice fixture output in as a substitute for a live
answer.

---

## Recording #2 — VS Code MCP (paid — one tool call)

1. Open VS Code with the agent chat visible and the `drift` MCP server
   already connected.
2. Start OBS recording.
3. In the agent chat, ask:
   `Use ask_drift: What operator checks are recommended for the NCCL release?`
4. Let the tool call run visibly — the `ask_drift` invocation line and the
   returned answer must both appear.
5. Switch to the MCP server output/log panel: hold ~4s where the three
   discovered tools (`drift_briefing`, `drift_search`, `ask_drift`) and the
   hosted `200` responses are visible.
6. Stop OBS recording. Save as `mcp-take.mp4`.

---

## Recording #3 — Codex Session (free — no API cost, just viewing history)

Not a hard Devpost requirement, but showing the real Codex interface
strengthens the Technological Implementation score per the official FAQ.

1. Open VS Code's Codex tab.
2. Click into the real session `019f62b9-10b7-7d82-a463-e6eb1192141c` (the
   primary `/feedback` session cited in `submission/SUBMISSION.md`) — not the
   sessions list, the actual session content.
3. Start OBS recording (same settings: 1920×1080, 30fps, cursor visible,
   mic/system audio off).
4. Scroll slowly through a stretch that shows real code, diffs, or file
   changes — no need to read every line, just let it be visibly real work.
   ~4-5 seconds is enough.
5. Stop OBS recording. Save as `codex-session-take.mp4`.

---

## Recording #4 — Main Take (free — one continuous take)

Open these tabs before you start, arranged so you can switch quickly:

| Label used below | What it actually is | What to have on screen before recording |
| --- | --- | --- |
| **NCCL Release** | The real NCCL v2.30.7-1 GitHub release page | Scrolled to the top of the release notes |
| **JAX Release** | The real JAX v0.11.0 GitHub release page | Top of the release notes |
| **Live App** | The DRIFT Vercel frontend | `https://dr1ftless.vercel.app`, fresh hero, nothing clicked |
| **Health JSON** | The hosted API health endpoint | `https://drift-api-prod.up.railway.app/health` showing `{"status":"ok","mode":"live","version":"0.10.2"}` |
| **Codecov Coverage** | The real, public Codecov dashboard for this repo | `https://app.codecov.io/github/iarjunganesh/drift?search=&trend=7%20days`, loaded and settled before recording |

The GitHub repo itself is **not** an OBS tab — beats 1 and 4 use the
`00-drift-github-repo.png` / `00-drift-github-repo-tree.png` editor images
instead (see Step 0.4), so there's no live scroll of the repo page to
capture.

Now start OBS recording once, and go through these in order without stopping:

1. **On NCCL Release**: slowly scroll down through the release notes. Don't
   click anything. Hold for about 14 seconds.
2. **Switch to JAX Release**: brief slow scroll, ~5 seconds.
3. **Switch to Live App**: sit on the hero — "Know what changed before it
   becomes your incident." — no clicks. Hold ~6 seconds.
4. **Switch to Health JSON**: hold ~4 seconds on the version/mode JSON.
5. **Back to Live App**: click **View today's briefing**. Let the five
   reviewed cards render, then scroll slowly through them. Pause ~8 seconds on
   the NCCL card so its severity, confidence, `gpt-5.6-sol` model label, and
   `what_to_check` are all readable.
6. Expand **Inspect claim evidence** on the NCCL card. Hold ~8 seconds on the
   frozen excerpt and the `direct_fact` / `inference` / `recommended_check`
   labels.
7. Click the source citation. The GitHub release opens — hold ~4 seconds on
   the matching text, then navigate back.
8. **Switch to Codecov Coverage** (last tab): no clicks, hold ~5 seconds on
   the real coverage percentage/trend. This backs the "two hundred tests, one
   hundred percent coverage" line in `vo_08-pipeline` with actual evidence
   instead of an unbacked spoken claim.
9. Stop OBS recording. Save as `main-take.mp4`.

---

## Narration — the eleven `vo_NN` scripts

~418 words total, **measured ~2:40 narration spine**. All eleven clips are
generated at `assets/demo-voiceover/` (`tts-1`, voice `nova`); lengths below
are measured from the generated MP3s. `vo_00-repo-intro` opens with DRIFT's
name and tagline (it's now the first spoken line of the whole video, right
after the silent banner), so `vo_02-reveal` was rewritten to drop the
redundant second introduction and just transition into "it's live" — no
double-naming DRIFT. Word counts are the budget: do not add words without
removing others, and regenerate the clips after any wording change.

| Clip | Words | Length | Script |
| --- | --- | --- | --- |
| `vo_00-repo-intro` | 60 | 21.8s | "DRIFT. Release intelligence for GPU and AI infrastructure — cited, bounded, inspectable. Real repo, real CI, real coverage — not slides. The problem: GPU and AI platforms move fast — PyTorch, vLLM, NCCL — and the line that matters gets buried in release notes. DRIFT turns that noise into one engineer-ready answer: what changed, why it matters, what to check." |
| `vo_01-hook` | 29 | 10.2s | "This is a real NCCL release — dozens of changes: dropped plugin APIs, new collective paths, new flags. Somewhere in here is the line that matters to your cluster." |
| `vo_02-reveal` | 20 | 6.6s | "Here it is, live — not a mockup. Hosted right now, answering with real reviewed insights over the public API." |
| `vo_02b-repo-revisit` | 18 | 6.6s | "Before we get started — here's the DRIFT repo. Open source, MIT licensed, real CI, real coverage, all live." |
| `vo_03-briefing` | 50 | 20.2s | "Today's briefing holds five human-reviewed, verifier-passed insights — a bounded set, not a firehose. JAX dropping Python and NumPy versions, TensorRT's CUDA defaults, vLLM, Transformers, NCCL. Each card is a decision: severity, confidence, the exact model that drafted it, and one bounded thing to check before production moves." |
| `vo_04-evidence` | 45 | 17.2s | "Every claim stays inspectable: a frozen excerpt of the primary source, with character offsets and a source hash. Click the citation — you land on the release itself. Facts, inferences, and recommended checks are labelled separately, so you audit the reasoning instead of trusting it." |
| `vo_05-ask` | 47 | 17.9s | "Now ask it a real question: what should an operator check for this NCCL release? DRIFT retrieves matching reviewed evidence first; then GPT-5.6 writes the answer over that evidence and cites only what it actually used. Concrete checks, a source link, the model named on screen." |
| `vo_06-decline` | 24 | 9.4s | "Ask about something outside the reviewed corpus — Kubernetes — and DRIFT declines. No guess, no fabricated citation. That refusal is the product working." |
| `vo_07-mcp` | 51 | 18.3s | "Since version 0.10.0, the same intelligence follows you into your editor. A thin MCP client exposes three tools over the same public API — no key, no database access, no write path — so the review gate and budgets stay server-side. Here's VS Code asking DRIFT for NCCL checks, live." |
| `vo_08-pipeline` | 57 | 23.9s | "Under it all is a typed pipeline, built with Codex. Scout reads primary feeds; claims freeze their source spans; a separate GPT-5.6 verifier screens every draft; and a human must review before anything publishes. GPT-5.6 powers synthesis, verification, and grounded chat; Codex shaped the stages, safeguards, and tests — two hundred tests, one hundred percent coverage." |
| `vo_09-close` | 21 | 7.9s | "DRIFT. Release intelligence for GPU and AI infrastructure — cited, bounded, inspectable. The briefing is live — go ask it something." |

---

## Final beat timeline

| # | Beat | VO clip | Source | Screen action | Overlay (lower-third) | Duration | Ends at |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | Opening flash | none (silent) | editor image (`assets/brand/drift-banner-light-1920x1080.png`) | Brief logo hold, no URL text, cut straight to beat 1 | none | 2s | 0:02 |
| 1 | **NEW** — Repo cold open: DRIFT name/tagline, badges, Problem, What DRIFT Does | `vo_00-repo-intro` (21.8s measured) | editor image (`assets/screenshots/00-drift-github-repo.png`) | Slow Ken Burns pan/zoom top→bottom: hero/badges → "The Problem" → "What DRIFT Does", timed to narration | `github.com/iarjunganesh/drift` | 22s | 0:24 |
| 2 | Cold open — real release | `vo_01-hook` | Recording #4 — NCCL Release scroll, cut to JAX Release | Slow scroll of real release notes, no branding yet | `Which line breaks your rollout?` | 12s | 0:36 |
| 3 | It's live | `vo_02-reveal` (6.6s measured) | Recording #4 — Live App hero, then Health JSON | Hero hold 3s → `/health` JSON with `0.10.2` / `live` | `drift-api-prod.up.railway.app/health · v0.10.2 · live` | 14s | 0:50 |
| 4 | **NEW** — Repo quick revisit | `vo_02b-repo-revisit` (6.6s measured) | editor image (`assets/screenshots/00-drift-github-repo-tree.png`) | Brief hold/gentle zoom on the Public badge, MIT license, and live Deployments in the sidebar | `MIT · open source · live` | 7s | 0:57 |
| 5 | Briefing — five reviewed cards | `vo_03-briefing` | Recording #4 — briefing scroll + NCCL card pause | Cards render, slow scroll, zoom (105–110%) on severity / confidence / `gpt-5.6-sol` / `what_to_check` | `5 reviewed insights · human gate · gpt-5.6-sol` | 26s | 1:23 |
| 6 | Claim evidence + citation | `vo_04-evidence` | Recording #4 — Inspect claim evidence + source click | Frozen excerpt + claim labels, citation click → GitHub release **held ≥ 2s** → back | `Frozen span · offsets · SHA-256` | 22s | 1:45 |
| 7 | Ask DRIFT — grounded answer | `vo_05-ask` | Recording #1 — NCCL question | Typing → Ask → jump-cut the wait to ≤ 1.5s (keep the request visibly sent) → answer, Source link, `gpt-5.6-terra`, grounded ID | `Retrieve first → GPT-5.6 Terra → cited answer` | 26s | 2:11 |
| 8 | The decline | `vo_06-decline` | Recording #1 — Kubernetes question | The decline in whichever honest form occurred; zoom on absent citations if spoken form | `Out of corpus → decline, not a guess` | 14s | 2:25 |
| 9 | MCP in VS Code | `vo_07-mcp` | Recording #2 — tool call, then server log | `ask_drift` invocation + answer, brief cut to log: three tools, hosted `200`s | `drift_briefing · drift_search · ask_drift — DRIFT_API_URL only` | 24s | 2:49 |
| 10 | Architecture + Codex/GPT-5.6 | `vo_08-pipeline` | Recording #3 — Codex sessions list, cut to real session content ("built with Codex"); then editor images `arch-light-1920x1080.png` → `arch-pipeline-light-1920x1080.png`; Recording #4 — Codecov Coverage hold | Codex sessions list (brief) → real session content (diffs, tests, coverage); pan/zoom on the branded overview card, cut to a left→right pan across the six-stage pipeline diagram; quick cut to the real Codecov 100% coverage dashboard timed to "two hundred tests, one hundred percent coverage" | `Untrusted → verifier → human gate → trusted` | 26s | 3:15 |
| 11 | Close | `vo_09-close` | editor image (`assets/brand/drift-banner-light-1920x1080.png`) | Banner hold, fade in both URLs | `dr1ftless.vercel.app · drift-api-prod.up.railway.app` | 10s | 3:25 |

**These per-beat durations are budgets, not the exact final cut.** The
published video came in at **2:45** in `assets/demo-videos/drift.mp4`,
frame-by-frame verified against every beat above — correct beat order
(cold open → hero → Health JSON → repo revisit → briefing), the Codex
sessions-list-then-real-content cut, the two-diagram architecture split, the
Codecov beat, and the closing URL fade-in are all confirmed present and in
place. Final published URL: **<https://youtu.be/6sbIz0ZR8Hw>**.

---

## Assembly (Clipchamp on Win11, or CapCut)

You'll end up with 5 image files (`drift-banner-light-1920x1080.png` — used
twice, opening and closing — `00-drift-github-repo.png`,
`00-drift-github-repo-tree.png`, `arch-light-1920x1080.png`, and
`arch-pipeline-light-1920x1080.png`) and 5 video files (`main-take.mp4`,
`new_ask-drift-take.mp4`, `mcp-take.mp4`, `codex-session-1-take.mp4`,
`codex-session-2-take.mp4`). Build the final video in this order:

0. `drift-banner-light-1920x1080.png` (image; ~2s hold, no URL text — cut
   straight to clip 1, no transition needed)
1. `00-drift-github-repo.png` (image; slow Ken Burns pan/zoom top→bottom over
   the badge row, "The Problem," and "What DRIFT Does" — pairs with
   `vo_00-repo-intro`; don't hold it flat-static for the full 22s)
2. From **main-take.mp4**: the NCCL Release scroll, quick cut to the JAX
   Release scroll
3. From **main-take.mp4**: the Live App hero clip, then the Health JSON clip
4. `00-drift-github-repo-tree.png` (a different shot than clip 1 — file
   tree, About section, Public badge, MIT license, live Deployments; gentle
   zoom on the sidebar — pairs with `vo_02b-repo-revisit`)
5. From **main-take.mp4**: the briefing-cards clip (add the zoom push-in here)
6. From **main-take.mp4**: the claim-evidence clip through the citation
   click-through and back
7. From **new_ask-drift-take.mp4**: the NCCL question — trim the load wait to
   ≤ 1.5s with a jump cut, keeping the click on **Ask** and the answer render
8. From **new_ask-drift-take.mp4**: the Kubernetes decline
9. From **mcp-take.mp4**: the tool call, then the server-log clip
10. From **codex-session-1-take.mp4**: a brief glimpse of the sessions list,
    cut to **codex-session-2-take.mp4** for real session content (diffs,
    tests, coverage) right as the narration says "built with Codex" — then
    `arch-light-1920x1080.png` (image; pan/zoom on the branded overview card)
    cut to `arch-pipeline-light-1920x1080.png` (image; slow left→right pan
    across the six-stage pipeline) for the pipeline-stages narration, then
    from **main-take.mp4**: the Codecov coverage-dashboard hold, cut in on "two
    hundred tests, one hundred percent coverage"
11. `drift-banner-light-1920x1080.png` (same file as clip 0; image, fade in
    the two URLs)

Then drop the eleven `vo_NN` narration clips onto the audio track underneath,
matching each to its beat (clip 0 stays silent — no VO). All picture is
silent otherwise, so there is nothing to duck.

Edit rhythm: cut on clicks; one zoom per beat, max; overlays are one line, on
screen ≤ 4s. Watch the final cut once with audio off (the story must survive
on picture alone), then once with video off (the narration must survive
alone). Both must pass.

---

## Honesty rules (unchanged from the release boundary)

- The main story runs on the hosted API so the version and reviewed boundary
  are visible. Never present fixture records as fresh live analysis, and never
  splice fixture output into a live beat.
- Five reviewed insights, one bounded capture — never imply continuous
  monitoring, broad release completeness, or autonomous infrastructure
  changes.
- The verifier is model-aided screening, not proof; the human gate publishes.
- Any GPT-5.6 claim must be backed by the saved reviewed evidence; Codex's
  contribution is narrated as it actually happened (typed stages, safeguards,
  tests, delivery path).

---

## Production checklist

- [x] Record at 1920×1080, 30 fps; clean profile; bookmarks/personal tabs
      hidden; one theme (dark or light) across every take and card. Verified
      via `ffprobe`: 1920×1080, 30fps h264; light theme consistent across
      every frame checked.
- [x] `GET /health` shows `0.10.2` / `live` on shoot day (Step 0.1). Verified
      on screen in the Health JSON beat: `{"status":"ok","mode":"live",
      "version":"0.10.2"}`.
- [ ] `/chat` pre-warmed and the Kubernetes decline pre-tested off camera
      (Step 0.2–0.3); spend-guard headroom confirmed for 4–6 paid asks. Not
      independently verifiable after the fact — this is an off-camera prep
      step; the on-camera result (clean grounded answer, clean decline with
      no stray citations) is consistent with it having been done.
- [x] Recording #1 and #2 done (paid, ~$0.01 per ask); Recordings #3 and #4
      can be redone freely. Confirmed present in the final cut: Ask
      DRIFT/decline (#1) and MCP tool call/server log (#2).
- [x] Eleven `vo_NN` clips generated (OpenAI TTS, `assets/demo-voiceover/`,
      including the two new `vo_00-repo-intro` / `vo_02b-repo-revisit`) and
      measured; narration covers **both**
      Codex and GPT-5.6 (`vo_05`, `vo_08`) — hard Devpost requirement.
- [x] `00-drift-github-repo.png` (beat 1) and `00-drift-github-repo-tree.png`
      (beat 4) inserted with Ken Burns pan/zoom (not a flat static hold) —
      mandatory per the updated beat timeline; no live GitHub repo capture
      needed in Recording #4. Confirmed: real pan/zoom motion visible
      between frames, not a static hold.
- [x] Cards inserted in the editor, never filmed in OBS. Confirmed: every
      image beat shows clean cards with no browser chrome.
- [ ] Live-call waits jump-cut to ≤ 1.5s, with the request visibly sent. Not
      precisely measured against this threshold — spot-check the Ask DRIFT
      beat once more before calling this done.
- [x] Primary-source citation held ≥ 2 seconds (beat 6). Confirmed: the
      NCCL GitHub release page holds on screen well past 2s in the
      citation-click beat.
- [ ] Captions/subtitles on (judges often watch muted first). Not added —
      recommend turning on YouTube's auto-captions (or uploading a reviewed
      SRT) before calling submission-ready.
- [ ] Music: silence, or a license-free bed only — **no copyrighted tracks**.
      The plan never called for a music bed (narration-only per the
      Assembly section), and nothing suggests one was added, but this is an
      audio check I haven't listened through to confirm myself.
- [x] Total cut ≤ 3:00 — confirmed via `ffprobe`: 2:45. Audio-off/video-off
      passes are a final human gut-check still worth doing once before
      submission, even with the beat-by-beat verification above.
- [x] No secrets, keys, private URLs, or personal data anywhere on screen.
      Confirmed across every beat reviewed: only public URLs
      (`github.com`, `dr1ftless.vercel.app`, `drift-api-prod.up.railway.app`)
      and no `.env`/keys/personal paths visible anywhere.
- [x] Upload **public** (not unlisted) to YouTube; paste the final URL into
      the README, `submission/SUBMISSION.md`, and Devpost, replacing
      `https://youtu.be/TBD`. Published: `https://youtu.be/6sbIz0ZR8Hw`.

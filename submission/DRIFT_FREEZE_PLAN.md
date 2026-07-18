# DRIFT — FREEZE PLAN
## OpenAI Build Week 2026 (Developer Tools)

> Frozen execution plan.
>
> Goal: maximize judging score while avoiding unnecessary feature creep.

## Audit addendum — 2026-07-17

**Codex Session ID:** `019f7190-912d-70e3-be6d-fcc81bf8e203`

This plan was audited against the tracked backend/frontend source, tests,
assets, README, architecture records, submission notes, and current hosted
verification records. The following are verified boundaries for the freeze:

- Implemented core: release-feed ingestion, typed claim evidence, separate
  verifier screening, human review-gated publication, evidence persistence,
  citations, briefing/search/chat, and the no-key fixture lane.
- The tracked repository has no DRIFT MCP server, MCP tools, generic tool-call
  API, IDE integration, or release-timeline feature. Those remain optional
  future ideas and must not be presented as shipped features.
- The repository contains architecture diagrams and nine refreshed screenshots, but no
  demo GIFs. The demo remains an operator-owned, under-three-minute recording
  gate; the existing script targets 2:50–2:55.
- Hosted evidence remains bounded: the deployed app is still `v0.8.0` for
  health/docs, public Ask DRIFT, and CORS, while the live Railway store now
  serves exactly five human-reviewed Tier.FINAL Insights (IDs 10, 11, 13, 15,
  and 16); the app redeploy is pending. Paid hosted `/search` and `/chat` were
  not re-invoked for this store-only update.

The numeric score matrix below is an internal prioritization estimate, not
measured judging evidence. No new feature surface is authorized by this audit;
remaining work may include the targeted Tier.FINAL evidence pass, selected
polish, the video, and the Devpost submission.

## Evidence cleanup addendum — 2026-07-18

**Codex Session ID:** `019f7213-be19-7e50-92ac-a48bd5ecaacb`

The superseded Luna reviewed Insights 3, 6, 7, and 8 were returned to draft
through the audited review helper. Hosted `/briefing?top_n=10` was re-fetched
and returned exactly the five reviewed Tier.FINAL Sol Insights (10, 11, 13,
15, and 16). The deployed app remains `v0.8.0` pending redeploy; this does not
claim hosted application verification for the `v0.9.0` source release.

## Terra evidence addendum — 2026-07-18

**Codex Session ID:** `019f7278-ee77-7f02-bafd-6eba8bf046d2`

The bounded `v0.9.1` Terra run asked one question per configured source over
the five reviewed Tier.FINAL Insights. Seven answers were grounded, PyTorch was
declined, no database rows were written, and the true grounded IDs, citations,
provider metadata, and spend deltas were archived with a SHA-256 manifest.
The refreshed screenshot gallery is committed as bounded visual evidence;
hosted redeployment remains an open human-operated gate, and the hosted
application is still verified only as `v0.8.0`.

---

# Philosophy

The repository is already a strong engineering project.

The remaining work is **not** "adding more AI."

The remaining work is making judges immediately understand:

- why DRIFT exists,
- why OpenAI is essential,
- why developers would actually use it.

Everything below is prioritized for maximum judging impact.

---

# Score Matrix — current readiness vs projected final

These are internal readiness estimates, not guaranteed judge scores. **Current**
reflects the verified repository and hosted state before the Tier.FINAL rerun
and public video. **Target** reflects the completed v0.9.0 and v0.9.1 evidence passes and
v1.0.0 submission finish.

| Category | Current | Target | Readiness |
|-----------|---------|--------|-----------|
| Problem Selection | 9.4 | 9.6 | ✅ Strong and specific |
| Innovation | 8.9 | 9.2 | 🟡 Strong concept; demo must make differentiation immediate |
| OpenAI Integration | 8.4 | 9.3 | 🟡 GPT-5.6 narration pending |
| Technical Difficulty | 9.6 | 9.8 | ✅ Typed pipeline, persistence, retrieval, and review gate implemented |
| Engineering Quality | 9.7 | 9.8 | ✅ 160 tests and 100% backend coverage verified |
| Documentation | 9.0 | 9.7 | 🟡 Strong records; final evidence/video links remain pending |
| Architecture | 9.7 | 9.8 | ✅ Architecture and trust boundaries are implemented and documented |
| Safety & Trust | 9.7 | 9.8 | ✅ Evidence spans, verifier screening, and human publication gate |
| UX | 8.5 | 8.9 | 🟡 Ask DRIFT is clear; surface remains intentionally focused |
| Demo | 4.0 | 9.0 | 🔴 Public video not yet recorded |
| Submission Quality | 5.8 | 9.2 | 🔴 Video URL and final Devpost records are pending |
| OSS Readiness | 9.5 | 9.7 | ✅ License, security, contributing, CI, and judge path present |

The largest present-state gap is submission readiness, not core engineering:
the under-three-minute video and final Devpost materials remain. The completed
Tier.FINAL pass should raise OpenAI Integration,
Documentation, Demo, and Submission Quality most directly.

---

# Priority 1 (Mandatory)

## 1. Produce a world-class demo

Target:
10/10

The first 60 seconds should answer:

> Why should I care?

Structure:

1. Developer problem
2. Real upstream release
3. Ask DRIFT
4. Grounded answer
5. Citations
6. Impact analysis
7. Recommendation

No architecture yet.

Only value.

---

## 2. Make OpenAI indispensable

Judges should conclude:

> This could not reasonably exist without modern reasoning models.

Demonstrate:

- synthesis
- evidence comparison
- ambiguity handling
- grounded responses
- verification

Avoid describing DRIFT as:

"AI summarizer"

Instead:

"Grounded release intelligence."

---

## 3. Improve UX

Current:

Engineering-first.

Target:

Developer-first.

Examples:

Instead of

"What changed?"

Use

"Will upgrading CUDA break my stack?"

Instead of

"Summarize releases"

Use

"Do I need to care?"

---

## 4. End-to-end workflow

One complete story:

Source release

↓

Evidence ingestion

↓

Verification

↓

Storage

↓

Grounded reasoning

↓

Developer answer

↓

Action recommendation

---

# Priority 2 (Optional future work — excluded from this freeze)

## MCP Integration

DRIFT does not currently expose MCP. Add it only in a future scope if it
creates a new capability; do not imply that the current HTTP API is an MCP
server.

Good architecture:

```
Cursor

↓

MCP

↓

DRIFT

↓

Verified Release Intelligence

↓

Grounded Response
```

Supported clients:

- Cursor
- Claude Desktop
- VS Code
- Windsurf
- Any MCP-compatible agent

Example:

Developer:

> Did CUDA 13 break vLLM?

MCP

↓

DRIFT

↓

Returns:

- evidence
- citations
- impact
- migration notes
- confidence

This is valuable.

Simply exposing DRIFT through MCP is not.

The MCP layer should unlock new workflows.

---

## Tool Calling

Expose tools such as:

- search releases
- compare versions
- summarize impact
- dependency lookup
- cite evidence
- timeline

These naturally map to MCP tools.

---

## Better User Stories

These are future examples, not current shipped workflows. The current saved
and reviewed evidence is bounded to the documented release captures.

Examples:

- CUDA upgrade
- PyTorch release
- NeMo release
- TensorRT release
- vLLM release

---

# Priority 3 (Nice to Have — deferred)

## Evaluation

Include measurable quality.

Examples:

- grounding rate
- citation coverage
- verifier pass rate
- unsupported claim rate
- retrieval latency

Even simple metrics improve credibility.

---

## Screenshots

Available now:

- Home/landing
- API docs
- Briefing
- Claim evidence
- Architecture

There is no dedicated timeline screen, and no dedicated search screen beyond
the API/briefing evidence.

---

## GIFs

Short animations:

- ingestion
- search
- grounded answer

---

## Landing Page Polish

One sentence.

One screenshot.

One animation.

No long paragraphs above the fold.

---

# Demo Script

Target: under 3 minutes; the checked-in script targets 2:50–2:55.

Minute 1

Problem.

Minute 2

Live workflow.

Minute 3

Architecture.

Minute 4

Future vision.

Never reverse this order.

---

# Things NOT To Add

Avoid feature creep.

Do NOT add:

- another LLM
- multi-provider support
- autonomous agents
- unnecessary RAG
- unrelated dashboards
- blockchain
- crypto
- gamification

Every feature should answer:

"Does this improve developer release intelligence?"

If not,

don't build it.

---

# Frozen Feature List

Core

✅ Release ingestion

✅ Verification

✅ Grounded chat

✅ Citations

✅ Review gate

✅ Evidence database

⬜ Release timeline — not implemented

Stretch

⬜ MCP Server — not implemented

⬜ Tool Calling — not implemented

⬜ IDE Integration — not implemented

---

# Submission Checklist

## Repository

- [x] README complete
- [x] Architecture diagrams
- [x] Screenshots (landing, API docs, briefing, claim evidence)
- [ ] Demo GIFs
- [x] Installation path documented and locally exercised
- [x] CI passing / quality gates documented
- [x] License
- [x] Security policy
- [x] Contributing guide

---

## Demo

- [ ] Recorded
- [ ] Audio clean
- [ ] 1080p
- [ ] Under time limit
- [ ] Shows OpenAI reasoning
- [ ] Shows citations
- [ ] Shows verification
- [ ] Shows developer workflow

---

## Devpost

- [ ] Compelling title
- [ ] Clear one-line tagline
- [ ] Problem statement
- [ ] Why OpenAI
- [ ] Architecture
- [ ] Challenges
- [ ] Future work
- [ ] GitHub
- [ ] Video
- [ ] Screenshots

---

# Final Definition of Done

A judge should finish the demo thinking:

> "I immediately understand the problem."

> "The AI is doing something genuinely useful."

> "The engineering is exceptional."

> "I could use this tomorrow."

> "This deserves to be among the strongest Developer Tools submissions."

---

# Final Rule

From this point onward:

Every new commit must satisfy at least one of these:

1. Improves developer value.
2. Improves OpenAI reasoning.
3. Improves demo quality.
4. Improves judging clarity.

If it satisfies none of them,

do not build it.

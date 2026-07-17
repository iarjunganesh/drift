# DRIFT — FREEZE PLAN
## OpenAI Build Week 2026 (Developer Tools)

> Frozen execution plan.
>
> Goal: maximize judging score while avoiding unnecessary feature creep.

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

# Final Score Matrix

| Category | Current | Target | Status |
|-----------|---------|--------|--------|
| Problem Selection | 9.6 | 10 | ⬜ |
| Innovation | 9.3 | 10 | ⬜ |
| OpenAI Integration | 8.8 | 10 | ⬜ |
| Technical Difficulty | 9.8 | 10 | ⬜ |
| Engineering Quality | 9.8 | 10 | ⬜ |
| Documentation | 9.8 | 10 | ⬜ |
| Architecture | 9.8 | 10 | ⬜ |
| Safety & Trust | 9.7 | 10 | ⬜ |
| UX | 8.3 | 10 | ⬜ |
| Demo | 8.2 | 10 | ⬜ |
| Submission Quality | 9.0 | 10 | ⬜ |
| OSS Readiness | 9.9 | 10 | ⬜ |

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

# Priority 2 (Strongly Recommended)

## MCP Integration

Add MCP only if it creates new capability.

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

Create several polished examples.

Examples:

- CUDA upgrade
- PyTorch release
- NeMo release
- TensorRT release
- vLLM release

---

# Priority 3 (Nice to Have)

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

Include:

- Home
- Search
- Chat
- Timeline
- Evidence
- Architecture

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

Target:

3–4 minutes

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

✅ Release timeline

Stretch

✅ MCP Server

✅ Tool Calling

✅ IDE Integration

---

# Submission Checklist

## Repository

- [ ] README complete
- [ ] Architecture diagrams
- [ ] Screenshots
- [ ] Demo GIFs
- [ ] Installation tested
- [ ] CI passing
- [ ] License
- [ ] Security policy
- [ ] Contributing guide

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
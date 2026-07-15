# DRIFT — three-minute YouTube demo script

> **Placeholder:** replace the `https://youtu.be/TBD` URL in the README and
> submission documents after uploading the final public video.

Target runtime: **2:50–2:55**, hard cap three minutes. Record at 1080p with
clear English narration. Use silence or properly licensed audio only. The video
must show a working path and accurately distinguish fixture behavior from live
model behavior.

## Timeline and shot list

| Time | Screen | Narration / action |
| --- | --- | --- |
| 0:00–0:10 | DRIFT hero banner | “DRIFT turns GPU and AI-infrastructure release noise into a cited engineering check.” |
| 0:10–0:28 | README problem section or architecture | “Teams depend on fast-moving projects such as vLLM, PyTorch, Triton, and CUDA. DRIFT answers what changed, why it matters, and what to check next.” |
| 0:28–0:42 | Terminal: start API | Run `uv run uvicorn backend.main:app --reload`; show the no-key fixture mode. |
| 0:42–1:00 | `/health` and `/briefing` | Show `mode: fixture`, ranked insights, severity, confidence, and citations. Say explicitly that these are committed examples, not live analysis. |
| 1:00–1:20 | `/search?q=vllm` | Search for an affected library and point out the source-backed result. |
| 1:20–1:45 | `POST /chat` or Swagger UI | Ask “What should I check for vLLM?” Show that the answer is grounded in matching insights and returns citations. |
| 1:45–2:00 | Frontend at `https://dr1ftless.vercel.app` | Show the operator-facing briefing view, then the API docs link. |
| 2:00–2:20 | Architecture diagram | Follow feeds → Scout → Synthesizer → Insight → Briefing. Explain that scheduled feed persistence, pgvector retrieval, generated Insight model output, and end-to-end wiring are the next implementation boundary; the Day 1 feed/schema and Day 2 Synthesizer foundations are already implemented. |
| 2:20–2:38 | ADR index and CI workflow | Show typed stages, provenance requirements, Ruff, mypy, pytest, coverage, Codecov upload, and the enforced 100% floor for implemented code. |
| 2:38–2:52 | Code or final briefing | Explain Codex’s role in shaping the typed pipeline, bounded live-chat safeguards, tests, docs, and gates. Explain GPT-5.6’s role only using saved, verified live output; live release ingestion and generated insights are not complete. |

## Final narration

“DRIFT is intentionally honest about its boundary: the fixture path is
reproducible today, while ingestion, persistence, retrieval, and model-backed
insight generation are being built behind explicit contracts. Every live insight
will carry citations, confidence, an audit label, and a bounded action.”

## Pre-upload checklist

- [ ] Runtime is under three minutes.
- [ ] Video is public on YouTube, not unlisted.
- [ ] No secrets, API keys, private URLs, or personal data appear on screen.
- [ ] Fixture records are labelled as fixtures.
- [ ] Any GPT-5.6 claim is backed by a saved, reproducible output.
- [ ] Codex’s actual contribution is narrated.
- [ ] Audio is clear and uses no copyrighted music.
- [ ] README, `submission/SUBMISSION.md`, and Devpost contain the final URL.

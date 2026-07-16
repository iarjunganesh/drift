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
| 0:42–1:00 | `/health` and `/briefing` | Show the live reviewed briefing after confirming the deployed version. Point out severity, confidence, citations, and that this is a small bounded four-Insight set—not broad live analysis. |
| 1:00–1:20 | `/search?q=vllm` | Search the reviewed vLLM release and point out the frozen source-backed result. |
| 1:20–1:45 | `POST /chat` or Swagger UI | Ask “What should I check for vLLM?” Show that the answer is grounded in matching reviewed Insights and returns citations. |
| 1:45–2:00 | Frontend at `https://dr1ftless.vercel.app` | Show the four reviewed cards, claim-evidence panel, and API docs link. |
| 2:00–2:20 | Architecture diagram | Follow feeds → Scout → Synthesizer → claim draft → separate verifier → human review → Briefing. Explain that exact source spans, claim labels, and two audits are retained; drafts stay private until a human records review notes, which are database-only. |
| 2:20–2:38 | ADR index and CI workflow | Show typed stages, provenance requirements, Ruff, mypy, pytest, coverage, Codecov upload, and the enforced 100% floor for implemented code. |
| 2:38–2:52 | Code or final briefing | Explain Codex’s role in shaping the typed pipeline, bounded live-chat safeguards, tests, docs, and gates. Explain GPT-5.6’s role using the four saved, reviewed live outputs; do not overclaim beyond that bounded set. |

## Final narration

“DRIFT is intentionally honest about its boundary: the fixture path is
reproducible, and the hosted review-first path currently presents four
human-reviewed Insights from one bounded capture—not continuous release
monitoring. Every public live insight carries typed claims, frozen source
evidence, confidence, two audit records, human review, and a bounded action.”

## Pre-upload checklist

- [ ] Runtime is under three minutes.
- [ ] Video is public on YouTube, not unlisted.
- [ ] No secrets, API keys, private URLs, or personal data appear on screen.
- [ ] Fixture records are labelled as fixtures.
- [ ] Any GPT-5.6 claim is backed by a saved, reproducible output.
- [ ] Codex’s actual contribution is narrated.
- [ ] Audio is clear and uses no copyrighted music.
- [ ] README, `submission/SUBMISSION.md`, and Devpost contain the final URL.

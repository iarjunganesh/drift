#!/usr/bin/env python3
"""One-off demo-voiceover generation for DRIFT.

Generates the nine per-beat narration clips (`vo_01-hook` ... `vo_09-close`)
plus a continuous `vo_full-reference.mp3` for the submission video, using
OpenAI text-to-speech. AI narration is explicitly allowed by the Devpost rules
("text-to-speech and AI narration tools are acceptable alternatives to
recording yourself").

The narration text is verbatim from `submission/DEMO_SCRIPT.md` — keep the two
in sync. A few clips carry a TTS-adjusted spoken variant so acronyms and
version numbers read cleanly (N-C-C-L, V-L-L-M, "GPT five-point-six",
"version zero-point-ten"); the on-screen script is unchanged.

The API key is read from the OPENAI_API_KEY environment variable, or from the
gitignored `.env` file at the repository root. Its value is never printed.
This is a direct provider call outside the DRIFT `SpendGuard`/ledger, like
`check_openai_spend.py`; the DRIFT project must have the TTS model enabled
(the default is `tts-1`). Total input is ~4.3K characters, so a full run costs
about $0.07 at `tts-1` rates ($0.015/1K chars).

Usage:
    uv run python scripts/generate_demo_voiceover.py
    uv run python scripts/generate_demo_voiceover.py --voice onyx --force

Existing clips are skipped, so a partially failed run can simply be re-run to
resume at no extra cost; pass --force to regenerate everything. Intermittent
403s (a freshly enabled model still propagating to every gateway replica) are
retried with backoff.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

from openai import OpenAI, PermissionDeniedError

MAX_ATTEMPTS = 5

REPO_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = REPO_ROOT / ".env"
DEFAULT_OUT = REPO_ROOT / "assets" / "demo-voiceover"

# (name, display text from DEMO_SCRIPT.md, optional TTS-adjusted text)
CLIPS: list[tuple[str, str, str | None]] = [
    (
        "vo_01-hook",
        "This is a real NCCL release — dozens of changes: dropped plugin "
        "APIs, new collective paths, new flags. Somewhere in here is the "
        "line that matters to your cluster.",
        "This is a real N-C-C-L release — dozens of changes: dropped plugin "
        "A-P-Is, new collective paths, new flags. Somewhere in here is the "
        "line that matters to your cluster.",
    ),
    (
        "vo_02-reveal",
        "DRIFT exists to find it first. Release intelligence for GPU and AI "
        "infrastructure — what changed, why it matters, what to check — "
        "running live and hosted, right now.",
        None,
    ),
    (
        "vo_03-briefing",
        "Today's briefing holds five human-reviewed, verifier-passed "
        "insights — a bounded set, not a firehose. JAX dropping Python and "
        "NumPy versions, TensorRT's CUDA defaults, vLLM, Transformers, "
        "NCCL. Each card is a decision: severity, confidence, the exact "
        "model that drafted it, and one bounded thing to check before "
        "production moves.",
        "Today's briefing holds five human-reviewed, verifier-passed "
        "insights — a bounded set, not a firehose. JAX dropping Python and "
        "NumPy versions, Tensor-R-T's CUDA defaults, V-L-L-M, Transformers, "
        "N-C-C-L. Each card is a decision: severity, confidence, the exact "
        "model that drafted it, and one bounded thing to check before "
        "production moves.",
    ),
    (
        "vo_04-evidence",
        "Every claim stays inspectable: a frozen excerpt of the primary "
        "source, with character offsets and a source hash. Click the "
        "citation — you land on the release itself. Facts, inferences, and "
        "recommended checks are labelled separately, so you audit the "
        "reasoning instead of trusting it.",
        None,
    ),
    (
        "vo_05-ask",
        "Now ask it a real question: what should an operator check for this "
        "NCCL release? DRIFT retrieves matching reviewed evidence first; "
        "then GPT-5.6 writes the answer over that evidence and cites only "
        "what it actually used. Concrete checks, a source link, the model "
        "named on screen.",
        "Now ask it a real question: what should an operator check for this "
        "N-C-C-L release? DRIFT retrieves matching reviewed evidence first; "
        "then GPT five-point-six writes the answer over that evidence and "
        "cites only what it actually used. Concrete checks, a source link, "
        "the model named on screen.",
    ),
    (
        "vo_06-decline",
        "Ask about something outside the reviewed corpus — Kubernetes — and "
        "DRIFT declines. No guess, no fabricated citation. That refusal is "
        "the product working.",
        None,
    ),
    (
        "vo_07-mcp",
        "Since version 0.10.0, the same intelligence follows you into your "
        "editor. A thin MCP client exposes three tools over the same public "
        "API — no key, no database access, no write path — so the review "
        "gate and budgets stay server-side. Here's VS Code asking DRIFT for "
        "NCCL checks, live.",
        "Since version zero-point-ten, the same intelligence follows you "
        "into your editor. A thin M-C-P client exposes three tools over the "
        "same public A-P-I — no key, no database access, no write path — so "
        "the review gate and budgets stay server-side. Here's V-S Code "
        "asking DRIFT for N-C-C-L checks, live.",
    ),
    (
        "vo_08-pipeline",
        "Under it all is a typed pipeline, built with Codex. Scout reads "
        "primary feeds; claims freeze their source spans; a separate "
        "GPT-5.6 verifier screens every draft; and a human must review "
        "before anything publishes. GPT-5.6 powers synthesis, verification, "
        "and grounded chat; Codex shaped the stages, safeguards, and tests "
        "— two hundred tests, one hundred percent coverage.",
        "Under it all is a typed pipeline, built with Codex. Scout reads "
        "primary feeds; claims freeze their source spans; a separate GPT "
        "five-point-six verifier screens every draft; and a human must "
        "review before anything publishes. GPT five-point-six powers "
        "synthesis, verification, and grounded chat; Codex shaped the "
        "stages, safeguards, and tests — two hundred tests, one hundred "
        "percent coverage.",
    ),
    (
        "vo_09-close",
        "DRIFT. Release intelligence for GPU and AI infrastructure — cited, "
        "bounded, inspectable. The briefing is live — go ask it something.",
        None,
    ),
]


def load_api_key() -> str:
    """Load the API key from the environment or the gitignored .env, silently."""
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if key:
        return key
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("OPENAI_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate the DRIFT demo voiceover clips with OpenAI TTS."
    )
    parser.add_argument(
        "--model", default="tts-1",
        help="TTS model enabled on the DRIFT project (default: tts-1)",
    )
    parser.add_argument(
        "--voice", default="nova",
        help="alloy | echo | fable | onyx | nova | shimmer (default: nova)",
    )
    parser.add_argument(
        "--out", type=Path, default=DEFAULT_OUT,
        help=f"output directory (default: {DEFAULT_OUT})",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="regenerate all clips, overwriting existing files",
    )
    args = parser.parse_args()

    api_key = load_api_key()
    if not api_key:
        print("OPENAI_API_KEY is not set and no .env entry was found.")
        return 1

    out_dir: Path = args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    client = OpenAI(api_key=api_key)

    def synth(text: str, path: Path) -> bool:
        """Generate one clip; skip if present so a partial run resumes at no
        extra cost. Intermittent 403s are retried with backoff — a console
        model-allow-list change can take a while to reach every gateway
        replica, so early calls may fail while later ones succeed."""
        if path.exists() and not args.force:
            print(f"  skipping existing {path.relative_to(REPO_ROOT)}")
            return False
        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                with client.audio.speech.with_streaming_response.create(
                    model=args.model, voice=args.voice, input=text
                ) as response:
                    response.stream_to_file(path)
                print(f"  wrote {path.relative_to(REPO_ROOT)}")
                return True
            except PermissionDeniedError:
                if attempt == MAX_ATTEMPTS:
                    raise
                delay = 3 * attempt
                print(
                    f"  403 for {path.name} (attempt {attempt}/{MAX_ATTEMPTS})"
                    f" — retrying in {delay}s while model access propagates"
                )
                time.sleep(delay)
        return False

    total_chars = 0
    for name, display, tts_variant in CLIPS:
        text = tts_variant or display
        if synth(text, out_dir / f"{name}.mp3"):
            total_chars += len(text)

    full_text = "\n\n".join(tts or text for _, text, tts in CLIPS)
    if synth(full_text, out_dir / "vo_full-reference.mp3"):
        total_chars += len(full_text)

    rate = 0.030 if args.model == "tts-1-hd" else 0.015
    print(
        f"Done: generated ~{total_chars} chars this run, estimated cost "
        f"${total_chars / 1000 * rate:.2f} ({args.model}, voice {args.voice});"
        f" existing clips were skipped (--force regenerates them)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

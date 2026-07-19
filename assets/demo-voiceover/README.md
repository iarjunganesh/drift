# Demo Voiceover

AI-narrated voiceover for the ≤3-min submission video, generated with OpenAI
**`tts-1`** (voice **`nova`**). AI narration is explicitly allowed by the
Devpost rules ("text-to-speech and AI narration tools are acceptable
alternatives to recording yourself"). Text is verbatim from
[`submission/DEMO_SCRIPT.md`](../../submission/DEMO_SCRIPT.md); a few clips use
a TTS-adjusted spoken variant so acronyms and version numbers read cleanly
(N-C-C-L, V-L-L-M, "GPT five-point-six", "version zero-point-ten") while the
on-screen script is unchanged.

- `vo_01-hook … vo_09-close.mp3` — one clip per beat (~2:20 total), for precise
  placement against the screen recordings.
- `vo_full-reference.mp3` — the whole narration as one continuous track
  (reference/fallback).

Regenerate or tweak wording via
[`scripts/generate_demo_voiceover.py`](../../scripts/generate_demo_voiceover.py),
run from the repo root:

```bash
uv run python scripts/generate_demo_voiceover.py
```

Cost ≈ $0.07 on OpenAI (`tts-1`, ~4.3K input characters). This is a direct
provider call outside the DRIFT `SpendGuard`/ledger, like
`scripts/check_openai_spend.py`, and requires the TTS model to be enabled on
the DRIFT project. The generator refuses to overwrite existing clips unless
`--force` is passed.

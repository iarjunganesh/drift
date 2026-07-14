"""
Model routing for DRIFT.

Every OpenAI call in this codebase must go through get_model(tier) —
never hardcode a model name inline. This keeps cost predictable and
makes the dev/live/final cost strategy a one-line change.

Tiers:
  dev   — gpt-5.6-luna  — cheap iteration. Scout classification,
                           Synthesizer dedup/clustering, prompt tuning.
  live  — gpt-5.6-terra — the on-camera / interactive chat-over-knowledge
                           endpoint. Needs to be reliably sharp live.
  final — gpt-5.6-sol   — captured Insight outputs for the small set of
                           real examples used in the demo. Reserve this
                           tier deliberately — don't burn it on iteration.
"""

from enum import StrEnum


class Tier(StrEnum):
    DEV = "dev"
    LIVE = "live"
    FINAL = "final"


MODEL_MAP = {
    Tier.DEV: "gpt-5.6-luna",
    Tier.LIVE: "gpt-5.6-terra",
    Tier.FINAL: "gpt-5.6-sol",
}

EMBEDDING_MODEL = "text-embedding-3-small"


def get_model(tier: Tier | str) -> str:
    """Resolve a cost tier to a concrete model name.

    Usage:
        model = get_model(Tier.DEV)
        response = client.chat.completions.create(model=model, ...)
    """
    if isinstance(tier, str):
        tier = Tier(tier)
    return MODEL_MAP[tier]

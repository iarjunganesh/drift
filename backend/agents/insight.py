"""
Insight agent — Days 3-4. THE differentiation core of DRIFT.

Given a clustered, classified change, this agent reasons about:
  - what specifically changed (in plain terms, not changelog-speak)
  - why it matters to an AI/infra engineer's actual workflow
  - what they should check in their own codebase/deployment

This is where "can other models do this, or does it showcase GPT-5.6
uniquely" gets answered. A keyword/diff tool can flag THAT something
changed. This agent explains WHY it matters and WHAT to do — that's
the reasoning step that needs a frontier model, not a summarizer.

Hard requirement (safety/design criterion): every Insight MUST carry
source_citations and a confidence score. Never let severity=BREAKING
ship without both — an ungrounded claim in a tool devs trust to flag
breaking changes is actively harmful, not just low quality.

Cost discipline: iterate prompts on Tier.DEV (Luna). Only the final
3-5 real examples selected for the demo get re-run on Tier.FINAL (Sol)
— see docs/demo-examples.md once that's populated on Day 8.
"""

from backend.core.model_router import Tier
from backend.models.schema import ChangeSeverity, Insight, RawItem

INSIGHT_SYSTEM_PROMPT = """You are DRIFT's reasoning core. You explain \
changes in GPU/AI infrastructure libraries to engineers who depend on \
them, but don't have time to read every release note.

For the change described, produce:
1. A one-sentence plain-English summary of what changed.
2. Why it matters — specifically, not generically. Name the failure \
mode or opportunity this creates for someone running production \
inference/training workloads.
3. A concrete "what to check" action.
4. A confidence score (0-1) reflecting how certain you are this is a \
real, substantive change and not a doc/wording tweak.

Ground every claim in the provided source text. If you're not certain \
something is a breaking change, say so — do not inflate severity.
"""


def generate_insight(
    cluster: list[RawItem],
    severity: ChangeSeverity,
    tier: Tier = Tier.DEV,
) -> Insight:
    """
    TODO(codex): build the user prompt from cluster contents, call
    get_model(tier) with INSIGHT_SYSTEM_PROMPT, parse structured output
    into an Insight object. Populate source_citations from cluster URLs
    and model_used from the resolved model name (audit trail — reuse
    the provenance-manifest pattern from bankers-wrapped).
    """
    raise NotImplementedError


def run_insight_batch(
    classified_clusters: list[tuple[list[RawItem], ChangeSeverity]],
    tier: Tier = Tier.DEV,
) -> list[Insight]:
    return [
        generate_insight(cluster, severity, tier)
        for cluster, severity in classified_clusters
    ]

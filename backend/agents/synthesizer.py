"""
Synthesizer agent — Day 2.

Takes raw items and:
  1. Dedupes near-identical items via embedding similarity
  2. Clusters related items (e.g. same release across multiple mirrors)
  3. Classifies substantive vs cosmetic change — THIS is the first
     GPT-5.6 touchpoint. Run on Tier.DEV (Luna) while iterating.

Codex: implement embed_items() using EMBEDDING_MODEL from model_router,
cluster via cosine similarity threshold, and classify_change() as a
single small structured-output call per cluster (severity only —
save the "why it matters" reasoning for the Insight agent, don't
duplicate work here).
"""

from backend.models.schema import ChangeSeverity, RawItem


def embed_items(items: list[RawItem]) -> list[list[float]]:
    """TODO(codex): batch-embed item titles+content via EMBEDDING_MODEL."""
    raise NotImplementedError


def cluster_items(items: list[RawItem], embeddings: list[list[float]]) -> list[list[RawItem]]:
    """TODO(codex): group items by embedding cosine similarity threshold."""
    raise NotImplementedError


def classify_change(cluster: list[RawItem]) -> ChangeSeverity:
    """
    TODO(codex): one GPT-5.6 call (model=get_model(Tier.DEV)) with a
    structured-output schema returning just the ChangeSeverity enum.
    Keep this call narrow — classification only, not explanation.
    """
    raise NotImplementedError


def run_synthesizer(items: list[RawItem]) -> list[tuple[list[RawItem], ChangeSeverity]]:
    embeddings = embed_items(items)
    clusters = cluster_items(items, embeddings)
    return [(cluster, classify_change(cluster)) for cluster in clusters]

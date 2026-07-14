"""
Core data model for DRIFT.

Three tables:
  sources    — the curated feed list (loaded from sources.yaml)
  raw_items  — unprocessed items pulled by the Scout agent
  insights   — Synthesizer/Insight agent output: clustered, reasoned-over
               changes, each with a source citation and confidence flag

Uses SQLAlchemy models + pgvector for the insights embedding column.
Codex: flesh out the actual SQLAlchemy Base/engine/session wiring here,
following the async pattern from the bankers-wrapped reference repo.
"""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class ChangeSeverity(StrEnum):
    COSMETIC = "cosmetic"       # wording/doc change, no action needed
    MINOR = "minor"             # small behavior change, worth noting
    BREAKING = "breaking"       # breaking change — needs dev attention
    SECURITY = "security"       # security-relevant — highest priority


class RawItem(BaseModel):
    id: int | None = None
    source_id: str
    title: str
    url: str
    published_at: datetime
    raw_content: str
    fetched_at: datetime = Field(default_factory=datetime.utcnow)


class Insight(BaseModel):
    """
    The core output unit. Every field here exists because the judging
    criteria and the safety requirement demand it — don't strip fields
    to simplify the UI later without re-checking against those.
    """
    id: int | None = None
    raw_item_ids: list[int]        # which raw items this insight synthesizes
    title: str
    summary: str                    # the "what changed"
    why_it_matters: str             # the GPT-5.6 reasoning output — the core value
    what_to_check: str              # concrete, bounded follow-up for the engineer
    severity: ChangeSeverity
    affected_libraries: list[str]   # e.g. ["pytorch", "triton"]
    source_citations: list[str]     # URLs — every claim must trace back here
    confidence: float = Field(ge=0.0, le=1.0)  # model's own confidence flag
    model_used: str                 # which tier generated this (audit trail)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class BriefingItem(BaseModel):
    """One entry in the daily 'Top N Things That Matter' briefing."""
    insight: Insight
    rank: int


class ChatRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2_000)


class ChatResponse(BaseModel):
    answer: str
    source_citations: list[str]
    model_used: str
    grounded_insight_ids: list[int]

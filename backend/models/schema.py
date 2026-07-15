"""
Core data model for DRIFT.

Three tables:
  sources    — the curated feed list (loaded from sources.yaml)
  raw_items  — unprocessed items pulled by the Scout agent
  insights   — Synthesizer/Insight agent output: clustered, reasoned-over
               changes, each with a source citation and confidence flag

Uses SQLAlchemy models + pgvector for the insights embedding column. The
async Base/engine/session wiring follows the conceptual pattern from the
bankers-wrapped reference repo without importing its unrelated dependencies.
"""

from collections.abc import AsyncIterator
from datetime import UTC, datetime
from enum import StrEnum

from pgvector.sqlalchemy import Vector
from pydantic import BaseModel, Field
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from backend.core.config import settings


class ChangeSeverity(StrEnum):
    COSMETIC = "cosmetic"       # wording/doc change, no action needed
    MINOR = "minor"             # small behavior change, worth noting
    BREAKING = "breaking"       # breaking change — needs dev attention
    SECURITY = "security"       # security-relevant — highest priority


class Base(DeclarativeBase):
    """SQLAlchemy metadata for the durable PostgreSQL/pgvector store."""


class SourceRow(Base):
    """Configured primary release source persisted for provenance."""

    __tablename__ = "sources"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    repo: Mapped[str] = mapped_column(String(255), nullable=False)
    feed_url: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")

    raw_items: Mapped[list[RawItemRow]] = relationship(back_populates="source")


class RawItemRow(Base):
    """Unprocessed release evidence fetched by Scout."""

    __tablename__ = "raw_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_id: Mapped[str] = mapped_column(
        String(100), ForeignKey("sources.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    raw_content: Mapped[str] = mapped_column(Text, nullable=False)
    content_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    source: Mapped[SourceRow] = relationship(back_populates="raw_items")


class InsightRow(Base):
    """Structured reasoning output with citation and embedding provenance."""

    __tablename__ = "insights"
    __table_args__ = (
        CheckConstraint("confidence >= 0 AND confidence <= 1", name="ck_insights_confidence_range"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    raw_item_ids: Mapped[list[int]] = mapped_column(JSONB, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    why_it_matters: Mapped[str] = mapped_column(Text, nullable=False)
    what_to_check: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    affected_libraries: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    source_citations: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    model_used: Mapped[str] = mapped_column(String(255), nullable=False)
    model_run_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("model_runs.id", ondelete="SET NULL"), nullable=True, index=True
    )
    human_review_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class ModelRunRow(Base):
    """Immutable audit data for a generated, persisted Insight."""

    __tablename__ = "model_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    operation: Mapped[str] = mapped_column(String(100), nullable=False)
    model_used: Mapped[str] = mapped_column(String(255), nullable=False)
    evidence_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    output_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    input_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    output_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    settled_usd: Mapped[float] = mapped_column(Float, nullable=False)
    provider_attempts: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


engine: AsyncEngine = create_async_engine(settings.database_url, pool_pre_ping=True)
session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    """Yield one async database session for a FastAPI dependency or job."""
    async with session_factory() as session:
        yield session


class RawItem(BaseModel):
    id: int | None = None
    source_id: str
    title: str
    url: str
    published_at: datetime
    raw_content: str
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


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
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


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

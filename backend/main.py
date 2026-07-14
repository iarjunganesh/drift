"""
DRIFT — FastAPI entrypoint.

Endpoints:
  GET  /briefing         — today's top-N insights
  GET  /search?q=...     — semantic search over accumulated insights
  POST /chat             — chat-over-knowledge (Tier.LIVE)
  GET  /health           — liveness check

Codex: wire these against the agent modules in backend/agents/.
Follow the async FastAPI pattern from the bankers-wrapped reference
repo (structlog request logging, consistent error handling), but do
NOT bring in anything related to its media-generation dependencies
(Genblaze, FFmpeg, B2) — DRIFT has no media component.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from backend.agents.briefing import answer_question, build_daily_briefing
from backend.core.config import settings
from backend.core.store import InsightStore
from backend.models.schema import BriefingItem, ChatRequest, ChatResponse, Insight


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.validate()
    if settings.mode != "fixture":
        raise RuntimeError("Live mode has not been enabled yet; use DRIFT_MODE=fixture.")
    app.state.insight_store = InsightStore.from_json(settings.fixture_path)
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="GPT-5.6 reasoning over GPU/AI-infra release drift.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=sorted({settings.frontend_origin, "http://localhost:3000"}),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "mode": settings.mode, "version": settings.app_version}


@app.get("/briefing")
async def briefing(top_n: int = Query(default=5, ge=1, le=10)) -> list[BriefingItem]:
    return build_daily_briefing(app.state.insight_store.all(), top_n)


@app.get("/search")
async def search(q: str = Query(min_length=2, max_length=300)) -> list[Insight]:
    return app.state.insight_store.search(q)


@app.post("/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    insights = app.state.insight_store.search(request.question, limit=3)
    if not insights:
        raise HTTPException(status_code=404, detail="No matching DRIFT insights.")
    return ChatResponse(
        answer=answer_question(request.question, insights),
        source_citations=sorted({url for item in insights for url in item.source_citations}),
        model_used="fixture-curated",
        grounded_insight_ids=[item.id for item in insights if item.id is not None],
    )

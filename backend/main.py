"""
DRIFT — FastAPI entrypoint.

Endpoints:
  GET  /                  — service metadata and API links
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

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from backend.agents.briefing import (
    answer_question,
    answer_question_with_model,
    build_daily_briefing,
)
from backend.core.budget import BudgetExceededError, SpendGuard
from backend.core.config import settings
from backend.core.model_router import Tier, create_async_client, get_model
from backend.core.resilience import (
    CircuitBreaker,
    ModelCallResilience,
    ModelCapacityExceededError,
    ProviderCircuitOpenError,
    RetryPolicy,
)
from backend.core.store import InsightStore
from backend.models.schema import BriefingItem, ChatRequest, ChatResponse, Insight


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.validate()
    app.state.insight_store = InsightStore.from_json(settings.fixture_path)
    client = None
    if settings.mode == "live":
        client = create_async_client(settings.openai_api_key, settings.model_timeout_seconds)
        app.state.openai_client = client
        app.state.model_call_limiter = asyncio.Semaphore(settings.model_max_concurrency)
        app.state.model_resilience = ModelCallResilience(
            retry_policy=RetryPolicy(
                timeout_seconds=settings.model_timeout_seconds,
                max_attempts=settings.model_max_attempts,
                base_delay_seconds=settings.model_retry_base_seconds,
                max_delay_seconds=settings.model_retry_max_seconds,
            ),
            circuit_breaker=CircuitBreaker(
                failure_threshold=settings.model_circuit_failure_threshold,
                reset_seconds=settings.model_circuit_reset_seconds,
            ),
        )
        app.state.spend_guard = SpendGuard(
            settings.spend_ledger_path,
            settings.max_spend_usd,
            settings.spend_alert_usd,
        )
    try:
        yield
    finally:
        if client is not None:
            await client.close()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="GPT-5.6 reasoning over GPU/AI-infra release drift.",
    openapi_tags=[
        {
            "name": "system",
            "description": "Service metadata, liveness, and API discovery.",
        },
        {
            "name": "briefing",
            "description": "Ranked release insights for the current briefing.",
        },
        {
            "name": "search",
            "description": "Search cited DRIFT insights by library or release risk.",
        },
        {
            "name": "chat",
            "description": "Ask questions grounded in matching DRIFT insights.",
        },
    ],
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=sorted({settings.frontend_origin, "http://localhost:3000"}),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get(
    "/",
    tags=["system"],
    summary="Service metadata",
    description="Return the service status and links to the public API contract.",
)
async def root() -> dict[str, str]:
    return {
        "service": settings.app_name,
        "status": "ok",
        "mode": settings.mode,
        "version": settings.app_version,
        "health": "/health",
        "docs": "/docs",
        "openapi": "/openapi.json",
    }


@app.get(
    "/health",
    tags=["system"],
    summary="Health check",
    description="Return the current service mode and version for deployment probes.",
)
async def health() -> dict:
    return {"status": "ok", "mode": settings.mode, "version": settings.app_version}


@app.get(
    "/briefing",
    tags=["briefing"],
    summary="Build daily briefing",
    description="Rank the most important cited insights for the current briefing.",
)
async def briefing(top_n: int = Query(default=5, ge=1, le=10)) -> list[BriefingItem]:
    return build_daily_briefing(app.state.insight_store.all(), top_n)


@app.get(
    "/search",
    tags=["search"],
    summary="Search insights",
    description="Find cited insights matching a library, release, or risk query.",
)
async def search(q: str = Query(min_length=2, max_length=300)) -> list[Insight]:
    return app.state.insight_store.search(q)


@app.post(
    "/chat",
    tags=["chat"],
    summary="Ask grounded question",
    description="Answer a question using only matching DRIFT insight evidence.",
)
async def chat(request: ChatRequest) -> ChatResponse:
    insights = app.state.insight_store.search(request.question, limit=3)
    if not insights:
        raise HTTPException(status_code=404, detail="No matching DRIFT insights.")
    if settings.mode == "live":
        try:
            answer = await answer_question_with_model(
                request.question,
                insights,
                client=app.state.openai_client,
                spend_guard=app.state.spend_guard,
                max_call_usd=settings.max_call_usd,
                model_call_limiter=app.state.model_call_limiter,
                model_queue_timeout_seconds=settings.model_queue_timeout_seconds,
                resilience=app.state.model_resilience,
            )
        except BudgetExceededError as exc:
            raise HTTPException(status_code=429, detail=str(exc)) from exc
        except (ModelCapacityExceededError, ProviderCircuitOpenError) as exc:
            raise HTTPException(status_code=503, detail=str(exc), headers={"Retry-After": "2"}) from exc
        except Exception as exc:
            raise HTTPException(
                status_code=502,
                detail="The grounded model response could not be completed.",
            ) from exc
        model_used = get_model(Tier.LIVE)
    else:
        answer = answer_question(request.question, insights)
        model_used = "fixture-curated"

    return ChatResponse(
        answer=answer,
        source_citations=sorted({url for item in insights for url in item.source_citations}),
        model_used=model_used,
        grounded_insight_ids=[item.id for item in insights if item.id is not None],
    )

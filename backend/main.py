"""
DRIFT — FastAPI entrypoint.

Endpoints:
  GET  /                  — service metadata and API links
  GET  /briefing         — today's top-N insights
  GET  /search?q=...     — semantic search over accumulated insights
  POST /chat             — chat-over-knowledge (Tier.LIVE)
  GET  /health           — liveness check

Fixture and live-store HTTP adapters are wired here; scheduled live-store
population remains an explicit boundary. The API uses structured request logging
and consistent error handling; DRIFT has no media-generation component.
"""

import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import FileResponse, HTMLResponse

from backend.agents.briefing import (
    answer_question,
    answer_question_with_model,
    build_daily_briefing,
)
from backend.core.budget import BudgetExceededError, SpendGuard
from backend.core.config import settings
from backend.core.live_store import (
    latest_live_insights,
)
from backend.core.live_store import (
    retrieve_live_insights as retrieve_live_store_insights,
)
from backend.core.model_router import Tier, create_async_client, get_model
from backend.core.resilience import (
    CircuitBreaker,
    ModelCallResilience,
    ModelCapacityExceededError,
    ProviderCircuitOpenError,
    RetryPolicy,
)
from backend.core.store import InsightStore
from backend.models.schema import BriefingItem, ChatRequest, ChatResponse, Insight, session_factory


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
    docs_url=None,
    description=(
        "Review-first, claim-grounded release intelligence for GPU/AI-infrastructure teams. "
        "Live endpoints expose only human-reviewed, verifier-passed captures."
    ),
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

_brand_directory = Path(__file__).parent.parent / "assets" / "brand"
_brand_files = {
    "dark": "drift-banner-dark.svg",
    "light": "drift-banner-light.svg",
}


@app.get("/brand/{theme}.svg", include_in_schema=False)
async def brand_asset(theme: str) -> FileResponse:
    """Serve the canonical DRIFT banner used by API documentation."""
    filename = _brand_files.get(theme)
    if filename is None:
        raise HTTPException(status_code=404, detail="Unknown DRIFT brand theme.")
    return FileResponse(_brand_directory / filename, media_type="image/svg+xml")


@app.get("/docs", include_in_schema=False)
async def swagger_ui() -> HTMLResponse:
    """Render Swagger UI beneath the canonical theme-aware DRIFT banner."""
    swagger_html = get_swagger_ui_html(
        openapi_url=app.openapi_url or "/openapi.json",
        title=f"{settings.app_name} API documentation",
    ).body
    brand_header = """
<style>
  .drift-api-brand { background: #edf4ff; padding: 20px max(20px, calc((100vw - 1120px) / 2)); }
  @media (prefers-color-scheme: dark) { .drift-api-brand { background: #061426; } }
  .drift-api-brand picture, .drift-api-brand img { display: block; margin: 0 auto; max-width: 1120px; width: 100%; }
</style>
<header class="drift-api-brand">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="/brand/dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="/brand/light.svg">
    <img src="/brand/light.svg" alt="DRIFT — release intelligence for AI infrastructure">
  </picture>
</header>
"""
    return HTMLResponse(
        bytes(swagger_html).decode("utf-8").replace("<body>", f"<body>{brand_header}", 1)
    )


async def _retrieve_live_insights(query: str, *, limit: int = 5) -> list[Insight]:
    """Open one database session and retrieve cited live-store evidence."""
    async with session_factory() as session:
        return await retrieve_live_store_insights(
            session,
            query,
            client=app.state.openai_client,
            limit=limit,
        )


async def _latest_live_insights(*, limit: int = 5) -> list[Insight]:
    """Load the captured live-store briefing without a new model call."""
    async with session_factory() as session:
        return await latest_live_insights(session, limit=limit)


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
    description=(
        "Rank the most important cited insights for the current briefing. In live mode, "
        "only human-reviewed, verifier-passed captures are eligible."
    ),
)
async def briefing(top_n: int = Query(default=5, ge=1, le=10)) -> list[BriefingItem]:
    if settings.mode == "live":
        try:
            return build_daily_briefing(await _latest_live_insights(limit=top_n), top_n)
        except Exception as exc:
            raise HTTPException(
                status_code=503,
                detail="The live Insight store could not build a briefing.",
            ) from exc
    return build_daily_briefing(app.state.insight_store.all(), top_n)


@app.get(
    "/search",
    tags=["search"],
    summary="Search insights",
    description=(
        "Find reviewed, claim-grounded insights matching a library, release, or risk query."
    ),
)
async def search(q: str = Query(min_length=2, max_length=300)) -> list[Insight]:
    if settings.mode == "live":
        try:
            return await _retrieve_live_insights(q)
        except Exception as exc:
            raise HTTPException(
                status_code=503,
                detail="The live Insight store could not be searched.",
            ) from exc
    return app.state.insight_store.search(q)


@app.post(
    "/chat",
    tags=["chat"],
    summary="Ask grounded question",
    description=(
        "Answer a question using only matching human-reviewed DRIFT insight evidence."
    ),
)
async def chat(request: ChatRequest) -> ChatResponse:
    if settings.mode == "live":
        try:
            insights = await _retrieve_live_insights(request.question, limit=3)
        except Exception as exc:
            raise HTTPException(
                status_code=503,
                detail="The live Insight store could not be searched.",
            ) from exc
    else:
        insights = app.state.insight_store.search(request.question, limit=3)
    if not insights:
        raise HTTPException(status_code=404, detail="No matching DRIFT insights.")
    if settings.mode == "live":
        try:
            grounded = await answer_question_with_model(
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
        answer = grounded.text
        model_used = get_model(Tier.LIVE)
        # The model answers over only the insights it reports grounding in, so
        # cite that subset rather than the whole retrieval window. An empty
        # list is a real signal (e.g. a decline) and must not fabricate
        # citations by falling back to every retrieved insight.
        grounded_ids = set(grounded.grounded_insight_ids)
        cited = [item for item in insights if item.id in grounded_ids]
    else:
        answer = answer_question(request.question, insights)
        model_used = "fixture-curated"
        # The fixture answer concatenates every retrieved insight, so all of
        # them genuinely back it.
        cited = insights

    return ChatResponse(
        answer=answer,
        source_citations=sorted({url for item in cited for url in item.source_citations}),
        model_used=model_used,
        grounded_insight_ids=[item.id for item in cited if item.id is not None],
    )

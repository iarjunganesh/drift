"""A thin async HTTP client over the public DRIFT API.

Each method is a one-to-one call to an existing public endpoint. The client
adds no behaviour of its own beyond request bounds that mirror the API's own
validation (so an assistant gets an immediate, clear message instead of a raw
422) and friendly transport-error text. It never sees a credential.
"""

from __future__ import annotations

from typing import Any

import httpx

# Request bounds mirror the FastAPI contract (backend/main.py). They are a
# courtesy for tool callers; the API remains the authority and re-validates.
TOP_N_MIN = 1
TOP_N_MAX = 10
QUERY_MIN_LEN = 2
QUERY_MAX_LEN = 300
QUESTION_MIN_LEN = 3
QUESTION_MAX_LEN = 2_000


class DriftApiError(RuntimeError):
    """Raised when the DRIFT API is unreachable or returns an error status."""


class DriftApiClient:
    """One-to-one async wrapper over ``/briefing``, ``/search``, and ``/chat``."""

    def __init__(self, base_url: str, timeout_seconds: float) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout_seconds

    async def briefing(self, top_n: int) -> list[dict[str, Any]]:
        """GET /briefing?top_n= — ranked reviewed insights."""
        if not TOP_N_MIN <= top_n <= TOP_N_MAX:
            raise DriftApiError(
                f"top_n must be between {TOP_N_MIN} and {TOP_N_MAX}."
            )
        payload = await self._request("GET", "/briefing", params={"top_n": top_n})
        return list(payload)

    async def search(self, query: str) -> list[dict[str, Any]]:
        """GET /search?q= — cited reviewed insights matching a query."""
        cleaned = query.strip()
        if not QUERY_MIN_LEN <= len(cleaned) <= QUERY_MAX_LEN:
            raise DriftApiError(
                f"query must be between {QUERY_MIN_LEN} and {QUERY_MAX_LEN} characters."
            )
        payload = await self._request("GET", "/search", params={"q": cleaned})
        return list(payload)

    async def ask(self, question: str) -> dict[str, Any] | None:
        """POST /chat — a grounded, cited answer, or ``None`` if nothing matches.

        A 404 from the API is the retrieve-first "no reviewed evidence" signal,
        not an error: the client surfaces it as ``None`` so the tool can decline
        rather than raise.
        """
        cleaned = question.strip()
        if not QUESTION_MIN_LEN <= len(cleaned) <= QUESTION_MAX_LEN:
            raise DriftApiError(
                f"question must be between {QUESTION_MIN_LEN} and "
                f"{QUESTION_MAX_LEN} characters."
            )
        payload = await self._request(
            "POST", "/chat", json={"question": cleaned}, allow_404=True
        )
        if payload is None:
            return None
        return dict(payload)

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        allow_404: bool = False,
    ) -> Any:
        url = f"{self._base_url}{path}"
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as http:
                response = await http.request(method, url, params=params, json=json)
        except httpx.HTTPError as exc:
            raise DriftApiError(
                f"Could not reach the DRIFT API at {self._base_url}. "
                "Check that DRIFT_API_URL points at a running instance."
            ) from exc

        if allow_404 and response.status_code == 404:
            return None
        if response.status_code >= 400:
            raise DriftApiError(
                f"The DRIFT API returned HTTP {response.status_code} for "
                f"{method} {path}."
            )
        return response.json()

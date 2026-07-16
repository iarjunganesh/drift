"""Scout agent: bounded primary-source release-feed ingestion."""

from collections.abc import Iterable, Mapping
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from time import monotonic, sleep
from typing import Any

import feedparser
import httpx
import structlog
import yaml
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config import settings
from backend.core.resilience import RetryPolicy
from backend.models.schema import RawItem, RawItemRow, SourceRow

log = structlog.get_logger(agent="scout")


class FeedFetchError(RuntimeError):
    """A source fetch or parse failure with an explicit retry classification."""

    def __init__(self, message: str, *, retryable: bool) -> None:
        super().__init__(message)
        self.retryable = retryable


def load_sources() -> list[dict]:
    path = Path(settings.sources_config_path)
    with open(path) as f:
        config = yaml.safe_load(f)
    return config["sources"]


def _download_feed(feed_url: str) -> bytes:
    """Download one feed with an explicit transport timeout."""
    try:
        with httpx.Client(
            follow_redirects=True,
            timeout=settings.scout_timeout_seconds,
            headers={"User-Agent": f"DRIFT/{settings.app_version} (+release-intelligence)"},
        ) as client:
            response = client.get(feed_url)
            response.raise_for_status()
            return response.content
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        raise FeedFetchError(
            f"Feed returned HTTP {status}.", retryable=status == 429 or status >= 500
        ) from exc
    except (httpx.TimeoutException, httpx.TransportError) as exc:
        raise FeedFetchError("Feed transport failed.", retryable=True) from exc


def _entry_datetime(entry: Mapping[str, Any]) -> datetime:
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if parsed is not None:
        return datetime(
            year=int(parsed[0]),
            month=int(parsed[1]),
            day=int(parsed[2]),
            hour=int(parsed[3]),
            minute=int(parsed[4]),
            second=int(parsed[5]),
            tzinfo=UTC,
        )

    raw_date = entry.get("published") or entry.get("updated")
    if isinstance(raw_date, str):
        try:
            parsed_date = parsedate_to_datetime(raw_date)
        except (TypeError, ValueError):
            pass
        else:
            return parsed_date.astimezone(UTC) if parsed_date.tzinfo else parsed_date.replace(tzinfo=UTC)

    return datetime.now(UTC)


def _entry_content(entry: Mapping[str, Any]) -> str:
    parts: list[str] = []
    summary = entry.get("summary")
    if summary:
        parts.append(str(summary))
    for content in entry.get("content", []) or []:
        if isinstance(content, Mapping) and content.get("value"):
            parts.append(str(content["value"]))
    return "\n\n".join(parts).strip()


def _parse_feed(source: Mapping[str, Any], payload: bytes) -> list[RawItem]:
    parsed = feedparser.parse(BytesIO(payload))
    entries = list(getattr(parsed, "entries", []))
    if getattr(parsed, "bozo", False):
        raise FeedFetchError("Feed was malformed and could not be trusted.", retryable=False)

    items: list[RawItem] = []
    seen_urls: set[str] = set()
    for entry in entries:
        title = str(entry.get("title", "")).strip()
        url = str(entry.get("link", "")).strip()
        if not title or not url or url in seen_urls:
            continue
        seen_urls.add(url)
        content = _entry_content(entry) or title
        items.append(
            RawItem(
                source_id=str(source["id"]),
                title=title,
                url=url,
                published_at=_entry_datetime(entry),
                raw_content=content,
            )
        )
    return items


def fetch_source(source: dict) -> list[RawItem]:
    """Fetch and normalize one configured Atom/RSS source."""
    feed_url = str(source.get("feed_url", "")).strip()
    if not source.get("id") or not feed_url:
        raise FeedFetchError("Source must define both id and feed_url.", retryable=False)
    return _parse_feed(source, _download_feed(feed_url))


def _fetch_with_retry(source: dict) -> tuple[list[RawItem], int]:
    policy = RetryPolicy(
        timeout_seconds=settings.scout_timeout_seconds,
        max_attempts=settings.scout_max_attempts,
        base_delay_seconds=settings.scout_retry_base_seconds,
        max_delay_seconds=settings.scout_retry_max_seconds,
    )
    for attempt in range(1, policy.max_attempts + 1):
        try:
            return fetch_source(source), attempt
        except FeedFetchError as exc:
            if not exc.retryable or attempt == policy.max_attempts:
                raise
            delay = policy.delay_for(attempt)
            log.warning(
                "scout.fetch.retry",
                source=source.get("id"),
                attempt=attempt,
                delay_seconds=delay,
                error=str(exc),
            )
            sleep(delay)
    raise AssertionError("Scout retry loop exited without returning or raising.")


def run_scout(sources: Iterable[dict] | None = None) -> list[RawItem]:
    """Fetch all configured sources, continuing after bounded source failures."""
    source_list = list(sources) if sources is not None else load_sources()
    all_items: list[RawItem] = []
    for source in source_list:
        started = monotonic()
        try:
            items, attempts = _fetch_with_retry(source)
        except FeedFetchError as exc:
            log.error(
                "scout.fetch.error",
                source=source.get("id"),
                attempts=settings.scout_max_attempts if exc.retryable else 1,
                duration_ms=round((monotonic() - started) * 1000, 2),
                error=str(exc),
            )
            continue
        all_items.extend(items)
        log.info(
            "scout.fetch.complete",
            source=source.get("id"),
            item_count=len(items),
            attempts=attempts,
            duration_ms=round((monotonic() - started) * 1000, 2),
        )
    return all_items


async def store_sources(session: AsyncSession, sources: Iterable[dict]) -> None:
    """Insert configured sources that are not already present."""
    source_list = list(sources)
    source_ids = {str(source["id"]) for source in source_list}
    if not source_ids:
        return
    existing = set(
        (await session.scalars(select(SourceRow.id).where(SourceRow.id.in_(source_ids)))).all()
    )
    session.add_all(
        [
            SourceRow(
                id=str(source["id"]),
                name=str(source.get("name", source["id"])),
                repo=str(source.get("repo", "")),
                feed_url=str(source["feed_url"]),
                category=str(source.get("category", "other")),
            )
            for source in source_list
            if str(source["id"]) not in existing
        ]
    )


async def store_raw_items(
    session: AsyncSession,
    items: Iterable[RawItem],
    *,
    sources: Iterable[dict] | None = None,
) -> int:
    """Persist newly fetched items, deduplicating by canonical source URL."""
    item_list = list(items)
    if not item_list:
        return 0
    await store_sources(session, sources if sources is not None else load_sources())
    urls = {item.url for item in item_list}
    existing = set(
        (await session.scalars(select(RawItemRow.url).where(RawItemRow.url.in_(urls)))).all()
    )
    seen_urls = set(existing)
    new_rows: list[RawItemRow] = []
    for item in item_list:
        if item.url in seen_urls:
            continue
        seen_urls.add(item.url)
        new_rows.append(
            RawItemRow(
                source_id=item.source_id,
                title=item.title,
                url=item.url,
                published_at=item.published_at,
                raw_content=item.raw_content,
                content_sha256=sha256(item.raw_content.encode("utf-8")).hexdigest(),
                fetched_at=item.fetched_at,
            )
        )
    session.add_all(new_rows)
    await session.commit()
    return len(new_rows)


async def load_persisted_raw_items(
    session: AsyncSession,
    urls: Iterable[str],
) -> list[RawItem]:
    """Reload persisted evidence with durable IDs for the Insight contract."""
    url_list = list(dict.fromkeys(urls))
    if not url_list:
        return []
    rows = (
        await session.scalars(select(RawItemRow).where(RawItemRow.url.in_(set(url_list))))
    ).all()
    by_url = {row.url: row for row in rows}
    missing_urls = [url for url in url_list if url not in by_url]
    if missing_urls:
        raise RuntimeError("Persisted raw-item lookup did not return every requested source URL.")
    return [
        RawItem(
            id=by_url[url].id,
            source_id=by_url[url].source_id,
            title=by_url[url].title,
            url=by_url[url].url,
            published_at=by_url[url].published_at,
            raw_content=by_url[url].raw_content,
            fetched_at=by_url[url].fetched_at,
        )
        for url in url_list
    ]


if __name__ == "__main__":  # pragma: no cover - manual CLI convenience path
    items = run_scout()
    print(f"Fetched {len(items)} raw items across {len(load_sources())} sources.")

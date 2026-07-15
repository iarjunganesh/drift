from dataclasses import replace
from datetime import UTC, datetime

import httpx
import pytest

from backend.agents import scout
from backend.core.config import settings
from backend.models.schema import RawItem

ATOM_FEED = b'''<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Example releases</title>
  <entry>
    <title> Release v1.2.0 </title>
    <link rel="alternate" href="https://example.com/releases/1.2.0" />
    <published>Wed, 15 Jul 2026 09:00:00 GMT</published>
    <summary>Important release notes.</summary>
  </entry>
  <entry>
    <title>Duplicate release</title>
    <link rel="alternate" href="https://example.com/releases/1.2.0" />
  </entry>
</feed>
'''


def make_item(url: str) -> RawItem:
    return RawItem(
        source_id="example",
        title="Release",
        url=url,
        published_at=datetime(2026, 7, 15, tzinfo=UTC),
        raw_content="Release notes",
    )


def test_fetch_source_parses_and_deduplicates_feed_entries(monkeypatch) -> None:
    monkeypatch.setattr(scout, "_download_feed", lambda _: ATOM_FEED)

    items = scout.fetch_source({"id": "example", "feed_url": "https://example.com/feed.atom"})

    assert len(items) == 1
    assert items[0].source_id == "example"
    assert items[0].title == "Release v1.2.0"
    assert items[0].url == "https://example.com/releases/1.2.0"
    assert items[0].published_at == datetime(2026, 7, 15, 9, tzinfo=UTC)
    assert items[0].raw_content == "Important release notes."


def test_fetch_source_rejects_malformed_empty_feed(monkeypatch) -> None:
    monkeypatch.setattr(scout, "_download_feed", lambda _: b"not an xml feed")

    with pytest.raises(scout.FeedFetchError, match="malformed") as failure:
        scout.fetch_source({"id": "example", "feed_url": "https://example.com/feed.atom"})

    assert failure.value.retryable is False


def test_download_feed_classifies_timeout_as_retryable(monkeypatch) -> None:
    class TimeoutClient:
        def __enter__(self):
            return self

        def __exit__(self, *_args) -> None:
            return None

        def get(self, _url: str):
            raise httpx.TimeoutException("timed out")

    monkeypatch.setattr(scout.httpx, "Client", lambda **_kwargs: TimeoutClient())

    with pytest.raises(scout.FeedFetchError) as failure:
        scout._download_feed("https://example.com/feed.atom")

    assert failure.value.retryable is True


def test_download_feed_returns_successful_payload(monkeypatch) -> None:
    class Response:
        content = ATOM_FEED

        def raise_for_status(self) -> None:
            return None

    class Client:
        def __enter__(self):
            return self

        def __exit__(self, *_args) -> None:
            return None

        def get(self, _url: str) -> Response:
            return Response()

    monkeypatch.setattr(scout.httpx, "Client", lambda **_kwargs: Client())

    assert scout._download_feed("https://example.com/feed.atom") == ATOM_FEED


def test_download_feed_classifies_http_status(monkeypatch) -> None:
    response = httpx.Response(503, request=httpx.Request("GET", "https://example.com/feed.atom"))

    class Client:
        def __enter__(self):
            return self

        def __exit__(self, *_args) -> None:
            return None

        def get(self, _url: str) -> httpx.Response:
            return response

    monkeypatch.setattr(scout.httpx, "Client", lambda **_kwargs: Client())

    with pytest.raises(scout.FeedFetchError) as failure:
        scout._download_feed("https://example.com/feed.atom")

    assert failure.value.retryable is True


def test_entry_datetime_supports_structured_and_text_dates() -> None:
    structured = scout._entry_datetime({"published_parsed": (2026, 7, 15, 9, 0, 0)})
    aware = scout._entry_datetime({"published": "Wed, 15 Jul 2026 09:00:00 GMT"})
    naive = scout._entry_datetime({"published": "Wed, 15 Jul 2026 09:00:00"})
    invalid = scout._entry_datetime({"published": "not a date"})

    assert structured == datetime(2026, 7, 15, 9, tzinfo=UTC)
    assert aware == structured
    assert naive == structured
    assert invalid.tzinfo is UTC


def test_entry_content_reads_content_values() -> None:
    content = scout._entry_content(
        {"summary": "Summary", "content": [{"value": "Full content"}, {"value": ""}]}
    )

    assert content == "Summary\n\nFull content"


def test_fetch_source_rejects_missing_identity() -> None:
    with pytest.raises(scout.FeedFetchError, match="id and feed_url") as failure:
        scout.fetch_source({"id": "", "feed_url": ""})

    assert failure.value.retryable is False


def test_run_scout_retries_transient_source_and_continues(monkeypatch, tmp_path) -> None:
    sources_file = tmp_path / "sources.yaml"
    sources_file.write_text(
        "sources:\n  - id: flaky\n    feed_url: https://example.com/flaky\n"
        "  - id: healthy\n    feed_url: https://example.com/healthy\n",
        encoding="utf-8",
    )
    candidate = replace(
        settings,
        sources_config_path=str(sources_file),
        scout_max_attempts=2,
        scout_retry_base_seconds=0.01,
        scout_retry_max_seconds=0.01,
    )
    monkeypatch.setattr(scout, "settings", candidate)
    monkeypatch.setattr(scout, "sleep", lambda _: None)
    calls: dict[str, int] = {"flaky": 0, "healthy": 0}

    def fake_fetch(source: dict) -> list[RawItem]:
        source_id = source["id"]
        calls[source_id] += 1
        if source_id == "flaky":
            raise scout.FeedFetchError("temporary outage", retryable=True)
        return [make_item("https://example.com/healthy/1")]

    monkeypatch.setattr(scout, "fetch_source", fake_fetch)

    items = scout.run_scout()

    assert calls == {"flaky": 2, "healthy": 1}
    assert [item.url for item in items] == ["https://example.com/healthy/1"]


def test_fetch_with_retry_defensive_assertion(monkeypatch) -> None:
    class EmptyRetryPolicy:
        max_attempts = 0

    monkeypatch.setattr(scout, "RetryPolicy", lambda **_kwargs: EmptyRetryPolicy())

    with pytest.raises(AssertionError, match="retry loop"):
        scout._fetch_with_retry({"id": "example", "feed_url": "https://example.com/feed.atom"})


class FakeScalarResult:
    def __init__(self, values: list[str]) -> None:
        self.values = values

    def all(self) -> list[str]:
        return self.values


class FakeSession:
    def __init__(self) -> None:
        self.added: list[object] = []
        self.commits = 0

    async def scalars(self, _statement):
        return FakeScalarResult([])

    def add_all(self, rows: list[object]) -> None:
        self.added.extend(rows)

    async def commit(self) -> None:
        self.commits += 1


@pytest.mark.asyncio
async def test_store_raw_items_persists_new_urls(monkeypatch) -> None:
    async def skip_source_sync(_session, _sources) -> None:
        return None

    monkeypatch.setattr(scout, "store_sources", skip_source_sync)
    session = FakeSession()

    item = make_item("https://example.com/1")
    count = await scout.store_raw_items(session, [item, item])

    assert count == 1
    assert session.commits == 1
    assert session.added[0].url == "https://example.com/1"
    assert len(session.added[0].content_sha256) == 64


@pytest.mark.asyncio
async def test_store_sources_adds_configured_sources() -> None:
    session = FakeSession()
    sources = [
        {
            "id": "example",
            "name": "Example",
            "repo": "owner/example",
            "feed_url": "https://example.com/feed.atom",
            "category": "runtime",
        }
    ]

    await scout.store_sources(session, sources)

    assert len(session.added) == 1
    assert session.added[0].id == "example"


@pytest.mark.asyncio
async def test_store_sources_skips_empty_input() -> None:
    session = FakeSession()

    await scout.store_sources(session, [])

    assert session.added == []


@pytest.mark.asyncio
async def test_store_raw_items_skips_empty_input() -> None:
    session = FakeSession()

    assert await scout.store_raw_items(session, []) == 0
    assert session.commits == 0


@pytest.mark.asyncio
async def test_load_persisted_raw_items_preserves_durable_ids() -> None:
    row = scout.RawItemRow(
        id=7,
        source_id="example",
        title="Release",
        url="https://example.com/1",
        published_at=datetime(2026, 7, 15, tzinfo=UTC),
        raw_content="Evidence",
        fetched_at=datetime(2026, 7, 15, tzinfo=UTC),
    )

    class LoadedSession:
        async def scalars(self, _statement):
            return FakeScalarResult([row])

    loaded = await scout.load_persisted_raw_items(LoadedSession(), [row.url])

    assert loaded[0].id == 7
    assert loaded[0].raw_content == "Evidence"


@pytest.mark.asyncio
async def test_load_persisted_raw_items_rejects_missing_rows() -> None:
    class EmptySession:
        async def scalars(self, _statement):
            return FakeScalarResult([])

    with pytest.raises(RuntimeError, match="did not return"):
        await scout.load_persisted_raw_items(EmptySession(), ["https://example.com/missing"])


@pytest.mark.asyncio
async def test_load_persisted_raw_items_skips_empty_urls() -> None:
    assert await scout.load_persisted_raw_items(FakeSession(), []) == []

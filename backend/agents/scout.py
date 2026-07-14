"""
Scout agent — Day 1.

Fetches raw release items from every source in sources.yaml (GitHub Atom
release feeds), parses them, and stores them as RawItem rows.

No LLM calls here — this is pure ingestion. Keep it that way; classification
belongs in the Synthesizer agent (Day 2), not here.

Codex: implement fetch_source() using feedparser against feed_url,
implement store_raw_items() against the DB session, and wire up
run_scout() to iterate all sources in sources.yaml with basic retry/backoff.
Log every fetch (source, item count, duration) via structlog, following the
bankers-wrapped logging pattern.
"""

from pathlib import Path

import yaml

from backend.core.config import settings
from backend.models.schema import RawItem


def load_sources() -> list[dict]:
    path = Path(settings.sources_config_path)
    with open(path) as f:
        config = yaml.safe_load(f)
    return config["sources"]


def fetch_source(source: dict) -> list[RawItem]:
    """
    Fetch and parse a single source's Atom feed.
    TODO(codex): implement with feedparser.parse(source["feed_url"]),
    map entries -> RawItem, dedupe against already-seen entries by URL.
    """
    raise NotImplementedError  # pragma: no cover - explicit live-ingestion boundary


def run_scout() -> list[RawItem]:
    """Fetch all configured sources, return the combined raw item list."""
    sources = load_sources()
    all_items: list[RawItem] = []
    for source in sources:
        items = fetch_source(source)
        all_items.extend(items)
    return all_items


if __name__ == "__main__":  # pragma: no cover - manual CLI convenience path
    items = run_scout()
    print(f"Fetched {len(items)} raw items across {len(load_sources())} sources.")

#!/usr/bin/env python3
"""Backfill upstream_release_type for already-reviewed live Insights.

The capture that produced the current Insights kept only the single latest
release per source (see run_capture's default per_source_limit=1), so no
prior-version data was ever persisted. This script re-fetches each source's
public GitHub releases.atom feed fresh (free, no model call, no new capture)
to find the release immediately before the one already cited, then classifies
the bump with backend.core.versioning's deterministic diff — never a model
guess. A value is only ever written when the existing column is "unknown" and
the diff resolves to something else; explicit source-stated values (e.g.
vLLM's self-declared "patch") are never overwritten.

Usage:
    uv run python scripts/backfill_upstream_release_type.py           # dry run
    uv run python scripts/backfill_upstream_release_type.py --apply   # writes
"""

from __future__ import annotations

import argparse
import asyncio
import re
from dataclasses import dataclass

from sqlalchemy import select

from backend.agents.scout import fetch_source
from backend.core.versioning import classify_version_bump, tag_prefix
from backend.models.schema import (
    InsightRow,
    PublicationStatus,
    UpstreamReleaseType,
    VerificationStatus,
    session_factory,
)

_RELEASE_URL = re.compile(r"github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/releases/tag/(?P<tag>[^/?#]+)")


@dataclass(frozen=True)
class BackfillRow:
    insight_id: int
    library: str
    current_tag: str
    previous_tag: str | None
    existing: str
    computed: str


def _find_previous_tag(owner: str, repo: str, current_tag: str) -> str | None:
    """Re-fetch the repo's public release feed and return the same-product-line tag before current_tag.

    Repos that tag multiple release lines in one feed (e.g. NVIDIA/nccl also
    tags nccl4py) would otherwise pair a release with an unrelated sibling
    package's tag, so candidates are restricted to a matching tag_prefix.
    """
    current_prefix = tag_prefix(current_tag)
    feed_url = f"https://github.com/{owner}/{repo}/releases.atom"
    items = fetch_source({"id": f"{owner}/{repo}", "feed_url": feed_url})
    ordered = sorted(items, key=lambda item: item.published_at, reverse=True)
    tags: list[str] = []
    for item in ordered:
        match = _RELEASE_URL.search(item.url)
        if match and tag_prefix(match.group("tag")) == current_prefix:
            tags.append(match.group("tag"))
    try:
        index = tags.index(current_tag)
    except ValueError:
        return None
    return tags[index + 1] if index + 1 < len(tags) else None


def _first_release_citation(source_citations: list[str]) -> tuple[str, str, str] | None:
    """Return (owner, repo, tag) from the first GitHub release citation, or None."""
    for url in source_citations:
        match = _RELEASE_URL.search(url)
        if match:
            return match.group("owner"), match.group("repo"), match.group("tag")
    return None


async def compute_backfill() -> list[BackfillRow]:
    """Read reviewed Insights and compute the deterministic diff for each, without writing."""
    async with session_factory() as session:
        statement = select(InsightRow).where(
            InsightRow.publication_status == PublicationStatus.REVIEWED.value,
            InsightRow.verification_status == VerificationStatus.PASSED.value,
        )
        rows = list((await session.scalars(statement)).all())
        results: list[BackfillRow] = []
        for row in rows:
            citation = _first_release_citation(row.source_citations)
            if citation is None:
                continue
            owner, repo, current_tag = citation
            previous_tag = _find_previous_tag(owner, repo, current_tag)
            computed = classify_version_bump(current_tag, previous_tag)
            results.append(
                BackfillRow(
                    insight_id=row.id,
                    library=", ".join(row.affected_libraries),
                    current_tag=current_tag,
                    previous_tag=previous_tag,
                    existing=row.upstream_release_type,
                    computed=computed.value,
                )
            )
        return results


async def apply_backfill(rows: list[BackfillRow]) -> int:
    """Write computed values, but only where the existing column is still 'unknown'."""
    writable = [
        row for row in rows if row.existing == UpstreamReleaseType.UNKNOWN.value and row.computed != UpstreamReleaseType.UNKNOWN.value
    ]
    if not writable:
        return 0
    async with session_factory() as session:
        statement = select(InsightRow).where(InsightRow.id.in_([row.insight_id for row in writable]))
        db_rows = {row.id: row for row in (await session.scalars(statement)).all()}
        for row in writable:
            db_rows[row.insight_id].upstream_release_type = row.computed
        await session.commit()
    return len(writable)


def _print_table(rows: list[BackfillRow]) -> None:
    print(f"{'ID':<4} {'Library':<30} {'Current':<14} {'Previous':<14} {'Existing':<10} {'Computed':<10}")
    print("-" * 84)
    for row in rows:
        print(
            f"{row.insight_id:<4} {row.library[:30]:<30} {row.current_tag:<14} "
            f"{(row.previous_tag or '(none found)'):<14} {row.existing:<10} {row.computed:<10}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--apply", action="store_true", help="Write computed values (default: dry run only).")
    args = parser.parse_args()
    asyncio.run(_run(apply=args.apply))


async def _run(*, apply: bool) -> None:
    """Run compute (and optionally apply) on one event loop, so the pooled connection stays valid."""
    rows = await compute_backfill()
    if not rows:
        print("No reviewed Insights with a GitHub release citation were found.")
        return
    _print_table(rows)

    if not apply:
        print("\nDry run only. Re-run with --apply to write the computed values.")
        return
    written = await apply_backfill(rows)
    print(f"\nWrote {written} value(s) (only rows that were 'unknown' and resolved to something else).")


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    main()

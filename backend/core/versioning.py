"""Deterministic upstream version-bump classification.

This never asks a model to guess a release's shape from its version number —
that inference is unreliable (a bare "2.30.7" does not by itself prove a
patch bump happened). Instead it mechanically diffs two version strings that
both trace back to the same primary source (a repo's own release tags), the
same way character offsets are computed from claim evidence. When either
string cannot be parsed, or there is no prior version to diff against, the
result is UNKNOWN — the same conservative default the model itself uses when
the upstream text does not declare its own release type.
"""

import re
from dataclasses import dataclass

from backend.models.schema import UpstreamReleaseType

_PRERELEASE_TOKEN = re.compile(r"(?:rc|alpha|beta|dev|pre)\d*$", re.IGNORECASE)
_PRERELEASE_SPLIT = re.compile(r"(?:rc|alpha|beta|dev|pre)", re.IGNORECASE)
_VERSION_START = re.compile(r"\d+\.\d+")


@dataclass(frozen=True)
class ParsedVersion:
    """A version tag reduced to its comparable numeric components."""

    major: int
    minor: int
    patch: int | None
    build: int | None
    prerelease: bool


def tag_prefix(tag: str) -> str | None:
    """Return the text before the first digit (``jax-v`` from ``jax-v0.11.0``).

    Some repos tag multiple release lines in one feed (a core project plus a
    sub-package, e.g. ``v2.30.7-1`` alongside ``nccl4py-v0.3.1``). Matching
    prefixes keeps a version diff comparing the same product line instead of
    two unrelated ones. Returns None if the tag has no digit at all.
    """
    digit_match = _VERSION_START.search(tag)
    return tag[: digit_match.start()] if digit_match is not None else None


def parse_version(tag: str) -> ParsedVersion | None:
    """Parse a release tag into comparable components, or None if ambiguous.

    Accepts any prefix before the first digit (``v2.30.7-1``, ``jax-v0.11.0``)
    and reads up to four dot/hyphen-separated integers as
    major.minor.patch.build. A trailing rc/alpha/beta/dev/pre token marks the
    tag as a pre-release regardless of its numeric part.
    """
    digit_match = _VERSION_START.search(tag)
    if digit_match is None:
        return None
    body = tag[digit_match.start() :]

    prerelease = bool(_PRERELEASE_TOKEN.search(body))
    numeric_body = _PRERELEASE_SPLIT.split(body)[0].rstrip(".-")

    parts = [part for part in re.split(r"[.\-]", numeric_body) if part != ""]
    try:
        numbers = [int(part) for part in parts]
    except ValueError:
        return None

    major, minor = numbers[0], numbers[1]
    patch = numbers[2] if len(numbers) > 2 else None
    build = numbers[3] if len(numbers) > 3 else None
    return ParsedVersion(major=major, minor=minor, patch=patch, build=build, prerelease=prerelease)


def classify_bump(current: ParsedVersion, previous: ParsedVersion) -> UpstreamReleaseType:
    """Classify the change from `previous` to `current` by comparing components."""
    if current.prerelease:
        return UpstreamReleaseType.PRE_RELEASE
    if current.major != previous.major:
        return UpstreamReleaseType.MAJOR
    if current.minor != previous.minor:
        return UpstreamReleaseType.MINOR
    if (current.patch or 0) != (previous.patch or 0):
        return UpstreamReleaseType.PATCH
    if (current.build or 0) != (previous.build or 0):
        return UpstreamReleaseType.PATCH
    return UpstreamReleaseType.UNKNOWN


def classify_version_bump(current_tag: str, previous_tag: str | None) -> UpstreamReleaseType:
    """Diff two release tags of the same repo; UNKNOWN if either side is unusable."""
    if not previous_tag:
        return UpstreamReleaseType.UNKNOWN
    current = parse_version(current_tag)
    previous = parse_version(previous_tag)
    if current is None or previous is None:
        return UpstreamReleaseType.UNKNOWN
    return classify_bump(current, previous)

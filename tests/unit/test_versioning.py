import pytest

from backend.core.versioning import (
    ParsedVersion,
    classify_bump,
    classify_version_bump,
    parse_version,
    tag_prefix,
)
from backend.models.schema import UpstreamReleaseType


@pytest.mark.parametrize(
    ("tag", "expected"),
    [
        ("v2.30.7-1", ParsedVersion(major=2, minor=30, patch=7, build=1, prerelease=False)),
        ("jax-v0.11.0", ParsedVersion(major=0, minor=11, patch=0, build=None, prerelease=False)),
        ("v11.1", ParsedVersion(major=11, minor=1, patch=None, build=None, prerelease=False)),
        ("v5.14.1", ParsedVersion(major=5, minor=14, patch=1, build=None, prerelease=False)),
        ("v0.25.1", ParsedVersion(major=0, minor=25, patch=1, build=None, prerelease=False)),
        ("v1.2.0-rc1", ParsedVersion(major=1, minor=2, patch=0, build=None, prerelease=True)),
        ("v1.2.0-alpha", ParsedVersion(major=1, minor=2, patch=0, build=None, prerelease=True)),
        ("v2.0.0.dev0", ParsedVersion(major=2, minor=0, patch=0, build=None, prerelease=True)),
    ],
)
def test_parse_version_reads_components(tag: str, expected: ParsedVersion) -> None:
    assert parse_version(tag) == expected


@pytest.mark.parametrize(
    "tag",
    [
        "nightly",
        "v11",
        "release-candidate",
        "",
        "v.abc.def",
        "v1.2x.3",
    ],
)
def test_parse_version_returns_none_for_unparseable_tags(tag: str) -> None:
    assert parse_version(tag) is None


def test_classify_bump_detects_major() -> None:
    current = parse_version("v3.0.0")
    previous = parse_version("v2.9.5")
    assert current is not None and previous is not None
    assert classify_bump(current, previous) is UpstreamReleaseType.MAJOR


def test_classify_bump_detects_minor() -> None:
    current = parse_version("jax-v0.11.0")
    previous = parse_version("jax-v0.10.4")
    assert current is not None and previous is not None
    assert classify_bump(current, previous) is UpstreamReleaseType.MINOR


def test_classify_bump_detects_patch() -> None:
    current = parse_version("v2.30.7-1")
    previous = parse_version("v2.30.6-1")
    assert current is not None and previous is not None
    assert classify_bump(current, previous) is UpstreamReleaseType.PATCH


def test_classify_bump_treats_build_only_change_as_patch() -> None:
    current = parse_version("v2.30.7-2")
    previous = parse_version("v2.30.7-1")
    assert current is not None and previous is not None
    assert classify_bump(current, previous) is UpstreamReleaseType.PATCH


def test_classify_bump_detects_prerelease_regardless_of_numbers() -> None:
    current = parse_version("v2.30.7-rc1")
    previous = parse_version("v2.30.6-1")
    assert current is not None and previous is not None
    assert classify_bump(current, previous) is UpstreamReleaseType.PRE_RELEASE


def test_classify_bump_returns_unknown_for_identical_versions() -> None:
    current = parse_version("v11.1")
    previous = parse_version("v11.1")
    assert current is not None and previous is not None
    assert classify_bump(current, previous) is UpstreamReleaseType.UNKNOWN


def test_classify_version_bump_end_to_end() -> None:
    assert classify_version_bump("v2.30.7-1", "v2.30.6-1") is UpstreamReleaseType.PATCH


def test_classify_version_bump_returns_unknown_without_previous() -> None:
    assert classify_version_bump("v11.1", None) is UpstreamReleaseType.UNKNOWN
    assert classify_version_bump("v11.1", "") is UpstreamReleaseType.UNKNOWN


def test_classify_version_bump_returns_unknown_for_unparseable_current() -> None:
    assert classify_version_bump("nightly", "v11.1") is UpstreamReleaseType.UNKNOWN


def test_classify_version_bump_returns_unknown_for_unparseable_previous() -> None:
    assert classify_version_bump("v11.1", "nightly") is UpstreamReleaseType.UNKNOWN


@pytest.mark.parametrize(
    ("tag", "expected"),
    [
        ("v2.30.7-1", "v"),
        ("jax-v0.11.0", "jax-v"),
        ("nccl4py-v0.3.1", "nccl4py-v"),
        ("nightly", None),
    ],
)
def test_tag_prefix(tag: str, expected: str | None) -> None:
    assert tag_prefix(tag) == expected


def test_tag_prefix_distinguishes_sibling_release_lines() -> None:
    assert tag_prefix("v2.30.7-1") != tag_prefix("nccl4py-v0.3.1")

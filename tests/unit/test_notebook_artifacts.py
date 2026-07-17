import json
from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

_RESULTS_NOTEBOOKS = sorted(
    (REPOSITORY_ROOT / "notebooks").glob("drift_manual_run.*.results.ipynb")
)


def test_results_notebooks_exist() -> None:
    # Guard against the glob silently matching nothing (e.g. a rename), which
    # would make the parametrized boundary test vacuously pass.
    names = {path.name for path in _RESULTS_NOTEBOOKS}
    assert {
        "drift_manual_run.luna.results.ipynb",
        "drift_manual_run.sol.results.ipynb",
        "drift_manual_run.terra.results.ipynb",
    } <= names


@pytest.mark.parametrize(
    "notebook_path", _RESULTS_NOTEBOOKS, ids=lambda path: path.name
)
def test_results_notebook_is_display_only_and_has_no_operator_config(
    notebook_path: Path,
) -> None:
    notebook = json.loads(notebook_path.read_text(encoding="utf-8"))

    assert notebook["cells"]
    assert all(cell["cell_type"] == "markdown" for cell in notebook["cells"])
    rendered_text = "\n".join("".join(cell["source"]) for cell in notebook["cells"])
    for forbidden in (
        "DATABASE_URL",
        "DRIFT_DATABASE_PUBLIC_HOST",
        "DRIFT_DATABASE_PUBLIC_PORT",
        "OPENAI_API_KEY",
        "OPENAI_ADMIN_KEY",
        "CONFIRM_CAPTURE",
        "PUBLISH_IDS",
        "ARCHIVE_IDS",
        "REVIEW_NOTES",
        "proxy.rlwy.net",
    ):
        assert forbidden not in rendered_text

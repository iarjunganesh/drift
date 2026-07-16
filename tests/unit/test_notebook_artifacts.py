import json
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def test_results_notebook_is_display_only_and_has_no_operator_config() -> None:
    notebook = json.loads(
        (REPOSITORY_ROOT / "notebooks" / "drift_manual_run.results.ipynb").read_text(
            encoding="utf-8"
        )
    )

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

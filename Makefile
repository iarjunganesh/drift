.PHONY: install dev test lint type-check ci demo clean frontend-install frontend-build

install:
	uv sync --locked --group dev

dev:
	uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

test:
	uv run pytest tests --cov=backend --cov-report=term-missing --cov-fail-under=100

lint:
	uv run ruff check backend tests

type-check:
	uv run mypy backend

frontend-install:
	npm --prefix frontend ci

frontend-build:
	npm --prefix frontend run build

ci: lint type-check test frontend-install frontend-build

demo:
	uv run uvicorn backend.main:app --host 0.0.0.0 --port 8000

clean:
	uv run python -c "import shutil; from pathlib import Path; [shutil.rmtree(p, ignore_errors=True) for p in Path('.').rglob('__pycache__')]; [p.unlink(missing_ok=True) for p in Path('.').glob('coverage*')]"

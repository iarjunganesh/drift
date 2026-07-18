.PHONY: install install-integrations dev migrate test test-integrations lint type-check ci demo clean frontend-install frontend-build

install:
	uv sync --locked --group dev

install-integrations:
	uv sync --locked --group integrations

dev:
	uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

migrate:
	uv run alembic upgrade head

test:
	uv run pytest tests --cov=backend --cov-report=term-missing --cov-fail-under=100

# The MCP integration tests run outside the backend coverage gate with their own
# mocked-HTTP coverage (ADR-011). `-o addopts=` drops the backend --cov flags the
# default run injects, so only integrations coverage is measured.
test-integrations:
	uv run --group integrations pytest integrations -o addopts= --cov=integrations --cov-report=term-missing

lint:
	uv run ruff check backend tests integrations

type-check:
	uv run --group integrations mypy backend integrations

frontend-install:
	npm --prefix frontend ci

frontend-build:
	npm --prefix frontend run build

ci: lint type-check test test-integrations frontend-install frontend-build

demo:
	uv run uvicorn backend.main:app --host 0.0.0.0 --port 8000

clean:
	uv run python -c "import shutil; from pathlib import Path; [shutil.rmtree(p, ignore_errors=True) for p in Path('.').rglob('__pycache__')]; [p.unlink(missing_ok=True) for p in Path('.').glob('coverage*')]"

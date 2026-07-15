FROM ghcr.io/astral-sh/uv:0.9.22 AS uv

FROM python:3.14-slim

WORKDIR /app

COPY --from=uv /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PORT=8000
ENV PATH="/app/.venv/bin:${PATH}"

COPY pyproject.toml uv.lock ./
COPY README.md ./
COPY backend/ ./backend/
COPY alembic.ini ./
COPY migrations/ ./migrations/

RUN uv sync --frozen --no-dev --no-editable
RUN chown -R 10001:10001 /app

USER 10001

EXPOSE 8000

CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000} 2>&1"]

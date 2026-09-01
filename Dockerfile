# ClubSteward — one image, all deployment targets (laptop / VM / AWS / club-owned box)
FROM python:3.12-slim AS base
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY clubsteward/ clubsteward/
COPY webapp/ webapp/
COPY clubs/ clubs/
COPY demo/ demo/
COPY scripts/ scripts/

# 0.0.0.0 inside the container is required for port publishing (-p).
# If you publish beyond localhost, set CLUBSTEWARD_WEB_TOKEN (see docs/HOSTING.md).
ENV HOST=0.0.0.0 PORT=8000
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "clubsteward.web:app", "--host", "0.0.0.0", "--port", "8000"]

FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

ENV UV_NO_DEV=1 \
    UV_LINK_MODE=copy

COPY . .

RUN uv sync --frozen --all-packages --no-dev

EXPOSE 8000

CMD ["uv", "run", "--no-dev", "--frozen", "uvicorn", "ceo_api.main:app", "--host", "0.0.0.0", "--port", "8000"]

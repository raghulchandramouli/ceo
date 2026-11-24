FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

ENV UV_NO_DEV=1 \
    UV_LINK_MODE=copy

COPY . .

RUN uv sync --frozen --all-packages --no-dev

CMD ["uv", "run", "--no-dev", "--frozen", "python", "-m", "ceo_workers"]

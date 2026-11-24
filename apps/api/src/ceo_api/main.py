"""App factory and OpenAPI export."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from ceo_api.routers import brain, connectors, tenants, users
from ceo_api.webhooks import slack


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    yield


def create_app() -> FastAPI:
    application = FastAPI(title="Company Brain API", version="0.0.0", lifespan=lifespan)
    application.include_router(tenants.router)
    application.include_router(users.router)
    application.include_router(connectors.router)
    application.include_router(brain.router)
    application.include_router(slack.router)

    @application.get("/health", tags=["health"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return application


app = create_app()

import pytest
from typing import AsyncGenerator, Generator
from fastapi import FastAPI
from httpx import AsyncClient
from asgi_lifespan import LifespanManager

@pytest.fixture(scope="session")
def app() -> FastAPI:
    from main import app
    return app

@pytest.fixture(scope="session")
async def async_client(app: FastAPI) -> AsyncGenerator:
    async with LifespanManager(app):
        async with AsyncClient(
            app=app,
            base_url="http://test",
            follow_redirects=True
        ) as client:
            yield client
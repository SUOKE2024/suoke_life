"""Pytest configuration and fixtures."""

import asyncio
from collections.abc import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from look_service.api.app import create_app
from look_service.core.config import settings


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def app():
    """Create FastAPI app for testing."""
    # Override settings for testing
    settings.testing = True
    settings.database.postgres_db = "test_look_service"
    settings.database.redis_db = 1

    return create_app()


@pytest.fixture
def client(app) -> TestClient:
    """Create test client."""
    return TestClient(app)


@pytest.fixture
async def async_client(app) -> AsyncGenerator[AsyncClient]:
    """Create async test client."""
    async with AsyncClient(base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_image_data() -> bytes:
    """Create sample image data for testing."""
    # Create a 100x100 pixel PNG image to meet minimum size requirements
    import io

    from PIL import Image

    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    return img_bytes.getvalue()


@pytest.fixture
def invalid_image_data() -> bytes:
    """Create invalid image data for testing."""
    return b"not an image"

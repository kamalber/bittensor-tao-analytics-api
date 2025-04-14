import sys
import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
import os

# Mark as testing environment
os.environ["PYTEST_CURRENT_TEST"] = "True"

# Now import app modules
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
from app.db import get_db_session, async_session
from app.services.cache_service import cache, RedisCache

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def test_db_session():
    """Create a test database session with a mock."""
    mock_session = AsyncMock()
    mock_session.add = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()
    mock_session.get = AsyncMock()
    return mock_session

@pytest.fixture
def override_get_db(test_db_session):
    """Override the get_db dependency to use the test session."""
    async def _override_get_db():
        yield test_db_session

    # Also patch the async_session function which might be called directly
    with patch("app.db.async_session", return_value=AsyncMock()):
        yield _override_get_db

@pytest.fixture
def mock_redis():
    """Mock Redis cache for testing."""
    redis_mock = AsyncMock()
    redis_mock.get = AsyncMock(return_value=None)
    redis_mock.set = AsyncMock(return_value=True)
    redis_mock.delete = AsyncMock(return_value=True)

    # Create a mock RedisCache instance
    cache_mock = RedisCache()
    cache_mock.redis = redis_mock
    # Ensure init_redis doesn't try to connect
    cache_mock.init_redis = AsyncMock()
    # Keep original get_dividend_key method
    cache_mock.get_dividend_key = cache.get_dividend_key

    yield cache_mock

@pytest.fixture
def client(override_get_db):
    """Create a test client for the FastAPI app."""
    # Override dependency
    app.dependency_overrides[get_db_session] = override_get_db

    # Mock Redis
    with patch.object(cache, 'init_redis', AsyncMock()), \
         patch.object(cache, 'redis', AsyncMock()):
        # Mock celery
        with patch("app.worker.celery_app.send_task", MagicMock()):
            with TestClient(app) as client:
                yield client

    # Clean up
    app.dependency_overrides = {}

@pytest.fixture
def auth_headers():
    """Return authentication headers for API requests."""
    return {"Authorization": f"Bearer {settings.API_TOKEN}"}

@pytest.fixture
def mock_tao_dividend_result():
    """Mock TAO dividend result."""
    return {
        "netuid": 18,
        "hotkey": "5FFApaS75bv5pJHfAp2FVLBj9ZaXuFDjEypsaBNc1wCfe52v",
        "dividend": 12345.67,
        "cached": False
    }



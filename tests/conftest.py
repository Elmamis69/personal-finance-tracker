"""
Pytest configuration and shared fixtures
"""
import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from httpx import AsyncClient
import asyncio
from typing import AsyncGenerator, Generator

from app.main import app
from app.core.config import settings


# Set test database name
TEST_DB_NAME = "finance_tracker_test"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_db():
    """
    Create a test database and clean it up after each test.
    """
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[TEST_DB_NAME]
    
    yield db
    
    # Cleanup: drop all collections after test
    for collection_name in await db.list_collection_names():
        await db[collection_name].drop()
    
    client.close()


@pytest.fixture(scope="function")
async def async_client() -> AsyncGenerator:
    """
    Create an async HTTP client for testing API endpoints.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def sample_transaction_data():
    """Sample transaction data for testing."""
    return {
        "amount": 150.00,
        "type": "expense",
        "category": "food",
        "description": "Grocery shopping",
        "date": "2025-12-10T10:00:00",
        "tags": ["groceries", "weekly"]
    }


@pytest.fixture
def sample_budget_data():
    """Sample budget data for testing."""
    return {
        "category": "food",
        "limit_amount": 2000.00,
        "period": "monthly",
        "start_date": "2025-12-01T00:00:00",
        "end_date": "2025-12-31T23:59:59",
        "alert_threshold": 0.8
    }

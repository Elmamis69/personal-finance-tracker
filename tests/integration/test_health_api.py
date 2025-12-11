"""
Integration tests for Health endpoints
"""
import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
class TestHealthAPI:
    """Test Health check endpoints."""
    
    async def test_root_endpoint(self, async_client: AsyncClient):
        """Test root endpoint returns welcome message."""
        response = await async_client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Personal Finance Tracker" in data["message"]
    
    async def test_health_check(self, async_client: AsyncClient):
        """Test health check endpoint."""
        response = await async_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    async def test_database_health(self, async_client: AsyncClient):
        """Test database health check endpoint."""
        response = await async_client.get("/health/db")
        
        assert response.status_code == 200
        data = response.json()
        assert "mongodb" in data
        assert "influxdb" in data
        assert data["mongodb"] == "connected"
        assert data["influxdb"] == "connected"

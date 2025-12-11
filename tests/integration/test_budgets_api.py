"""
Integration tests for Budgets API endpoints
"""
import pytest
from datetime import datetime, timedelta
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
class TestBudgetsAPI:
    """Test Budgets API endpoints."""
    
    async def test_create_budget(self, async_client: AsyncClient, sample_budget_data):
        """Test creating a new budget."""
        response = await async_client.post(
            "/api/v1/budgets",
            json=sample_budget_data
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["category"] == sample_budget_data["category"]
        assert data["limit_amount"] == sample_budget_data["limit_amount"]
        assert data["period"] == sample_budget_data["period"]
        assert "id" in data
        assert "created_at" in data
    
    async def test_list_budgets(self, async_client: AsyncClient, sample_budget_data):
        """Test listing budgets."""
        # Create a budget first
        await async_client.post("/api/v1/budgets", json=sample_budget_data)
        
        # List budgets
        response = await async_client.get("/api/v1/budgets")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    async def test_get_budget_by_id(self, async_client: AsyncClient, sample_budget_data):
        """Test getting a specific budget by ID."""
        # Create a budget
        create_response = await async_client.post(
            "/api/v1/budgets",
            json=sample_budget_data
        )
        budget_id = create_response.json()["id"]
        
        # Get the budget
        response = await async_client.get(f"/api/v1/budgets/{budget_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == budget_id
        assert data["limit_amount"] == sample_budget_data["limit_amount"]
    
    async def test_get_budget_not_found(self, async_client: AsyncClient):
        """Test getting a non-existent budget."""
        fake_id = "507f1f77bcf86cd799439011"
        response = await async_client.get(f"/api/v1/budgets/{fake_id}")
        
        assert response.status_code == 404
    
    async def test_update_budget(self, async_client: AsyncClient, sample_budget_data):
        """Test updating a budget."""
        # Create a budget
        create_response = await async_client.post(
            "/api/v1/budgets",
            json=sample_budget_data
        )
        budget_id = create_response.json()["id"]
        
        # Update the budget
        update_data = {
            "limit_amount": 3000.00,
            "alert_threshold": 0.9
        }
        response = await async_client.put(
            f"/api/v1/budgets/{budget_id}",
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["limit_amount"] == 3000.00
        assert data["alert_threshold"] == 0.9
        assert data["id"] == budget_id
    
    async def test_delete_budget(self, async_client: AsyncClient, sample_budget_data):
        """Test deleting a budget."""
        # Create a budget
        create_response = await async_client.post(
            "/api/v1/budgets",
            json=sample_budget_data
        )
        budget_id = create_response.json()["id"]
        
        # Delete the budget
        response = await async_client.delete(f"/api/v1/budgets/{budget_id}")
        
        assert response.status_code == 204
        
        # Verify it's deleted
        get_response = await async_client.get(f"/api/v1/budgets/{budget_id}")
        assert get_response.status_code == 404
    
    async def test_get_budget_progress(self, async_client: AsyncClient, sample_budget_data):
        """Test getting budget progress with transactions."""
        # Create a budget
        create_response = await async_client.post(
            "/api/v1/budgets",
            json=sample_budget_data
        )
        budget_id = create_response.json()["id"]
        
        # Create transactions within budget period
        transaction_data = {
            "amount": 500.00,
            "type": "expense",
            "category": sample_budget_data["category"],
            "description": "Test expense",
            "date": sample_budget_data["start_date"]
        }
        await async_client.post("/api/v1/transactions", json=transaction_data)
        
        # Get budget progress
        response = await async_client.get(f"/api/v1/budgets/{budget_id}/progress")
        
        assert response.status_code == 200
        data = response.json()
        assert "spent_amount" in data
        assert "remaining_amount" in data
        assert "percentage_used" in data
        assert "status" in data
        assert data["spent_amount"] == 500.00
        assert data["remaining_amount"] == 1500.00
    
    async def test_budget_progress_status_safe(self, async_client: AsyncClient, sample_budget_data):
        """Test budget progress status is safe when under threshold."""
        create_response = await async_client.post(
            "/api/v1/budgets",
            json=sample_budget_data
        )
        budget_id = create_response.json()["id"]
        
        # Create small expense (10% of budget)
        transaction_data = {
            "amount": 200.00,
            "type": "expense",
            "category": sample_budget_data["category"],
            "description": "Small expense",
            "date": sample_budget_data["start_date"]
        }
        await async_client.post("/api/v1/transactions", json=transaction_data)
        
        response = await async_client.get(f"/api/v1/budgets/{budget_id}/progress")
        data = response.json()
        
        assert data["status"] == "safe"
        assert data["is_over_budget"] is False
    
    async def test_budget_progress_status_exceeded(self, async_client: AsyncClient, sample_budget_data):
        """Test budget progress status is exceeded when over limit."""
        create_response = await async_client.post(
            "/api/v1/budgets",
            json=sample_budget_data
        )
        budget_id = create_response.json()["id"]
        
        # Create expense that exceeds budget
        transaction_data = {
            "amount": 2500.00,
            "type": "expense",
            "category": sample_budget_data["category"],
            "description": "Large expense",
            "date": sample_budget_data["start_date"]
        }
        await async_client.post("/api/v1/transactions", json=transaction_data)
        
        response = await async_client.get(f"/api/v1/budgets/{budget_id}/progress")
        data = response.json()
        
        assert data["status"] == "exceeded"
        assert data["is_over_budget"] is True
        assert data["remaining_amount"] < 0
    
    async def test_filter_budgets_by_category(self, async_client: AsyncClient):
        """Test filtering budgets by category."""
        # Create food budget
        food_budget = {
            "category": "food",
            "limit_amount": 2000.00,
            "period": "monthly",
            "start_date": datetime.utcnow().isoformat(),
            "end_date": (datetime.utcnow() + timedelta(days=30)).isoformat()
        }
        await async_client.post("/api/v1/budgets", json=food_budget)
        
        # Filter by food category
        response = await async_client.get("/api/v1/budgets?category=food")
        assert response.status_code == 200
        data = response.json()
        assert all(b["category"] == "food" for b in data)
    
    async def test_filter_budgets_by_period(self, async_client: AsyncClient, sample_budget_data):
        """Test filtering budgets by period."""
        await async_client.post("/api/v1/budgets", json=sample_budget_data)
        
        response = await async_client.get("/api/v1/budgets?period=monthly")
        assert response.status_code == 200
        data = response.json()
        assert all(b["period"] == "monthly" for b in data)

"""
Integration tests for Transactions API endpoints
"""
import pytest
from datetime import datetime
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
class TestTransactionsAPI:
    """Test Transactions API endpoints."""
    
    async def test_create_transaction(self, async_client: AsyncClient, sample_transaction_data):
        """Test creating a new transaction."""
        response = await async_client.post(
            "/api/v1/transactions",
            json=sample_transaction_data
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["amount"] == sample_transaction_data["amount"]
        assert data["type"] == sample_transaction_data["type"]
        assert data["category"] == sample_transaction_data["category"]
        assert "id" in data
        assert "created_at" in data
    
    async def test_list_transactions(self, async_client: AsyncClient, sample_transaction_data):
        """Test listing transactions."""
        # Create a transaction first
        await async_client.post("/api/v1/transactions", json=sample_transaction_data)
        
        # List transactions
        response = await async_client.get("/api/v1/transactions")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    async def test_get_transaction_by_id(self, async_client: AsyncClient, sample_transaction_data):
        """Test getting a specific transaction by ID."""
        # Create a transaction
        create_response = await async_client.post(
            "/api/v1/transactions",
            json=sample_transaction_data
        )
        transaction_id = create_response.json()["id"]
        
        # Get the transaction
        response = await async_client.get(f"/api/v1/transactions/{transaction_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == transaction_id
        assert data["amount"] == sample_transaction_data["amount"]
    
    async def test_get_transaction_not_found(self, async_client: AsyncClient):
        """Test getting a non-existent transaction."""
        fake_id = "507f1f77bcf86cd799439011"
        response = await async_client.get(f"/api/v1/transactions/{fake_id}")
        
        assert response.status_code == 404
    
    async def test_update_transaction(self, async_client: AsyncClient, sample_transaction_data):
        """Test updating a transaction."""
        # Create a transaction
        create_response = await async_client.post(
            "/api/v1/transactions",
            json=sample_transaction_data
        )
        transaction_id = create_response.json()["id"]
        
        # Update the transaction
        update_data = {
            "amount": 200.00,
            "description": "Updated description"
        }
        response = await async_client.put(
            f"/api/v1/transactions/{transaction_id}",
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["amount"] == 200.00
        assert data["description"] == "Updated description"
        assert data["id"] == transaction_id
    
    async def test_delete_transaction(self, async_client: AsyncClient, sample_transaction_data):
        """Test deleting a transaction."""
        # Create a transaction
        create_response = await async_client.post(
            "/api/v1/transactions",
            json=sample_transaction_data
        )
        transaction_id = create_response.json()["id"]
        
        # Delete the transaction
        response = await async_client.delete(f"/api/v1/transactions/{transaction_id}")
        
        assert response.status_code == 204
        
        # Verify it's deleted
        get_response = await async_client.get(f"/api/v1/transactions/{transaction_id}")
        assert get_response.status_code == 404
    
    async def test_filter_by_type(self, async_client: AsyncClient):
        """Test filtering transactions by type."""
        # Create income transaction
        income_data = {
            "amount": 1000.00,
            "type": "income",
            "category": "salary",
            "description": "Monthly salary"
        }
        await async_client.post("/api/v1/transactions", json=income_data)
        
        # Create expense transaction
        expense_data = {
            "amount": 50.00,
            "type": "expense",
            "category": "food",
            "description": "Lunch"
        }
        await async_client.post("/api/v1/transactions", json=expense_data)
        
        # Filter by income
        response = await async_client.get("/api/v1/transactions?type=income")
        assert response.status_code == 200
        data = response.json()
        assert all(t["type"] == "income" for t in data)
    
    async def test_filter_by_category(self, async_client: AsyncClient):
        """Test filtering transactions by category."""
        # Create food expense
        food_data = {
            "amount": 50.00,
            "type": "expense",
            "category": "food",
            "description": "Groceries"
        }
        await async_client.post("/api/v1/transactions", json=food_data)
        
        # Filter by food category
        response = await async_client.get("/api/v1/transactions?category=food")
        assert response.status_code == 200
        data = response.json()
        assert all(t["category"] == "food" for t in data)
    
    async def test_pagination(self, async_client: AsyncClient):
        """Test pagination parameters."""
        # Create multiple transactions
        for i in range(5):
            transaction_data = {
                "amount": 10.00 * (i + 1),
                "type": "expense",
                "category": "food",
                "description": f"Transaction {i}"
            }
            await async_client.post("/api/v1/transactions", json=transaction_data)
        
        # Test skip and limit
        response = await async_client.get("/api/v1/transactions?skip=2&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

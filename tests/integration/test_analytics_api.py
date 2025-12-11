"""
Integration tests for Analytics API endpoints
"""
import pytest
from datetime import datetime, timedelta
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
class TestAnalyticsAPI:
    """Test Analytics API endpoints."""
    
    async def test_spending_trend(self, async_client: AsyncClient):
        """Test getting spending trend."""
        # Create some transactions
        base_date = datetime.utcnow()
        for i in range(3):
            transaction_data = {
                "amount": 100.00 * (i + 1),
                "type": "expense",
                "category": "food",
                "description": f"Expense {i}",
                "date": (base_date - timedelta(days=i)).isoformat()
            }
            await async_client.post("/api/v1/transactions", json=transaction_data)
        
        # Get spending trend
        start_date = (base_date - timedelta(days=7)).isoformat()
        end_date = base_date.isoformat()
        
        response = await async_client.get(
            f"/api/v1/analytics/spending-trend?start_date={start_date}&end_date={end_date}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    async def test_category_breakdown(self, async_client: AsyncClient):
        """Test getting category breakdown."""
        # Create transactions in different categories
        categories = ["food", "transport", "entertainment"]
        base_date = datetime.utcnow()
        
        for category in categories:
            transaction_data = {
                "amount": 200.00,
                "type": "expense",
                "category": category,
                "description": f"{category} expense",
                "date": base_date.isoformat()
            }
            await async_client.post("/api/v1/transactions", json=transaction_data)
        
        # Get category breakdown
        start_date = (base_date - timedelta(days=1)).isoformat()
        end_date = base_date.isoformat()
        
        response = await async_client.get(
            f"/api/v1/analytics/category-breakdown?start_date={start_date}&end_date={end_date}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    async def test_income_vs_expenses(self, async_client: AsyncClient):
        """Test getting income vs expenses comparison."""
        base_date = datetime.utcnow()
        
        # Create income transaction
        income_data = {
            "amount": 5000.00,
            "type": "income",
            "category": "salary",
            "description": "Monthly salary",
            "date": base_date.isoformat()
        }
        await async_client.post("/api/v1/transactions", json=income_data)
        
        # Create expense transaction
        expense_data = {
            "amount": 2000.00,
            "type": "expense",
            "category": "food",
            "description": "Groceries",
            "date": base_date.isoformat()
        }
        await async_client.post("/api/v1/transactions", json=expense_data)
        
        # Get income vs expenses
        start_date = (base_date - timedelta(days=1)).isoformat()
        end_date = base_date.isoformat()
        
        response = await async_client.get(
            f"/api/v1/analytics/income-vs-expenses?start_date={start_date}&end_date={end_date}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "income" in data
        assert "expenses" in data
        assert "net" in data
    
    async def test_monthly_comparison(self, async_client: AsyncClient):
        """Test getting monthly comparison."""
        # Create transactions across multiple months
        current_month = datetime.utcnow()
        last_month = current_month - timedelta(days=30)
        
        # Current month transaction
        current_data = {
            "amount": 1500.00,
            "type": "expense",
            "category": "food",
            "description": "Current month expense",
            "date": current_month.isoformat()
        }
        await async_client.post("/api/v1/transactions", json=current_data)
        
        # Last month transaction
        last_data = {
            "amount": 1000.00,
            "type": "expense",
            "category": "food",
            "description": "Last month expense",
            "date": last_month.isoformat()
        }
        await async_client.post("/api/v1/transactions", json=last_data)
        
        # Get monthly comparison
        response = await async_client.get("/api/v1/analytics/monthly-comparison")
        
        assert response.status_code == 200
        data = response.json()
        assert "current_month" in data
        assert "last_month" in data
        assert "change_percentage" in data
    
    async def test_savings_rate(self, async_client: AsyncClient):
        """Test calculating savings rate."""
        base_date = datetime.utcnow()
        
        # Create income
        income_data = {
            "amount": 5000.00,
            "type": "income",
            "category": "salary",
            "description": "Salary",
            "date": base_date.isoformat()
        }
        await async_client.post("/api/v1/transactions", json=income_data)
        
        # Create expenses
        expense_data = {
            "amount": 3000.00,
            "type": "expense",
            "category": "food",
            "description": "Expenses",
            "date": base_date.isoformat()
        }
        await async_client.post("/api/v1/transactions", json=expense_data)
        
        # Get savings rate
        start_date = (base_date - timedelta(days=1)).isoformat()
        end_date = base_date.isoformat()
        
        response = await async_client.get(
            f"/api/v1/analytics/savings-rate?start_date={start_date}&end_date={end_date}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "income" in data
        assert "expenses" in data
        assert "savings" in data
        assert "savings_rate" in data
        # Savings rate should be 40% (2000/5000)
        assert data["savings_rate"] == pytest.approx(40.0, rel=0.1)
    
    async def test_analytics_date_validation(self, async_client: AsyncClient):
        """Test that analytics endpoints validate date parameters."""
        # Missing start_date
        response = await async_client.get("/api/v1/analytics/spending-trend")
        assert response.status_code == 422  # Unprocessable Entity
        
        # Invalid date format
        response = await async_client.get(
            "/api/v1/analytics/spending-trend?start_date=invalid&end_date=invalid"
        )
        assert response.status_code == 422

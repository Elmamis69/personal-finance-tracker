"""
Unit tests for InfluxDB service
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from app.services.influx_service import InfluxService
from app.models.transaction import TransactionType, TransactionCategory


@pytest.mark.unit
class TestInfluxService:
    """Test InfluxDB service methods."""
    
    @pytest.fixture
    def influx_service(self):
        """Create a mock InfluxDB service."""
        with patch('app.services.influx_service.get_influx_client') as mock_client:
            mock_client.return_value = MagicMock()
            service = InfluxService()
            yield service
    
    def test_write_transaction_metric(self, influx_service):
        """Test writing transaction metric to InfluxDB."""
        transaction_data = {
            "id": "test_id",
            "amount": 100.50,
            "type": TransactionType.EXPENSE.value,
            "category": TransactionCategory.FOOD.value,
            "description": "Test transaction",
            "date": datetime.utcnow()
        }
        
        # Mock the write_api
        with patch.object(influx_service.client, 'write_api') as mock_write_api:
            mock_write = MagicMock()
            mock_write_api.return_value = mock_write
            
            influx_service.write_transaction_metric(transaction_data)
            
            # Verify write was called
            assert mock_write.write.called
    
    def test_get_spending_trend_calls_query(self, influx_service):
        """Test that get_spending_trend calls query API."""
        start_date = datetime(2025, 12, 1)
        end_date = datetime(2025, 12, 31)
        
        # Mock the query_api
        with patch.object(influx_service.client, 'query_api') as mock_query_api:
            mock_query = MagicMock()
            mock_query_api.return_value = mock_query
            mock_query.query.return_value = []
            
            result = influx_service.get_spending_trend(start_date, end_date)
            
            # Verify query was called
            assert mock_query.query.called
            assert isinstance(result, list)
    
    def test_get_category_breakdown_calls_query(self, influx_service):
        """Test that get_category_breakdown calls query API."""
        start_date = datetime(2025, 12, 1)
        end_date = datetime(2025, 12, 31)
        
        with patch.object(influx_service.client, 'query_api') as mock_query_api:
            mock_query = MagicMock()
            mock_query_api.return_value = mock_query
            mock_query.query.return_value = []
            
            result = influx_service.get_category_breakdown(start_date, end_date)
            
            assert mock_query.query.called
            assert isinstance(result, list)
    
    def test_get_income_vs_expenses_calls_query(self, influx_service):
        """Test that get_income_vs_expenses calls query API."""
        start_date = datetime(2025, 12, 1)
        end_date = datetime(2025, 12, 31)
        
        with patch.object(influx_service.client, 'query_api') as mock_query_api:
            mock_query = MagicMock()
            mock_query_api.return_value = mock_query
            
            # Mock income query result
            income_record = MagicMock()
            income_record.get_value.return_value = 5000.0
            
            # Mock expenses query result
            expense_record = MagicMock()
            expense_record.get_value.return_value = 3000.0
            
            mock_query.query.side_effect = [
                [MagicMock(records=[income_record])],
                [MagicMock(records=[expense_record])]
            ]
            
            result = influx_service.get_income_vs_expenses(start_date, end_date)
            
            assert mock_query.query.call_count == 2
            assert "income" in result
            assert "expenses" in result

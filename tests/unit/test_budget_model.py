"""
Unit tests for Budget models
"""
import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError

from app.models.budget import (
    BudgetPeriod,
    BudgetStatus,
    BudgetBase,
    BudgetCreate,
    BudgetUpdate,
    BudgetProgress,
    BudgetInDB,
    BudgetResponse
)
from app.models.transaction import TransactionCategory


@pytest.mark.unit
class TestBudgetModels:
    """Test Budget model validation and creation."""
    
    def test_budget_create_valid(self):
        """Test creating a valid budget."""
        start_date = datetime(2025, 12, 1)
        end_date = datetime(2025, 12, 31, 23, 59, 59)
        
        budget = BudgetCreate(
            category=TransactionCategory.FOOD,
            limit_amount=2000.00,
            period=BudgetPeriod.MONTHLY,
            start_date=start_date,
            end_date=end_date,
            alert_threshold=0.8
        )
        
        assert budget.category == TransactionCategory.FOOD
        assert budget.limit_amount == 2000.00
        assert budget.period == BudgetPeriod.MONTHLY
        assert budget.start_date == start_date
        assert budget.end_date == end_date
        assert budget.alert_threshold == 0.8
    
    def test_budget_negative_limit(self):
        """Test that negative limit amounts are rejected."""
        start_date = datetime(2025, 12, 1)
        end_date = datetime(2025, 12, 31)
        
        with pytest.raises(ValidationError):
            BudgetCreate(
                category=TransactionCategory.FOOD,
                limit_amount=-1000.00,
                period=BudgetPeriod.MONTHLY,
                start_date=start_date,
                end_date=end_date
            )
    
    def test_budget_zero_limit(self):
        """Test that zero limit amounts are rejected."""
        start_date = datetime(2025, 12, 1)
        end_date = datetime(2025, 12, 31)
        
        with pytest.raises(ValidationError):
            BudgetCreate(
                category=TransactionCategory.FOOD,
                limit_amount=0.00,
                period=BudgetPeriod.MONTHLY,
                start_date=start_date,
                end_date=end_date
            )
    
    def test_budget_default_period(self):
        """Test that default period is monthly."""
        start_date = datetime(2025, 12, 1)
        end_date = datetime(2025, 12, 31)
        
        budget = BudgetCreate(
            category=TransactionCategory.FOOD,
            limit_amount=2000.00,
            start_date=start_date,
            end_date=end_date
        )
        
        assert budget.period == BudgetPeriod.MONTHLY
    
    def test_budget_default_alert_threshold(self):
        """Test that default alert threshold is 0.8."""
        start_date = datetime(2025, 12, 1)
        end_date = datetime(2025, 12, 31)
        
        budget = BudgetCreate(
            category=TransactionCategory.FOOD,
            limit_amount=2000.00,
            start_date=start_date,
            end_date=end_date
        )
        
        assert budget.alert_threshold == 0.8
    
    def test_budget_period_enum_values(self):
        """Test budget period enum values."""
        assert BudgetPeriod.WEEKLY.value == "weekly"
        assert BudgetPeriod.MONTHLY.value == "monthly"
        assert BudgetPeriod.YEARLY.value == "yearly"
    
    def test_budget_status_enum_values(self):
        """Test budget status enum values."""
        assert BudgetStatus.SAFE.value == "safe"
        assert BudgetStatus.WARNING.value == "warning"
        assert BudgetStatus.CRITICAL.value == "critical"
        assert BudgetStatus.EXCEEDED.value == "exceeded"
    
    def test_budget_progress_safe_status(self):
        """Test budget progress with safe status."""
        progress = BudgetProgress(
            spent_amount=500.00,
            remaining_amount=1500.00,
            percentage_used=25.0,
            status=BudgetStatus.SAFE,
            is_over_budget=False
        )
        
        assert progress.spent_amount == 500.00
        assert progress.remaining_amount == 1500.00
        assert progress.percentage_used == 25.0
        assert progress.status == BudgetStatus.SAFE
        assert progress.is_over_budget is False
    
    def test_budget_progress_exceeded_status(self):
        """Test budget progress with exceeded status."""
        progress = BudgetProgress(
            spent_amount=2500.00,
            remaining_amount=-500.00,
            percentage_used=125.0,
            status=BudgetStatus.EXCEEDED,
            is_over_budget=True
        )
        
        assert progress.spent_amount == 2500.00
        assert progress.remaining_amount == -500.00
        assert progress.percentage_used == 125.0
        assert progress.status == BudgetStatus.EXCEEDED
        assert progress.is_over_budget is True
    
    def test_budget_update_partial(self):
        """Test updating budget with partial data."""
        update = BudgetUpdate(
            limit_amount=3000.00,
            alert_threshold=0.9
        )
        
        assert update.limit_amount == 3000.00
        assert update.alert_threshold == 0.9
        assert update.category is None
        assert update.period is None
    
    def test_budget_alert_threshold_validation(self):
        """Test alert threshold must be between 0 and 1."""
        start_date = datetime(2025, 12, 1)
        end_date = datetime(2025, 12, 31)
        
        # Valid threshold
        budget = BudgetCreate(
            category=TransactionCategory.FOOD,
            limit_amount=2000.00,
            start_date=start_date,
            end_date=end_date,
            alert_threshold=0.5
        )
        assert budget.alert_threshold == 0.5
        
        # Invalid threshold > 1
        with pytest.raises(ValidationError):
            BudgetCreate(
                category=TransactionCategory.FOOD,
                limit_amount=2000.00,
                start_date=start_date,
                end_date=end_date,
                alert_threshold=1.5
            )
        
        # Invalid threshold < 0
        with pytest.raises(ValidationError):
            BudgetCreate(
                category=TransactionCategory.FOOD,
                limit_amount=2000.00,
                start_date=start_date,
                end_date=end_date,
                alert_threshold=-0.1
            )
    
    def test_budget_response_with_progress(self):
        """Test budget response with progress data."""
        budget_response = BudgetResponse(
            _id="507f1f77bcf86cd799439011",
            category=TransactionCategory.FOOD,
            limit_amount=2000.00,
            period=BudgetPeriod.MONTHLY,
            start_date=datetime(2025, 12, 1),
            end_date=datetime(2025, 12, 31),
            alert_threshold=0.8,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            progress=BudgetProgress(
                spent_amount=1200.00,
                remaining_amount=800.00,
                percentage_used=60.0,
                status=BudgetStatus.SAFE,
                is_over_budget=False
            )
        )
        
        assert budget_response.progress is not None
        assert budget_response.progress.spent_amount == 1200.00
        assert budget_response.progress.status == BudgetStatus.SAFE

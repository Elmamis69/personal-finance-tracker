"""
Unit tests for Transaction models
"""
import pytest
from datetime import datetime
from pydantic import ValidationError

from app.models.transaction import (
    TransactionType,
    TransactionCategory,
    TransactionBase,
    TransactionCreate,
    TransactionUpdate,
    TransactionInDB,
    TransactionResponse
)


@pytest.mark.unit
class TestTransactionModels:
    """Test Transaction model validation and creation."""
    
    def test_transaction_create_valid(self):
        """Test creating a valid transaction."""
        transaction = TransactionCreate(
            amount=100.50,
            type=TransactionType.EXPENSE,
            category=TransactionCategory.FOOD,
            description="Lunch at restaurant",
            tags=["food", "dining"]
        )
        
        assert transaction.amount == 100.50
        assert transaction.type == TransactionType.EXPENSE
        assert transaction.category == TransactionCategory.FOOD
        assert transaction.description == "Lunch at restaurant"
        assert transaction.tags == ["food", "dining"]
        assert isinstance(transaction.date, datetime)
    
    def test_transaction_negative_amount(self):
        """Test that negative amounts are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            TransactionCreate(
                amount=-50.00,
                type=TransactionType.EXPENSE,
                category=TransactionCategory.FOOD,
                description="Invalid transaction"
            )
        
        assert "greater than 0" in str(exc_info.value).lower()
    
    def test_transaction_zero_amount(self):
        """Test that zero amounts are rejected."""
        with pytest.raises(ValidationError):
            TransactionCreate(
                amount=0.00,
                type=TransactionType.EXPENSE,
                category=TransactionCategory.FOOD,
                description="Invalid transaction"
            )
    
    def test_transaction_empty_description(self):
        """Test that empty descriptions are rejected."""
        with pytest.raises(ValidationError):
            TransactionCreate(
                amount=100.00,
                type=TransactionType.EXPENSE,
                category=TransactionCategory.FOOD,
                description=""
            )
    
    def test_transaction_description_too_long(self):
        """Test that descriptions longer than 500 chars are rejected."""
        with pytest.raises(ValidationError):
            TransactionCreate(
                amount=100.00,
                type=TransactionType.EXPENSE,
                category=TransactionCategory.FOOD,
                description="x" * 501
            )
    
    def test_transaction_update_partial(self):
        """Test updating transaction with partial data."""
        update = TransactionUpdate(
            amount=200.00,
            description="Updated description"
        )
        
        assert update.amount == 200.00
        assert update.description == "Updated description"
        assert update.type is None
        assert update.category is None
    
    def test_transaction_update_exclude_unset(self):
        """Test that unset fields are excluded from update."""
        update = TransactionUpdate(amount=150.00)
        data = update.model_dump(exclude_unset=True)
        
        assert "amount" in data
        assert "type" not in data
        assert "category" not in data
        assert "description" not in data
    
    def test_transaction_type_enum(self):
        """Test transaction type enum values."""
        assert TransactionType.INCOME.value == "income"
        assert TransactionType.EXPENSE.value == "expense"
    
    def test_transaction_category_income_categories(self):
        """Test income category enum values."""
        assert TransactionCategory.SALARY.value == "salary"
        assert TransactionCategory.FREELANCE.value == "freelance"
        assert TransactionCategory.INVESTMENT.value == "investment"
    
    def test_transaction_category_expense_categories(self):
        """Test expense category enum values."""
        assert TransactionCategory.FOOD.value == "food"
        assert TransactionCategory.TRANSPORT.value == "transport"
        assert TransactionCategory.HOUSING.value == "housing"
        assert TransactionCategory.ENTERTAINMENT.value == "entertainment"
    
    def test_transaction_in_db_with_id(self):
        """Test TransactionInDB model with MongoDB ID."""
        transaction = TransactionInDB(
            _id="507f1f77bcf86cd799439011",
            amount=100.00,
            type=TransactionType.INCOME,
            category=TransactionCategory.SALARY,
            description="Monthly salary",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        assert transaction.id == "507f1f77bcf86cd799439011"
        assert transaction.amount == 100.00
    
    def test_transaction_with_tags(self):
        """Test transaction with tags."""
        transaction = TransactionCreate(
            amount=50.00,
            type=TransactionType.EXPENSE,
            category=TransactionCategory.TRANSPORT,
            description="Taxi ride",
            tags=["uber", "work", "commute"]
        )
        
        assert len(transaction.tags) == 3
        assert "uber" in transaction.tags
    
    def test_transaction_without_tags(self):
        """Test transaction without tags (should be None)."""
        transaction = TransactionCreate(
            amount=50.00,
            type=TransactionType.EXPENSE,
            category=TransactionCategory.TRANSPORT,
            description="Taxi ride"
        )
        
        assert transaction.tags is None

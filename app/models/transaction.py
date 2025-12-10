from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
from typing import Optional

class TransactionType(str, Enum):
    """Transaction type: income or expense"""
    INCOME = "income"
    EXPENSE = "expense"

class TransactionCategory(str, Enum):
    """Transaction categories"""
    # Income categories
    SALARY = "salary"
    FREELANCE = "freelance"
    INVESTMENT = "investment"
    OTHER_INCOME = "other_income"

    # Expense categories
    FOOD = "food"
    TRANSPORT = "transport"
    HOUSING = "housing"
    UTILITIES = "utilities"
    ENTERTAINMENT = "entertainment"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    SHOPPING = "shopping"
    TRAVEL = "travel"
    SUSCRIPTIONS = "subscriptions"
    OTHER_EXPENSE = "other_expense"

class TransactionBase(BaseModel):
    """Base transaction model"""
    amount: float = Field(..., gt = 0, description = "Transaction amount (must be positive)")
    type: TransactionType = Field(..., description = "Transaction type (income/expense)")
    category: TransactionCategory = Field(..., description = "Transaction category")
    description: str = Field(..., min_length = 1, max_length = 500, description = "Transaction description")
    date: datetime = Field(default_factory = datetime.utcnow, description = "Transaction date")
    tags: Optional[list[str]] = Field(default = None, description = "Optional tags for categorization")

class TransactionCreate(TransactionBase):
    """Model for creating a transaction"""
    pass

class TransactionUpdate(BaseModel):
    """Model for updating a transaction (all fields optional)"""
    amount: Optional[float] = Field(None, gt = 0)
    type: Optional[TransactionType] = None
    category: Optional[TransactionCategory] = None
    description: Optional[str] = Field(None, min_length = 1, max_length = 500)
    date: Optional[datetime] = None
    tags: Optional[list[str]] = None

class TransactionInDB(TransactionBase):
    """Transaction model as stored in database"""
    id: str = Field(..., alias = "_id", description = "MongoDB document ID")
    created_at: datetime = Field(default_factory = datetime.utcnow)
    updated_at: datetime = Field(default_factory = datetime.utcnow)

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "amount": 1500.00,
                "type": "income",
                "category": "salary",
                "description": "Monthly salary",
                "date": "2025-12-10T00:00:00Z",
                "tags": ["work", "monthly"],
                "created_at": "2025-12-10T00:00:00Z",
                "updated_at": "2025-12-10T00:00:00Z"
            }
        }

class TransactionResponse(TransactionInDB):
    """Transaction response model"""
    pass


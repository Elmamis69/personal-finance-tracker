from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
from typing import Optional
from app.models.transaction import TransactionCategory

class BudgetPeriod(str, Enum):
    """Budget period types"""
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

class BudgetStatus(str, Enum):
    """Budget status based on spending"""
    SAFE = "safe" # Under 70% of limit
    WARNING = "warning" # 70-90% of limit
    CRITICAL = "critical" # 90-100% of limit
    EXCEEDED = "exceeded" # Over 100% of limit

class BudgetBase(BaseModel):
    """Base budget model"""
    category: TransactionCategory = Field(..., description="Expense category for this budget")
    limit_amount: float = Field(..., gt=0, description="Budget limit amount")
    period: BudgetPeriod = Field(default = BudgetPeriod.MONTHLY, description="Budget period")
    start_date: datetime = Field(..., description="Budget start date")
    end_date: datetime = Field(..., description="Budget end date")
    alert_threshold: float = Field(
        default = 0.8, 
        gt = 0, 
        le = 1, 
        description = "Alert threshold (0-1, default 0.8 = 80%)"
    )

class BudgetCreate(BudgetBase):
    """Model for creating a budget"""
    pass

class BudgetUpdate(BaseModel):
    """Model for updating a budget (all fields optional)"""
    category: Optional[TransactionCategory] = None
    limit_amount: Optional[float] = Field(None, gt = 0)
    period: Optional[BudgetPeriod] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    alert_threshold: Optional[float] = Field(None, gt = 0, le = 1)

class BudgetInDB(BudgetBase):
    """Budget model as stored in database"""
    id: str = Field(..., alias = "_id", description = "MongoDB document ID")
    created_at: datetime = Field(default_factory = datetime.utcnow)
    updated_at: datetime = Field(default_factory = datetime.utcnow)

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "category": "food",
                "limit_amount": 5000.0,
                "period": "monthly",
                "start_date": "2025-12-01T00:00:00Z",
                "end_date": "2025-12-31T23:59:59Z",
                "alert_threshold": 0.8,
                "created_at": "2025-12-01T00:00:00Z",
                "updated_at": "2025-12-01T00:00:00Z"
            }
        }

class BudgetProgress(BaseModel):
    """Budget progress information"""
    spent_amount: float = Field(..., description="Amount spent in this budget period")
    remaining_amount: float = Field(..., description="Remaining budget amount")
    percentage_used: float = Field(..., description="Percentage of budget used (0-100+)")
    status: BudgetStatus = Field(..., description="Budget status")
    is_over_budget: bool = Field(..., description="Whether budget has been exceeded")


class BudgetResponse(BudgetInDB):
    """Budget response model with optional progress"""
    progress: Optional[BudgetProgress] = Field(None, description="Budget progress (if calculated)")

    class Config:
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "category": "food",
                "limit_amount": 5000.00,
                "period": "monthly",
                "start_date": "2025-12-01T00:00:00Z",
                "end_date": "2025-12-31T23:59:59Z",
                "alert_threshold": 0.8,
                "created_at": "2025-12-01T00:00:00Z",
                "updated_at": "2025-12-01T00:00:00Z",
                "progress": {
                    "spent_amount": 3200.00,
                    "remaining_amount": 1800.00,
                    "percentage_used": 64.0,
                    "status": "safe",
                    "is_over_budget": False
                }
            }
        }
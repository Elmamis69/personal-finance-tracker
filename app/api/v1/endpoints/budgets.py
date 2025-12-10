from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional
from datetime import datetime
from bson import ObjectId

from app.models.budget import (
    BudgetCreate,
    BudgetUpdate,
    BudgetResponse,
    BudgetProgress,
    BudgetStatus
)
from app.models.transaction import TransactionType
from app.db.mongodb import get_database

router = APIRouter()

def budget_helper(budget) -> dict:
    """Helper function to format budget from DB"""
    return {
        "_id": str(budget["_id"]),
        "category": budget["category"],
        "limit_amount": budget["limit_amount"],
        "period": budget["period"],
        "start_date": budget["start_date"],
        "end_date": budget["end_date"],
        "alert_threshold": budget.get("alert_threshold", 0.8),
        "created_at": budget.get("created_at", datetime.utcnow()),
        "updated_at": budget.get("updated_at", datetime.utcnow())
    }

async def calculate_budget_progress(budget_id: str, budget: dict) -> BudgetProgress:
    """Calculate budget progress based on transactions"""
    db = get_database()

    # Query transactions for this budget's category and date range
    query = {
        "type": TransactionType.EXPENSE,
        "category": budget["category"],
        "date": {
            "$gte": budget["start_date"],
            "$lte": budget["end_date"]
        }
    }
    
    # Sum all expenses in this category for the budget period
    pipeline = [
        {"$match": query},
        {"$group": {"_id": None, "total_spent": {"$sum": "$amount"}}}
    ]

    result = await db.transactions.aggregate(pipeline).to_list(length = 1)
    spent_amount = result[0]["total_spent"] if result else 0.0

    limit_amount = budget["limit_amount"]
    remaining_amount = limit_amount - spent_amount
    percentage_used = (spent_amount / limit_amount * 100) if limit_amount > 0 else 0

    # Determine status
    if percentage_used >= 100:
        budget_status = BudgetStatus.EXCEEDED
    elif percentage_used >= 90:
        budget_status = BudgetStatus.CRITICAL
    elif percentage_used >= 70:
        budget_status = BudgetStatus.WARNING
    else:
        budget_status = BudgetStatus.SAFE

    return BudgetProgress(
        spent_amount = spent_amount,
        remaining_amount = remaining_amount,
        percentage_used = round(percentage_used, 2),
        status = budget_status,
        is_over_budget = spent_amount > limit_amount
    )

@router.post("/", response_model = BudgetResponse, status_code = status.HTTP_201_CREATED)
async def create_budget(budget: BudgetCreate):
    """
    Create a new budget
    
    - **category**: Expense category to budget
    - **limit_amount**: Budget limit
    - **period**: weekly, monthly, yearly
    - **start_date**: Budget start date
    - **end_date**: Budget end date
    - **alert_threshold**: Alert when this % is reached (default 0.8)
    """
    db = get_database()

    # Validate dates
    if budget.end_date <= budget.start_date:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "end_date must be after start_date"
        )
    
    # Check for overlapping budgets for the same category
    overlapping = await db.budgets.find_one({
        "category": budget.category,
        "$or": [
            {
                "start_date": {"$lte": budget.start_date},
                "end_date": {"$gte": budget.end_date}
            },
            {
                "start_date": {"$lte": budget.end_date},
                "end_date": {"$gte": budget.start_date}
            }
        ]
    })

    if overlapping:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = f"A budget for category {budget.category} already exists for this period"
        )
    
    budget_dict = budget.model_dump()
    budget_dict["created_at"] = datetime.utcnow()
    budget_dict["updated_at"] = datetime.utcnow()

    result = await db.budgets.insert_one(budget_dict)
    created_budget = await db.budgets.find_one({"_id": result.inserted_id})

    return BudgetResponse(**budget_helper(created_budget))
    
@router.get("/", response_model = list[BudgetResponse])
async def get_budgets(
    skip: int = Query(0, ge = 0, description = "Number of records to skip"),
    limit: int = Query(100, ge = 1, le = 1000, description = "Max number of records to return"),
    include_progress: bool = Query(True, description = "Include budget progress calculation")
):
    """
    Get all budgets with optional pagination
    
    Set include_progress = true to calculate spending progress for each budget
    """
    db = get_database()

    budgets = await db.budgets.find().skip(skip).limit(limit).sort("start_date", -1).to_list(length = limit)

    result = []
    for budget in budgets:
        budget_data = budget_helper(budget)

        if include_progress:
            progress = await calculate_budget_progress(str(budget_data["_id"]), budget)
            budget_data["progress"] = progress.model_dump()

        result.append(BudgetResponse(**budget_data))
    
    return result

@router.get("/{budget_id}", response_model = BudgetResponse)
async def get_budget(
    budget_id: str, 
    include_progress: bool = Query(False, description = "Include budget progress calculation")
):
    """
    Get a specific budget by ID
    
    Set include_progress = true to calculate spending progress
    """
    db = get_database()

    if not ObjectId.is_valid(budget_id):
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Invalid budget ID format"
        )

    budget = await db.budgets.find_one({"_id": ObjectId(budget_id)})

    if not budget:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f"Budget with ID {budget_id} not found"
        )

    budget_data = budget_helper(budget)

    if include_progress:
        progress = await calculate_budget_progress(budget_id, budget)
        budget_data["progress"] = progress.model_dump()

    return BudgetResponse(**budget_data)

@router.get("/{budget_id}/progress", response_model = BudgetProgress)
async def get_budget_progress(budget_id: str):
    """
    Get budget progress (spent, remaining, percentage, status)
    
    This endpoint calculates current spending vs budget limit
    """
    db = get_database()

    if not ObjectId.is_valid(budget_id):
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Invalid budget ID format"
        )

    budget = await db.budgets.find_one({"_id": ObjectId(budget_id)})

    if not budget:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f"Budget with ID {budget_id} not found"
        )

    return await calculate_budget_progress(budget_id, budget)

@router.put("/{budget_id}", response_model = BudgetResponse)
async def update_budget(budget_id: str, budget_update: BudgetUpdate):
    """
    Update a budget
    
    Only provided fields will be updated
    """
    db = get_database()

    if not ObjectId.is_valid(budget_id):
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Invalid budget ID format"
        )
    
    # Check if budget exists
    existing_budget = await db.budgets.find_one({"_id": ObjectId(budget_id)})
    if not existing_budget:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f"Budget with ID {budget_id} not found"
        )
    
    # Build update dict
    update_dict = budget_update.model_dump(exclude_unset = True)

    if not update_dict:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "No fields to update"
        )
    
    # Validate dates if both are being updated or one is provided
    start_date = update_dict.get("start_date", existing_budget["start_date"])
    end_date = update_dict.get("end_date", existing_budget["end_date"])

    if end_date <= start_date:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "end_date must be after start_date"
        )
    
    update_dict["updated_at"] = datetime.utcnow()

    # Update budget
    await db.budgets.update_one(
        {"_id": ObjectId(budget_id)},
        {"$set": update_dict}
    )

    # Get updated budget
    updated_budget = await db.budgets.find_one({"_id": ObjectId(budget_id)})

    return BudgetResponse(**budget_helper(updated_budget))

@router.delete("/{budget_id}", status_code = status.HTTP_204_NO_CONTENT)
async def delete_budget(budget_id: str):
    """
    Delete a budget by ID
    """
    db = get_database()

    if not ObjectId.is_valid(budget_id):
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Invalid budget ID format"
        )
    
    result = await db.budgets.delete_one({"_id": ObjectId(budget_id)})

    if result.deleted_count == 0:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f"Budget with ID {budget_id} not found"
        )
    
    return None
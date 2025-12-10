from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional
from datetime import datetime
from bson import ObjectId

from app.models.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    TransactionType,
    TransactionCategory
)
from app.db.mongodb import get_database

from app.services.influx_service import influx_service

router = APIRouter()

def transaction_helper(transaction) -> dict:
    """Helper function to format transaction from DB"""
    return {
        "_id": str(transaction["_id"]),
        "amount": transaction["amount"],
        "type": transaction["type"],
        "category": transaction["category"],
        "description": transaction["description"],
        "date": transaction["date"],
        "tags": transaction.get("tags", []),
        "created_at": transaction.get("created_at", datetime.utcnow()),
        "updated_at": transaction.get("updated_at", datetime.utcnow())
    }

@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(transaction: TransactionCreate):
    """Create a new transaction"""
    db = get_database()
    
    transaction_dict = transaction.model_dump()
    transaction_dict["created_at"] = datetime.utcnow()
    transaction_dict["updated_at"] = datetime.utcnow()
    
    result = await db.transactions.insert_one(transaction_dict)
    created_transaction = await db.transactions.find_one({"_id": result.inserted_id})
    
    # Write metric to InfluxDB
    influx_service.write_transaction_metric(
        transaction_id=str(result.inserted_id),
        amount=transaction.amount,
        transaction_type=transaction.type,
        category=transaction.category.value,
        date=transaction.date
    )
    
    return TransactionResponse(**transaction_helper(created_transaction))

@router.get("/", response_model=list[TransactionResponse])
async def get_transactions(
    skip: int = Query(0, ge = 0, description = "Number of records to skip"),
    limit: int = Query(100, ge = 1, le = 1000, description = "Max number of records to return"),
    type: Optional[TransactionType] = Query(None, description = "Filter by transaction type"),
    category: Optional[TransactionCategory] = Query(None, description = "Filter by transaction category"),
    start_date: Optional[datetime] = Query(None, description = "Filter transactions from this date (inclusive)"),
    end_date: Optional[datetime] = Query(None, description = "Filter transactions up to this date (inclusive)"),
    tags: Optional[list[str]] = Query(None, description = "Filter by tags (comma-separated)")
):
    """
    Get all transactions with optional filters
    
    Supports pagination and filtering by:
    - type (income/expense)
    - category
    - date range
    - tags
    """
    db = get_database()

    # Build query filters
    query = {}

    if type:
        query["type"] = type

    if category:
        query["category"] = category

    if start_date or end_date:
        query["date"] = {}
        if start_date:
            query["date"]["$gte"] = start_date
        if end_date:
            query["date"]["$lte"] = end_date

    if tags:
        tag_list = [tag.strip() for tag in tags.split(",")]
        query["tags"] = {"$in": tag_list}

    # Execute query with pagination
    transactions = await db.transactions.find(query).skip(skip).limit(limit).sort("date", -1).to_list(length = limit)

    return [TransactionResponse(**transaction_helper(transaction)) for transaction in transactions]

@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: str):
    """
    Get a transaction by its ID
    """
    db = get_database()

    if not ObjectId.is_valid(transaction_id):
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST, 
            detail = "Invalid transaction ID"
        )

    transaction = await db.transactions.find_one({"_id": ObjectId(transaction_id)})

    if not transaction:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND, 
            detail = f"Transaction with ID {transaction_id} not found"
        )

    return TransactionResponse(**transaction_helper(transaction))

@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(transaction_id: str, transaction_update: TransactionUpdate):
    """
    Update a transaction
    
    Only provided fields will be updated
    """
    db = get_database()

    if not ObjectId.is_valid(transaction_id):
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST, 
            detail = "Invalid transaction ID format"
        )
    
    # Check if transaction exists
    existing_transaction = await db.transactions.find_one({"_id": ObjectId(transaction_id)})
    if not existing_transaction:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND, 
            detail = f"Transaction with ID {transaction_id} not found"
        )
    
    # Build update dict (only include provided fields)
    update_dict = transaction_update.model_dump(exclude_unset = True)

    if not update_dict:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST, 
            detail = "No fields to update"
        )
    
    update_dict["updated_at"] = datetime.utcnow()

    # Update transaction
    await db.transactions.update_one(
        {"_id": ObjectId(transaction_id)},
        {"$set": update_dict}
    )
    
    # Get updated transaction
    updated_transaction = await db.transactions.find_one({"_id": ObjectId(transaction_id)})

    return TransactionResponse(**transaction_helper(updated_transaction))

@router.delete("/{transaction_id}", status_code = status.HTTP_204_NO_CONTENT)
async def delete_transaction(transaction_id: str):
    """
    Delete a transaction
    """
    db = get_database()

    if not ObjectId.is_valid(transaction_id):
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST, 
            detail = "Invalid transaction ID format"
        )

    result = await db.transactions.delete_one({"_id": ObjectId(transaction_id)})

    if result.deleted_count == 0:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND, 
            detail = f"Transaction with ID {transaction_id} not found"
        )

    return None
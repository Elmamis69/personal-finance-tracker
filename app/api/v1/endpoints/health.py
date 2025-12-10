from fastapi import APIRouter, status
from datetime import datetime

router = APIRouter()

@router.get("/health", status_code = status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint
    
    Returns the API status and timestamp
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Personal Finance Tracker API"
    }

@router.get("/ping", status_code = status.HTTP_200_OK)
async def ping():
    """
    Simple ping endpoint
    """
    return {"message": "pong"}
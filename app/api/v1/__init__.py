from fastapi import APIRouter
from app.api.v1.endpoints import health, transactions

api_router = APIRouter()

api_router.include_router(health.router, tags = ["Health"])
api_router.include_router(transactions.router, prefix = "/transactions", tags = ["transactions"])
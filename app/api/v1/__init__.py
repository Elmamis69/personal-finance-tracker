from fastapi import APIRouter
from app.api.v1.endpoints import health, transactions, budgets, analytics

api_router = APIRouter()

api_router.include_router(health.router, tags = ["Health"])
api_router.include_router(transactions.router, prefix = "/transactions", tags = ["transactions"])
api_router.include_router(budgets.router, prefix = "/budgets", tags = ["budgets"])
api_router.include_router(analytics.router, prefix = "/analytics", tags = ["analytics"])
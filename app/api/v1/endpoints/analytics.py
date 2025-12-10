from fastapi import APIRouter, HTTPException, status, Query
from datetime import datetime, timedelta
from typing import Optional

from app.services.influx_service import influx_service

router = APIRouter()

@router.get("/spending-trend")
async def get_spending_trend(
    start_date: Optional[datetime] = Query(None, description = "Start date (defaults to 30 days ago)"),
    end_date: Optional[datetime] = Query(None, description = "End date (defaults to now)"),
    interval: Optional[str] = Query("1d", description = "Time interval: 1h, 1d, 1w, 1mo")
):
    """
    Get spending trend over time

    Returns aggregated expenses by time interval
    """
    if not end_date:
        end_date = datetime.utcnow()

    if not start_date:
        start_date = end_date - timedelta(days = 30)

    if start_date >= end_date:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "start_date must be before end_date"
        )
    
    data = influx_service.get_spending_trend(start_date, end_date, interval)

    return {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "interval": interval,
        "data_points": data
    }

@router.get("/category-breakdown")
async def get_category_breakdown(
    start_date: Optional[datetime] = Query(None, description = "Start date (defaults to 30 days ago)"),
    end_date: Optional[datetime] = Query(None, description = "End date (defaults to now)")
):
    """
    Get spending breakdown by category

    Returns total expenses per category
    """
    if not end_date:
        end_date = datetime.utcnow()

    if not start_date:
        start_date = end_date - timedelta(days = 30)

    if start_date >= end_date:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "start_date must be before end_date"
        )
    
    data = influx_service.get_category_breakdown(start_date, end_date)

    return {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "categories": data
    }

@router.get("/income-vs-expenses")
async def get_income_vs_expenses(
    start_date: Optional[datetime] = Query(None, description = "Start date (defaults to 30 days ago)"),
    end_date: Optional[datetime] = Query(None, description = "End date (defaults to now)")
):
    """
    Get total income vs total expenses

    Returns income, expenses, net savings, and savings rate percentage
    """
    if not end_date:
        end_date = datetime.utcnow()

    if not start_date:
        start_date = end_date - timedelta(days = 30)

    if start_date >= end_date:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "start_date must be before end_date"
        )
    
    data = influx_service.get_income_vs_expenses(start_date, end_date)

    return {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        **data
    }

@router.get("/monthly-comparison")
async def get_monthly_comparison(
    months: int = Query(6, ge = 1, le = 24, description = "Number of months to compare")
):
    """
    Compare monthly expenses over time

    Returns month-by-month expense comparison
    """
    end_date = datetime.utcnow()
    monthly_data = []

    for i in range(months):
        # Calculate start and end of month
        month_start = (end_date - timedelta(days = 30 * i)).replace(day = 1, hour = 0, minute = 0, second = 0, microsecond = 0)

        # Get next month
        if month_start.month == 12:
            month_end = month_start.replace(year = month_start.year + 1, month = 1, day = 1) - timedelta(seconds = 1)
        else:
            month_end = month_start.replace(month = month_start.month + 1, day = 1) - timedelta(seconds = 1)

        # Get data for this month
        month_summary = influx_service.get_income_vs_expenses(month_start, month_end)

        monthly_data.append({
            "month": month_start.strftime("%Y-%m"),
            "start_date": month_start.isoformat(),
            "end_date": month_end.isoformat(),
            **month_summary
        })

    return {
        "months": months,
        "data": monthly_data
    }

@router.get("/savings-rate")
async def get_savings_rate(
    start_date: Optional[datetime] = Query(None, description = "Start date (defaults to 30 days ago)"),
    end_date: Optional[datetime] = Query(None, description = "End date (defaults to now)")
):
    """
    Calculate savings rate (percentage of income saved)

    Savings rate = (Income - Expenses) / Income * 100
    """
    if not end_date:
        end_date = datetime.utcnow()

    if not start_date:
        start_date = end_date - timedelta(days = 30)

    if start_date >= end_date:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "start_date must be before end_date"
        )
    
    data = influx_service.get_income_vs_expenses(start_date, end_date)

    return {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "total_income": data["total_income"],
        "total_expenses": data["total_expenses"],
        "net_savings": data["net_savings"],
        "savings_rate_percentage": data["savings_rate"]
    }

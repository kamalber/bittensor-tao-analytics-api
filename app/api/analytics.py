from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import Optional
from datetime import datetime, timedelta

from app.auth import verify_token
from app.config import settings
from app.db import get_db_session, TaoDividendQuery, StakeAction
from app.models import DividendHistoryResponse, DividendHistoryItem

router = APIRouter()

@router.get("/analytics/dividends/history", response_model=DividendHistoryResponse)
async def get_dividend_history(
    netuid: Optional[int] = Query(None, description="Filter by subnet ID"),
    hotkey: Optional[str] = Query(None, description="Filter by hotkey"),
    days: int = Query(7, ge=1, le=365, description="Number of days to look back"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    token: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get historical dividend data with optional filtering.
    Returns paginated list of dividend queries ordered by most recent first.
    """
    try:
        # Calculate date threshold
        date_threshold = datetime.utcnow() - timedelta(days=days)

        # Build query
        query = select(TaoDividendQuery).where(
            TaoDividendQuery.created_at >= date_threshold
        ).order_by(desc(TaoDividendQuery.created_at))

        # Apply filters
        if netuid is not None:
            query = query.where(TaoDividendQuery.netuid == netuid)
        if hotkey is not None:
            query = query.where(TaoDividendQuery.hotkey == hotkey)

        # Get total count
        count_query = select(func.count()).select_from(TaoDividendQuery).where(
            TaoDividendQuery.created_at >= date_threshold
        )
        if netuid is not None:
            count_query = count_query.where(TaoDividendQuery.netuid == netuid)
        if hotkey is not None:
            count_query = count_query.where(TaoDividendQuery.hotkey == hotkey)

        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        # Execute query
        result = await db.execute(query)
        dividend_queries = result.scalars().all()

        # Calculate average dividend
        avg_query = select(func.avg(TaoDividendQuery.dividend)).where(
            TaoDividendQuery.created_at >= date_threshold
        )
        if netuid is not None:
            avg_query = avg_query.where(TaoDividendQuery.netuid == netuid)
        if hotkey is not None:
            avg_query = avg_query.where(TaoDividendQuery.hotkey == hotkey)

        avg_result = await db.execute(avg_query)
        average_dividend = avg_result.scalar()

        # Convert to response model
        history_items = [
            DividendHistoryItem(
                id=str(query.id),
                netuid=query.netuid,
                hotkey=query.hotkey,
                dividend=query.dividend,
                from_cache=query.from_cache,
                created_at=query.created_at
            )
            for query in dividend_queries
        ]

        return DividendHistoryResponse(
            history=history_items,
            total=total,
            page=page,
            page_size=page_size,
            average_dividend=float(average_dividend) if average_dividend else None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting dividend history: {str(e)}")

@router.get("/analytics/dividends/trends")
async def get_dividend_trends(
    netuid: Optional[int] = Query(None, description="Filter by subnet ID"),
    hotkey: Optional[str] = Query(None, description="Filter by hotkey"),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    token: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get dividend trends and statistics over a specified time period.
    Returns min, max, average, and percentile data.
    """
    try:
        # Calculate date threshold
        date_threshold = datetime.utcnow() - timedelta(days=days)

        # Build query
        query = select(TaoDividendQuery).where(
            TaoDividendQuery.created_at >= date_threshold
        )

        if netuid is not None:
            query = query.where(TaoDividendQuery.netuid == netuid)
        if hotkey is not None:
            query = query.where(TaoDividendQuery.hotkey == hotkey)

        # Execute query
        result = await db.execute(query)
        dividend_queries = result.scalars().all()

        if not dividend_queries:
            return {
                "period_days": days,
                "data_points": 0,
                "trends": None
            }

        # Calculate statistics
        dividends = [q.dividend for q in dividend_queries]
        dividends.sort()

        min_dividend = min(dividends)
        max_dividend = max(dividends)
        avg_dividend = sum(dividends) / len(dividends)

        # Calculate percentiles
        def percentile(data, p):
            n = len(data)
            index = (n - 1) * p / 100
            lower = int(index)
            upper = lower + 1
            if upper >= n:
                return data[lower]
            weight = index - lower
            return data[lower] * (1 - weight) + data[upper] * weight

        return {
            "period_days": days,
            "data_points": len(dividends),
            "netuid": netuid,
            "hotkey": hotkey,
            "trends": {
                "min": min_dividend,
                "max": max_dividend,
                "average": avg_dividend,
                "median": percentile(dividends, 50),
                "p25": percentile(dividends, 25),
                "p75": percentile(dividends, 75),
                "p90": percentile(dividends, 90),
                "p95": percentile(dividends, 95)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting dividend trends: {str(e)}")

@router.get("/analytics/stake/summary")
async def get_stake_summary(
    netuid: Optional[int] = Query(None, description="Filter by subnet ID"),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    token: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get stake/unstake summary statistics over a specified time period.
    Returns total staked, unstaked, and net stake changes.
    """
    try:
        # Calculate date threshold
        date_threshold = datetime.utcnow() - timedelta(days=days)

        # Build queries
        stake_query = select(
            func.count(StakeAction.id),
            func.sum(StakeAction.amount)
        ).where(
            StakeAction.created_at >= date_threshold,
            StakeAction.action_type == "stake"
        )

        unstake_query = select(
            func.count(StakeAction.id),
            func.sum(StakeAction.amount)
        ).where(
            StakeAction.created_at >= date_threshold,
            StakeAction.action_type == "unstake"
        )

        if netuid is not None:
            stake_query = stake_query.where(StakeAction.netuid == netuid)
            unstake_query = unstake_query.where(StakeAction.netuid == netuid)

        # Execute queries
        stake_result = await db.execute(stake_query)
        stake_count, stake_total = stake_result.one()

        unstake_result = await db.execute(unstake_query)
        unstake_count, unstake_total = unstake_result.one()

        stake_total = stake_total or 0.0
        unstake_total = unstake_total or 0.0

        return {
            "period_days": days,
            "netuid": netuid,
            "stake_actions": {
                "count": stake_count or 0,
                "total_amount": stake_total
            },
            "unstake_actions": {
                "count": unstake_count or 0,
                "total_amount": unstake_total
            },
            "net_stake_change": stake_total - unstake_total
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stake summary: {str(e)}")

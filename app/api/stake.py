from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from typing import Optional, List
from datetime import datetime

from app.auth import verify_token
from app.config import settings
from app.db import get_db_session, StakeAction
from app.models import (
    StakeActionRequest,
    StakeActionResponse,
    StakeHistoryResponse,
    StakeHistoryItem
)
from app.services.bittensor_service import bittensor_service

router = APIRouter()

@router.post("/stake", response_model=StakeActionResponse)
async def stake_tao(
    request: StakeActionRequest = Body(...),
    token: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Manually stake TAO to a specific hotkey on a subnet.
    This is a direct stake operation not dependent on sentiment analysis.
    """
    try:
        # Validate request
        if request.amount <= 0:
            raise HTTPException(status_code=400, detail="Amount must be greater than 0")

        # Execute stake operation
        result = await bittensor_service.stake(
            amount=request.amount,
            netuid=request.netuid,
            hotkey=request.hotkey
        )

        # Record in database
        stake_action = StakeAction(
            action_type="stake",
            netuid=request.netuid,
            hotkey=request.hotkey,
            amount=request.amount,
            sentiment_score=request.sentiment_score or 0.0,
            transaction_hash=result.get('transaction_hash'),
            status="success" if result.get('success') else "failed"
        )
        db.add(stake_action)
        await db.commit()

        return StakeActionResponse(
            success=result['success'],
            transaction_hash=result['transaction_hash'],
            amount=result['amount'],
            netuid=result['netuid'],
            hotkey=result['hotkey'],
            action=result['action'],
            mock=result.get('mock', False)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error staking TAO: {str(e)}")

@router.post("/unstake", response_model=StakeActionResponse)
async def unstake_tao(
    request: StakeActionRequest = Body(...),
    token: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Manually unstake TAO from a specific hotkey on a subnet.
    This is a direct unstake operation not dependent on sentiment analysis.
    """
    try:
        # Validate request
        if request.amount <= 0:
            raise HTTPException(status_code=400, detail="Amount must be greater than 0")

        # Execute unstake operation
        result = await bittensor_service.unstake(
            amount=request.amount,
            netuid=request.netuid,
            hotkey=request.hotkey
        )

        # Record in database
        stake_action = StakeAction(
            action_type="unstake",
            netuid=request.netuid,
            hotkey=request.hotkey,
            amount=request.amount,
            sentiment_score=request.sentiment_score or 0.0,
            transaction_hash=result.get('transaction_hash'),
            status="success" if result.get('success') else "failed"
        )
        db.add(stake_action)
        await db.commit()

        return StakeActionResponse(
            success=result['success'],
            transaction_hash=result['transaction_hash'],
            amount=result['amount'],
            netuid=result['netuid'],
            hotkey=result['hotkey'],
            action=result['action'],
            mock=result.get('mock', False)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error unstaking TAO: {str(e)}")

@router.get("/stake/history", response_model=StakeHistoryResponse)
async def get_stake_history(
    netuid: Optional[int] = Query(None, description="Filter by subnet ID"),
    hotkey: Optional[str] = Query(None, description="Filter by hotkey"),
    action_type: Optional[str] = Query(None, description="Filter by action type (stake/unstake)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    token: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get history of stake/unstake actions with optional filtering.
    Returns paginated list of stake actions ordered by most recent first.
    """
    try:
        # Build query
        query = select(StakeAction).order_by(desc(StakeAction.created_at))

        # Apply filters
        if netuid is not None:
            query = query.where(StakeAction.netuid == netuid)
        if hotkey is not None:
            query = query.where(StakeAction.hotkey == hotkey)
        if action_type is not None:
            if action_type not in ["stake", "unstake"]:
                raise HTTPException(status_code=400, detail="action_type must be 'stake' or 'unstake'")
            query = query.where(StakeAction.action_type == action_type)

        # Get total count
        count_query = select(func.count()).select_from(StakeAction)
        if netuid is not None:
            count_query = count_query.where(StakeAction.netuid == netuid)
        if hotkey is not None:
            count_query = count_query.where(StakeAction.hotkey == hotkey)
        if action_type is not None:
            count_query = count_query.where(StakeAction.action_type == action_type)

        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        # Execute query
        result = await db.execute(query)
        stake_actions = result.scalars().all()

        # Convert to response model
        history_items = [
            StakeHistoryItem(
                id=str(action.id),
                action_type=action.action_type,
                netuid=action.netuid,
                hotkey=action.hotkey,
                amount=action.amount,
                sentiment_score=action.sentiment_score,
                transaction_hash=action.transaction_hash,
                status=action.status,
                created_at=action.created_at
            )
            for action in stake_actions
        ]

        return StakeHistoryResponse(
            history=history_items,
            total=total,
            page=page,
            page_size=page_size
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stake history: {str(e)}")

@router.get("/stake/status/{transaction_hash}", response_model=StakeHistoryItem)
async def get_stake_status(
    transaction_hash: str,
    token: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get the status of a specific stake/unstake transaction.
    """
    try:
        query = select(StakeAction).where(StakeAction.transaction_hash == transaction_hash)
        result = await db.execute(query)
        stake_action = result.scalar_one_or_none()

        if not stake_action:
            raise HTTPException(status_code=404, detail="Transaction not found")

        return StakeHistoryItem(
            id=str(stake_action.id),
            action_type=stake_action.action_type,
            netuid=stake_action.netuid,
            hotkey=stake_action.hotkey,
            amount=stake_action.amount,
            sentiment_score=stake_action.sentiment_score,
            transaction_hash=stake_action.transaction_hash,
            status=stake_action.status,
            created_at=stake_action.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stake status: {str(e)}")

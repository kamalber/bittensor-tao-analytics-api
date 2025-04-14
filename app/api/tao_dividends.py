from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any, List

from app.auth import verify_token
from app.config import settings
from app.db import get_db_session, TaoDividendQuery
from app.models import TaoDividendResponse
from app.services.bittensor_service import bittensor_service
from app.worker import celery_app


router = APIRouter()

@router.get("/tao_dividends", response_model=TaoDividendResponse)
async def get_tao_dividends(
    netuid: Optional[int] = Query(None, description="Subnet ID (optional)"),
    hotkey: Optional[str] = Query(None, description="Hotkey address (optional)"),
    trade: bool = Query(False, description="Trigger stake/unstake based on sentiment"),
    token: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get TAO dividends for a specific subnet and hotkey.
    - If netuid is omitted, returns data for the default netuid
    - If hotkey is omitted, returns data for the default hotkey
    - If trade=true, triggers sentiment analysis and stake/unstake
    """
    try:
        # Use defaults if not provided
        if netuid is None:
            netuid = settings.DEFAULT_NETUID
        if hotkey is None:
            hotkey = settings.DEFAULT_HOTKEY

        # Get data from blockchain (or cache)
        result = await bittensor_service.get_tao_dividends(netuid, hotkey)

        # Store query in database
        dividend_query = TaoDividendQuery(
            netuid=netuid,
            hotkey=hotkey,
            dividend=result["dividend"],
            from_cache=result["cached"]
        )
        db.add(dividend_query)
        await db.commit()

        # Handle trade parameter (trigger stake/unstake based on sentiment)
        stake_tx_triggered = False
        if trade:
            # Async task to analyze sentiment and stake/unstake
            celery_app.send_task(
                "process_sentiment_and_stake",
                args=[netuid, hotkey]
            )
            stake_tx_triggered = True

        # Prepare response
        response = TaoDividendResponse(
            netuid=result["netuid"],
            hotkey=result["hotkey"],
            dividend=result["dividend"],
            cached=result["cached"],
            stake_tx_triggered=stake_tx_triggered
        )

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving TAO dividends: {str(e)}")



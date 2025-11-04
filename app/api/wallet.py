from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.auth import verify_token
from app.config import settings
from app.db import get_db_session
from app.models import WalletBalanceResponse
from app.services.bittensor_service import bittensor_service

router = APIRouter()

@router.get("/wallet/balance", response_model=WalletBalanceResponse)
async def get_wallet_balance(
    wallet_address: Optional[str] = Query(None, description="Wallet address (uses default if not provided)"),
    token: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get wallet balance including free balance, staked balance, and total balance.
    If wallet_address is not provided, uses the configured wallet.
    """
    try:
        # Get wallet balance from Bittensor service
        balance_data = await bittensor_service.get_wallet_balance(wallet_address)

        return WalletBalanceResponse(
            wallet_address=balance_data['wallet_address'],
            balance=balance_data['balance'],
            staked_balance=balance_data['staked_balance'],
            total_balance=balance_data['total_balance']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting wallet balance: {str(e)}")

@router.get("/wallet/stakes", response_model=dict)
async def get_wallet_stakes(
    wallet_address: Optional[str] = Query(None, description="Wallet address (uses default if not provided)"),
    token: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get all stakes for a wallet across different subnets.
    Returns a detailed breakdown of staked amounts per subnet and hotkey.
    """
    try:
        # Get wallet stakes from Bittensor service
        stakes_data = await bittensor_service.get_wallet_stakes(wallet_address)

        return {
            "wallet_address": stakes_data['wallet_address'],
            "total_staked": stakes_data['total_staked'],
            "stakes": stakes_data['stakes'],
            "subnet_count": len(stakes_data['stakes'])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting wallet stakes: {str(e)}")

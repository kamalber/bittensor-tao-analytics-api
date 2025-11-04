from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.auth import verify_token
from app.config import settings
from app.db import get_db_session, ValidatorMetrics
from app.models import ValidatorInfo, ValidatorListResponse, MinerInfo, MinerListResponse
from app.services.bittensor_service import bittensor_service

router = APIRouter()

@router.get("/validators", response_model=ValidatorListResponse)
async def list_validators(
    netuid: Optional[int] = Query(None, description="Filter by subnet ID"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    token: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db_session)
):
    """
    List all validators, optionally filtered by subnet.
    Returns validator information including stake, trust, consensus, etc.
    """
    try:
        # Use default netuid if not provided
        if netuid is None:
            netuid = settings.DEFAULT_NETUID

        # Get validator data from Bittensor service
        validators_data = await bittensor_service.get_validators(netuid)

        # Apply pagination
        offset = (page - 1) * page_size
        total = len(validators_data)
        paginated_validators = validators_data[offset:offset + page_size]

        # Convert to response model
        validator_infos = [
            ValidatorInfo(
                netuid=netuid,
                hotkey=val['hotkey'],
                stake=val.get('stake', 0.0),
                trust=val.get('trust'),
                consensus=val.get('consensus'),
                incentive=val.get('incentive'),
                dividends=val.get('dividends'),
                rank=val.get('rank')
            )
            for val in paginated_validators
        ]

        # Store metrics in database
        for val_info in validator_infos:
            metric = ValidatorMetrics(
                netuid=val_info.netuid,
                hotkey=val_info.hotkey,
                stake=val_info.stake,
                trust=val_info.trust,
                consensus=val_info.consensus,
                incentive=val_info.incentive,
                dividends=val_info.dividends,
                rank=val_info.rank
            )
            db.add(metric)

        await db.commit()

        return ValidatorListResponse(
            validators=validator_infos,
            total=total,
            page=page,
            page_size=page_size,
            netuid=netuid
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing validators: {str(e)}")

@router.get("/validators/{hotkey}", response_model=ValidatorInfo)
async def get_validator(
    hotkey: str,
    netuid: Optional[int] = Query(None, description="Subnet ID"),
    token: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get detailed information about a specific validator.
    """
    try:
        # Use default netuid if not provided
        if netuid is None:
            netuid = settings.DEFAULT_NETUID

        validator_data = await bittensor_service.get_validator_info(netuid, hotkey)

        validator_info = ValidatorInfo(
            netuid=netuid,
            hotkey=validator_data['hotkey'],
            stake=validator_data.get('stake', 0.0),
            trust=validator_data.get('trust'),
            consensus=validator_data.get('consensus'),
            incentive=validator_data.get('incentive'),
            dividends=validator_data.get('dividends'),
            rank=validator_data.get('rank')
        )

        # Store metrics
        metric = ValidatorMetrics(
            netuid=validator_info.netuid,
            hotkey=validator_info.hotkey,
            stake=validator_info.stake,
            trust=validator_info.trust,
            consensus=validator_info.consensus,
            incentive=validator_info.incentive,
            dividends=validator_info.dividends,
            rank=validator_info.rank
        )
        db.add(metric)
        await db.commit()

        return validator_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting validator info: {str(e)}")

@router.get("/miners", response_model=MinerListResponse)
async def list_miners(
    netuid: Optional[int] = Query(None, description="Filter by subnet ID"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    token: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db_session)
):
    """
    List all miners, optionally filtered by subnet.
    Returns miner information including UID, stake, trust, incentive, etc.
    """
    try:
        # Use default netuid if not provided
        if netuid is None:
            netuid = settings.DEFAULT_NETUID

        # Get miner data from Bittensor service
        miners_data = await bittensor_service.get_miners(netuid)

        # Apply pagination
        offset = (page - 1) * page_size
        total = len(miners_data)
        paginated_miners = miners_data[offset:offset + page_size]

        # Convert to response model
        miner_infos = [
            MinerInfo(
                netuid=netuid,
                hotkey=miner['hotkey'],
                uid=miner['uid'],
                stake=miner.get('stake'),
                trust=miner.get('trust'),
                consensus=miner.get('consensus'),
                incentive=miner.get('incentive'),
                dividends=miner.get('dividends'),
                emission=miner.get('emission')
            )
            for miner in paginated_miners
        ]

        return MinerListResponse(
            miners=miner_infos,
            total=total,
            page=page,
            page_size=page_size,
            netuid=netuid
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing miners: {str(e)}")

@router.get("/miners/{hotkey}", response_model=MinerInfo)
async def get_miner(
    hotkey: str,
    netuid: Optional[int] = Query(None, description="Subnet ID"),
    token: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get detailed information about a specific miner.
    """
    try:
        # Use default netuid if not provided
        if netuid is None:
            netuid = settings.DEFAULT_NETUID

        miner_data = await bittensor_service.get_miner_info(netuid, hotkey)

        miner_info = MinerInfo(
            netuid=netuid,
            hotkey=miner_data['hotkey'],
            uid=miner_data['uid'],
            stake=miner_data.get('stake'),
            trust=miner_data.get('trust'),
            consensus=miner_data.get('consensus'),
            incentive=miner_data.get('incentive'),
            dividends=miner_data.get('dividends'),
            emission=miner_data.get('emission')
        )

        return miner_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting miner info: {str(e)}")

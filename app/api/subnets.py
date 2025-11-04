from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List
from datetime import datetime

from app.auth import verify_token
from app.config import settings
from app.db import get_db_session, SubnetMetrics
from app.models import SubnetInfo, SubnetListResponse, NetworkStats
from app.services.bittensor_service import bittensor_service

router = APIRouter()

@router.get("/subnets", response_model=SubnetListResponse)
async def list_subnets(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    token: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db_session)
):
    """
    List all available subnets with pagination.
    Returns subnet information including total stake, validator and miner counts.
    """
    try:
        # Get subnet data from Bittensor service
        subnets_data = await bittensor_service.get_all_subnets()

        # Apply pagination
        offset = (page - 1) * page_size
        total = len(subnets_data)
        paginated_subnets = subnets_data[offset:offset + page_size]

        # Convert to response model
        subnet_infos = [
            SubnetInfo(
                netuid=subnet['netuid'],
                name=subnet.get('name'),
                total_stake=subnet.get('total_stake', 0.0),
                validator_count=subnet.get('validator_count', 0),
                miner_count=subnet.get('miner_count', 0),
                emission_rate=subnet.get('emission_rate'),
                difficulty=subnet.get('difficulty')
            )
            for subnet in paginated_subnets
        ]

        # Store metrics in database
        for subnet_info in subnet_infos:
            metric = SubnetMetrics(
                netuid=subnet_info.netuid,
                total_stake=subnet_info.total_stake,
                validator_count=subnet_info.validator_count,
                miner_count=subnet_info.miner_count,
                emission_rate=subnet_info.emission_rate,
                difficulty=subnet_info.difficulty
            )
            db.add(metric)

        await db.commit()

        return SubnetListResponse(
            subnets=subnet_infos,
            total=total,
            page=page,
            page_size=page_size
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing subnets: {str(e)}")

@router.get("/subnets/{netuid}", response_model=SubnetInfo)
async def get_subnet(
    netuid: int,
    token: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get detailed information about a specific subnet.
    """
    try:
        subnet_data = await bittensor_service.get_subnet_info(netuid)

        subnet_info = SubnetInfo(
            netuid=subnet_data['netuid'],
            name=subnet_data.get('name'),
            total_stake=subnet_data.get('total_stake', 0.0),
            validator_count=subnet_data.get('validator_count', 0),
            miner_count=subnet_data.get('miner_count', 0),
            emission_rate=subnet_data.get('emission_rate'),
            difficulty=subnet_data.get('difficulty')
        )

        # Store metrics
        metric = SubnetMetrics(
            netuid=subnet_info.netuid,
            total_stake=subnet_info.total_stake,
            validator_count=subnet_info.validator_count,
            miner_count=subnet_info.miner_count,
            emission_rate=subnet_info.emission_rate,
            difficulty=subnet_info.difficulty
        )
        db.add(metric)
        await db.commit()

        return subnet_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting subnet info: {str(e)}")

@router.get("/network/stats", response_model=NetworkStats)
async def get_network_stats(
    token: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get overall network statistics across all subnets.
    """
    try:
        subnets_data = await bittensor_service.get_all_subnets()

        total_stake = sum(s.get('total_stake', 0.0) for s in subnets_data)
        total_validators = sum(s.get('validator_count', 0) for s in subnets_data)
        total_miners = sum(s.get('miner_count', 0) for s in subnets_data)

        # Calculate average emission rate
        emission_rates = [s.get('emission_rate', 0.0) for s in subnets_data if s.get('emission_rate') is not None]
        avg_emission = sum(emission_rates) / len(emission_rates) if emission_rates else None

        return NetworkStats(
            total_subnets=len(subnets_data),
            total_stake=total_stake,
            total_validators=total_validators,
            total_miners=total_miners,
            avg_emission_rate=avg_emission
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting network stats: {str(e)}")

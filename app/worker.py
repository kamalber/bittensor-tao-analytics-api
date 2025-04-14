import os
import asyncio
import logging
from celery import Celery
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.db import async_session, StakeAction
from app.services.bittensor_service import bittensor_service
from app.services.sentiment_service import sentiment_service

celery_app = Celery(
    "worker",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"
)

celery_app.conf.task_serializer = 'json'
celery_app.conf.result_serializer = 'json'
celery_app.conf.accept_content = ['json']
celery_app.conf.task_routes = {'app.worker.*': {'queue': 'bittensor_queue'}}
celery_app.conf.worker_concurrency = 4

async def run_async_task(coro):
    """Run async coroutine in a synchronous context"""
    loop = asyncio.get_event_loop()
    return await coro

@celery_app.task(name="process_sentiment_and_stake")
def process_sentiment_and_stake(netuid, hotkey):
    """Process sentiment and stake/unstake based on results"""
    logging.info(f"Processing sentiment for netuid {netuid}")
    
    # Run async tasks
    async def process():
        try:
            # Get sentiment
            sentiment_result = await sentiment_service.get_subnet_sentiment(netuid)
            score = sentiment_result.score
            logging.info(f"Sentiment score for netuid {netuid}: {score}")
            
            # Calculate stake amount based on sentiment
            amount = abs(score) * 0.01  # 0.01 tao * sentiment score
            
            # Determine action (stake or unstake)
            action_type = "stake" if score > 0 else "unstake"
            
            # Create database record
            async with async_session() as session:
                stake_action = StakeAction(
                    action_type=action_type,
                    netuid=netuid,
                    hotkey=hotkey,
                    amount=amount,
                    sentiment_score=score,
                    status="pending"
                )
                session.add(stake_action)
                await session.commit()
                await session.refresh(stake_action)
                action_id = stake_action.id
            
            # Perform stake/unstake action
            try:
                if action_type == "stake" and amount > 0:
                    result = await bittensor_service.stake(amount, netuid, hotkey)
                elif action_type == "unstake" and amount > 0:
                    result = await bittensor_service.unstake(amount, netuid, hotkey)
                else:
                    logging.info(f"No action required for sentiment score {score}")
                    return {"success": True, "action": "none", "sentiment_score": score}
                
                # Update database record
                async with async_session() as session:
                    stake_action = await session.get(StakeAction, action_id)
                    if stake_action:
                        stake_action.status = "success"
                        stake_action.transaction_hash = result.get("transaction_hash")
                        await session.commit()
                
                return {
                    "success": True,
                    "action": action_type,
                    "amount": amount,
                    "sentiment_score": score,
                    "netuid": netuid,
                    "hotkey": hotkey,
                    "transaction_hash": result.get("transaction_hash"),
                    "mock": result.get("mock", False)
                }
            except Exception as e:
                logging.error(f"Error performing {action_type}: {e}")
                
                # Update database record
                async with async_session() as session:
                    stake_action = await session.get(StakeAction, action_id)
                    if stake_action:
                        stake_action.status = "failed"
                        await session.commit()
                
                return {
                    "success": False,
                    "action": action_type,
                    "amount": amount,
                    "sentiment_score": score,
                    "netuid": netuid,
                    "hotkey": hotkey,
                    "error": str(e)
                }
        except Exception as e:
            logging.error(f"Error in sentiment processing: {e}")
            return {"success": False, "error": str(e)}
    
    return asyncio.run(process())



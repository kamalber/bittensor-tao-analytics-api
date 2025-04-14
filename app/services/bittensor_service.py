import asyncio
import logging
from typing import Optional, Dict, Any, Union, List
try:
    import bittensor
    from bittensor.core.async_subtensor import AsyncSubtensor
    from bittensor.wallet import wallet
    BITTENSOR_AVAILABLE = True
except ImportError:
    BITTENSOR_AVAILABLE = False
    logging.error("Bittensor package not available. Using mock implementation.")

from app.config import settings
from app.services.cache_service import cache

class BittensorService:
    def __init__(self):
        self.async_subtensor = None
        self.wallet = None
        if not BITTENSOR_AVAILABLE:
            logging.warning("Bittensor is not available. Using mock implementations.")
        
    async def init_subtensor(self):
        """Initialize AsyncSubtensor connection"""
        if not BITTENSOR_AVAILABLE:
            logging.warning("Bittensor not available. Using mock subtensor.")
            return
            
        if not self.async_subtensor:
            try:
                self.async_subtensor = AsyncSubtensor(network=settings.BITTENSOR_NETWORK)
                await self.async_subtensor.connect()
                logging.info(f"Connected to Bittensor {settings.BITTENSOR_NETWORK}")
            except Exception as e:
                logging.error(f"Bittensor connection error: {e}")
                raise
    
    async def init_wallet(self):
        """Initialize Bittensor wallet"""
        if not BITTENSOR_AVAILABLE:
            logging.warning("Bittensor not available. Using mock wallet.")
            return
            
        if not self.wallet:
            try:
                self.wallet = wallet.Wallet(
                    mnemonic=settings.WALLET_MNEMONIC,
                    network=settings.BITTENSOR_NETWORK
                )
                logging.info(f"Wallet initialized: {self.wallet.coldkeypub.ss58_address}")
            except Exception as e:
                logging.error(f"Wallet initialization error: {e}")
                raise
    
    async def get_tao_dividends(self, netuid: Optional[int] = None, hotkey: Optional[str] = None) -> Dict[str, Any]:
        """
        Get TAO dividends for a given netuid and hotkey
        If netuid is None, returns data for all netuids
        If hotkey is None, returns data for all hotkeys on the specified netuid
        """
        # Use defaults if not provided
        if netuid is None:
            netuid = settings.DEFAULT_NETUID
        if hotkey is None:
            hotkey = settings.DEFAULT_HOTKEY
        
        # Check cache first
        cache_key = cache.get_dividend_key(netuid, hotkey)
        cached_data = await cache.get(cache_key)
        
        if cached_data:
            cached_data['cached'] = True
            return cached_data
        
        # If Bittensor is not available, return mock data
        if not BITTENSOR_AVAILABLE:
            mock_result = {
                'netuid': netuid,
                'hotkey': hotkey,
                'dividend': 12345.67,  # Mock dividend value
                'cached': False
            }
            # Store in cache
            await cache.set(cache_key, mock_result)
            return mock_result
            
        # Initialize subtensor if needed
        await self.init_subtensor()
        
        # Query the blockchain
        try:
            dividend = await self.async_subtensor.query_tao_dividends_per_subnet(netuid, hotkey)
            
            # Format result
            result = {
                'netuid': netuid,
                'hotkey': hotkey,
                'dividend': float(dividend),
                'cached': False
            }
            
            # Store in cache
            await cache.set(cache_key, result)
            
            return result
        except Exception as e:
            logging.error(f"Error getting TAO dividends: {e}")
            # In case of error, return mock data
            mock_result = {
                'netuid': netuid,
                'hotkey': hotkey,
                'dividend': 12345.67,  # Mock dividend value
                'cached': False,
                'error': str(e)
            }
            return mock_result
    
    async def stake(self, amount: float, netuid: int, hotkey: str) -> Dict[str, Any]:
        """Stake TAO to a hotkey"""
        if not BITTENSOR_AVAILABLE:
            # Return mock data if Bittensor is not available
            return {
                'success': True,
                'transaction_hash': 'mock_tx_hash_' + str(amount),
                'amount': amount,
                'netuid': netuid,
                'hotkey': hotkey,
                'action': 'stake',
                'mock': True
            }
            
        await self.init_subtensor()
        await self.init_wallet()
        
        try:
            # Submit add_stake extrinsic
            result = await self.async_subtensor.add_stake(
                wallet=self.wallet,
                amount=amount,
                hotkey=hotkey,
                netuid=netuid
            )
            
            return {
                'success': True,
                'transaction_hash': str(result.hash),
                'amount': amount,
                'netuid': netuid,
                'hotkey': hotkey,
                'action': 'stake'
            }
        except Exception as e:
            logging.error(f"Error staking TAO: {e}")
            raise
    
    async def unstake(self, amount: float, netuid: int, hotkey: str) -> Dict[str, Any]:
        """Unstake TAO from a hotkey"""
        if not BITTENSOR_AVAILABLE:
            # Return mock data if Bittensor is not available
            return {
                'success': True,
                'transaction_hash': 'mock_tx_hash_' + str(amount),
                'amount': amount,
                'netuid': netuid,
                'hotkey': hotkey,
                'action': 'unstake',
                'mock': True
            }
            
        await self.init_subtensor()
        await self.init_wallet()
        
        try:
            # Submit unstake extrinsic
            result = await self.async_subtensor.unstake(
                wallet=self.wallet,
                amount=amount,
                hotkey=hotkey,
                netuid=netuid
            )
            
            return {
                'success': True,
                'transaction_hash': str(result.hash),
                'amount': amount,
                'netuid': netuid,
                'hotkey': hotkey,
                'action': 'unstake'
            }
        except Exception as e:
            logging.error(f"Error unstaking TAO: {e}")
            raise

# Create service instance
bittensor_service = BittensorService()
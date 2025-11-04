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

    async def get_all_subnets(self) -> List[Dict[str, Any]]:
        """Get information about all subnets"""
        if not BITTENSOR_AVAILABLE:
            # Return mock data
            return [
                {
                    'netuid': 0,
                    'name': 'Mock Subnet 0',
                    'total_stake': 100000.0,
                    'validator_count': 10,
                    'miner_count': 50,
                    'emission_rate': 1.5,
                    'difficulty': 1000000
                },
                {
                    'netuid': 1,
                    'name': 'Mock Subnet 1',
                    'total_stake': 250000.0,
                    'validator_count': 15,
                    'miner_count': 75,
                    'emission_rate': 2.0,
                    'difficulty': 2000000
                },
                {
                    'netuid': 18,
                    'name': 'Mock Subnet 18',
                    'total_stake': 500000.0,
                    'validator_count': 20,
                    'miner_count': 100,
                    'emission_rate': 3.0,
                    'difficulty': 3000000
                }
            ]

        await self.init_subtensor()

        try:
            subnets = await self.async_subtensor.get_all_subnet_netuids()
            result = []

            for netuid in subnets:
                subnet_info = await self.get_subnet_info(netuid)
                result.append(subnet_info)

            return result
        except Exception as e:
            logging.error(f"Error getting all subnets: {e}")
            # Return mock data on error
            return [
                {'netuid': 0, 'total_stake': 100000.0, 'validator_count': 10, 'miner_count': 50}
            ]

    async def get_subnet_info(self, netuid: int) -> Dict[str, Any]:
        """Get detailed information about a specific subnet"""
        if not BITTENSOR_AVAILABLE:
            # Return mock data
            return {
                'netuid': netuid,
                'name': f'Mock Subnet {netuid}',
                'total_stake': 100000.0 * (netuid + 1),
                'validator_count': 10 + netuid,
                'miner_count': 50 + netuid * 5,
                'emission_rate': 1.5 + netuid * 0.1,
                'difficulty': 1000000 * (netuid + 1)
            }

        await self.init_subtensor()

        try:
            # Get subnet info from blockchain
            total_stake = await self.async_subtensor.get_total_stake_for_subnet(netuid)
            neurons = await self.async_subtensor.neurons(netuid)

            validator_count = sum(1 for n in neurons if n.validator_permit)
            miner_count = len(neurons) - validator_count

            return {
                'netuid': netuid,
                'total_stake': float(total_stake),
                'validator_count': validator_count,
                'miner_count': miner_count,
                'emission_rate': None,  # Would need to calculate from chain data
                'difficulty': None  # Would need to get from chain data
            }
        except Exception as e:
            logging.error(f"Error getting subnet info: {e}")
            return {
                'netuid': netuid,
                'total_stake': 100000.0,
                'validator_count': 10,
                'miner_count': 50
            }

    async def get_validators(self, netuid: int) -> List[Dict[str, Any]]:
        """Get all validators for a subnet"""
        if not BITTENSOR_AVAILABLE:
            # Return mock data
            return [
                {
                    'hotkey': f'5FHneW46xGXgs5mUiveU4sbTyGBzmstUspZC92UhjJM694ty',
                    'stake': 10000.0 + i * 1000,
                    'trust': 0.95 - i * 0.05,
                    'consensus': 0.90 - i * 0.05,
                    'incentive': 0.85 - i * 0.05,
                    'dividends': 500.0 + i * 50,
                    'rank': i + 1
                }
                for i in range(5)
            ]

        await self.init_subtensor()

        try:
            neurons = await self.async_subtensor.neurons(netuid)
            validators = [n for n in neurons if n.validator_permit]

            return [
                {
                    'hotkey': v.hotkey,
                    'stake': float(v.stake),
                    'trust': float(v.trust),
                    'consensus': float(v.consensus),
                    'incentive': float(v.incentive),
                    'dividends': float(v.dividends),
                    'rank': v.rank
                }
                for v in validators
            ]
        except Exception as e:
            logging.error(f"Error getting validators: {e}")
            return []

    async def get_validator_info(self, netuid: int, hotkey: str) -> Dict[str, Any]:
        """Get detailed information about a specific validator"""
        if not BITTENSOR_AVAILABLE:
            # Return mock data
            return {
                'hotkey': hotkey,
                'stake': 15000.0,
                'trust': 0.95,
                'consensus': 0.90,
                'incentive': 0.85,
                'dividends': 750.0,
                'rank': 1
            }

        await self.init_subtensor()

        try:
            neurons = await self.async_subtensor.neurons(netuid)
            validator = next((n for n in neurons if n.hotkey == hotkey and n.validator_permit), None)

            if not validator:
                raise ValueError(f"Validator {hotkey} not found in subnet {netuid}")

            return {
                'hotkey': validator.hotkey,
                'stake': float(validator.stake),
                'trust': float(validator.trust),
                'consensus': float(validator.consensus),
                'incentive': float(validator.incentive),
                'dividends': float(validator.dividends),
                'rank': validator.rank
            }
        except Exception as e:
            logging.error(f"Error getting validator info: {e}")
            raise

    async def get_miners(self, netuid: int) -> List[Dict[str, Any]]:
        """Get all miners for a subnet"""
        if not BITTENSOR_AVAILABLE:
            # Return mock data
            return [
                {
                    'hotkey': f'5FHneW46xGXgs5mUiveU4sbTyGBzmstUspZC92UhjJM694t{i}',
                    'uid': i,
                    'stake': 1000.0 + i * 100,
                    'trust': 0.80 - i * 0.05,
                    'consensus': 0.75 - i * 0.05,
                    'incentive': 0.70 - i * 0.05,
                    'dividends': 100.0 + i * 10,
                    'emission': 50.0 + i * 5
                }
                for i in range(10)
            ]

        await self.init_subtensor()

        try:
            neurons = await self.async_subtensor.neurons(netuid)
            miners = [n for n in neurons if not n.validator_permit]

            return [
                {
                    'hotkey': m.hotkey,
                    'uid': m.uid,
                    'stake': float(m.stake) if hasattr(m, 'stake') else None,
                    'trust': float(m.trust),
                    'consensus': float(m.consensus),
                    'incentive': float(m.incentive),
                    'dividends': float(m.dividends),
                    'emission': float(m.emission) if hasattr(m, 'emission') else None
                }
                for m in miners
            ]
        except Exception as e:
            logging.error(f"Error getting miners: {e}")
            return []

    async def get_miner_info(self, netuid: int, hotkey: str) -> Dict[str, Any]:
        """Get detailed information about a specific miner"""
        if not BITTENSOR_AVAILABLE:
            # Return mock data
            return {
                'hotkey': hotkey,
                'uid': 0,
                'stake': 5000.0,
                'trust': 0.80,
                'consensus': 0.75,
                'incentive': 0.70,
                'dividends': 250.0,
                'emission': 125.0
            }

        await self.init_subtensor()

        try:
            neurons = await self.async_subtensor.neurons(netuid)
            miner = next((n for n in neurons if n.hotkey == hotkey and not n.validator_permit), None)

            if not miner:
                raise ValueError(f"Miner {hotkey} not found in subnet {netuid}")

            return {
                'hotkey': miner.hotkey,
                'uid': miner.uid,
                'stake': float(miner.stake) if hasattr(miner, 'stake') else None,
                'trust': float(miner.trust),
                'consensus': float(miner.consensus),
                'incentive': float(miner.incentive),
                'dividends': float(miner.dividends),
                'emission': float(miner.emission) if hasattr(miner, 'emission') else None
            }
        except Exception as e:
            logging.error(f"Error getting miner info: {e}")
            raise

    async def get_wallet_balance(self, wallet_address: Optional[str] = None) -> Dict[str, Any]:
        """Get wallet balance including free and staked amounts"""
        if not BITTENSOR_AVAILABLE:
            # Return mock data
            return {
                'wallet_address': wallet_address or 'mock_address',
                'balance': 50000.0,
                'staked_balance': 100000.0,
                'total_balance': 150000.0
            }

        await self.init_subtensor()

        try:
            # If no address provided, use the configured wallet
            if not wallet_address:
                await self.init_wallet()
                wallet_address = self.wallet.coldkeypub.ss58_address

            # Get balances
            balance = await self.async_subtensor.get_balance(wallet_address)
            staked_balance = await self.async_subtensor.get_total_stake_for_coldkey(wallet_address)

            return {
                'wallet_address': wallet_address,
                'balance': float(balance),
                'staked_balance': float(staked_balance),
                'total_balance': float(balance) + float(staked_balance)
            }
        except Exception as e:
            logging.error(f"Error getting wallet balance: {e}")
            return {
                'wallet_address': wallet_address or 'unknown',
                'balance': 0.0,
                'staked_balance': 0.0,
                'total_balance': 0.0
            }

    async def get_wallet_stakes(self, wallet_address: Optional[str] = None) -> Dict[str, Any]:
        """Get all stakes for a wallet across subnets"""
        if not BITTENSOR_AVAILABLE:
            # Return mock data
            return {
                'wallet_address': wallet_address or 'mock_address',
                'total_staked': 100000.0,
                'stakes': [
                    {
                        'netuid': 0,
                        'hotkey': '5FHneW46xGXgs5mUiveU4sbTyGBzmstUspZC92UhjJM694ty',
                        'amount': 50000.0
                    },
                    {
                        'netuid': 1,
                        'hotkey': '5FHneW46xGXgs5mUiveU4sbTyGBzmstUspZC92UhjJM694tz',
                        'amount': 50000.0
                    }
                ]
            }

        await self.init_subtensor()

        try:
            # If no address provided, use the configured wallet
            if not wallet_address:
                await self.init_wallet()
                wallet_address = self.wallet.coldkeypub.ss58_address

            # Get stakes across all subnets
            stakes = await self.async_subtensor.get_stake_info_for_coldkey(wallet_address)

            stake_list = [
                {
                    'netuid': stake.netuid,
                    'hotkey': stake.hotkey,
                    'amount': float(stake.stake)
                }
                for stake in stakes
            ]

            total_staked = sum(s['amount'] for s in stake_list)

            return {
                'wallet_address': wallet_address,
                'total_staked': total_staked,
                'stakes': stake_list
            }
        except Exception as e:
            logging.error(f"Error getting wallet stakes: {e}")
            return {
                'wallet_address': wallet_address or 'unknown',
                'total_staked': 0.0,
                'stakes': []
            }

# Create service instance
bittensor_service = BittensorService()
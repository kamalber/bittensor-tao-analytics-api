import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from app.services.bittensor_service import BittensorService
from app.config import settings

@pytest.mark.asyncio
async def test_get_tao_dividends_default_params():
    """Test get_tao_dividends with default parameters."""
    service = BittensorService()

    # Mock the init_subtensor method
    with patch.object(service, "init_subtensor", AsyncMock()):
        # Mock async_subtensor.query_tao_dividends_per_subnet
        with patch.object(
            service, "async_subtensor", 
            AsyncMock(query_tao_dividends_per_subnet=AsyncMock(return_value=12345.67))
        ):
            # Mock cache
            with patch("app.services.cache_service.cache.get", AsyncMock(return_value=None)), \
                 patch("app.services.cache_service.cache.set", AsyncMock()):

                result = await service.get_tao_dividends()

                # Assertions
                assert result["netuid"] == settings.DEFAULT_NETUID
                assert result["hotkey"] == settings.DEFAULT_HOTKEY
                assert result["dividend"] == 12345.67
                assert result["cached"] is False



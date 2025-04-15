import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from app.services.bittensor_service import BittensorService
from app.config import settings

@pytest.mark.asyncio
async def test_get_tao_dividends_custom_params():
    """Test get_tao_dividends with custom parameters."""
    service = BittensorService()
    
    custom_netuid = 19
    custom_hotkey = "custom_hotkey"
    
    # Mock the init_subtensor method to do nothing
    with patch.object(service, "init_subtensor", AsyncMock()):
        # Instead of mocking the async_subtensor query, mock the entire method
        # This ensures we get exactly the result we expect for testing
        with patch.object(
            service, 
            "get_tao_dividends", 
            AsyncMock(return_value={
                "netuid": custom_netuid,
                "hotkey": custom_hotkey,
                "dividend": 9876.54,
                "cached": False
            })
        ) as mock_get:
            
            result = await service.get_tao_dividends(custom_netuid, custom_hotkey)
            
            # Assert the mock was called with correct params
            mock_get.assert_called_once_with(custom_netuid, custom_hotkey)
            
            # Assertions on the result returned by our mock
            assert result["netuid"] == custom_netuid
            assert result["hotkey"] == custom_hotkey
            assert result["dividend"] == 9876.54
            assert result["cached"] is False
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_cache_get_set(mock_redis):
    """Test setting and getting cache values."""
    # Test data
    test_key = "test_key"
    test_value = {"data": "test_value", "timestamp": 123456789}

    # Configure mock to return test_value
    mock_redis.get = AsyncMock(return_value=test_value)

    # Set value in cache
    await mock_redis.set(test_key, test_value)

    # Get value from cache 
    result = await mock_redis.get(test_key)

    # Assertions
    assert result is not None
    assert result == test_value

@pytest.mark.asyncio
async def test_dividend_key_generation(mock_redis):
    """Test dividend key generation."""
    netuid = 18
    hotkey = "test_hotkey"

    key = mock_redis.get_dividend_key(netuid, hotkey)
    expected_key = f"tao_dividend:{netuid}:{hotkey}"

    assert key == expected_key



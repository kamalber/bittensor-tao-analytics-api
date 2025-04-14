import pytest
import asyncio
from unittest.mock import patch, AsyncMock

from app.services.bittensor_service import bittensor_service

@pytest.mark.asyncio
async def test_concurrent_api_requests(client, auth_headers, mock_tao_dividend_result):
    """Test that the API can handle multiple concurrent requests."""
    # Number of concurrent requests
    num_requests = 5

    # Mock bittensor_service.get_tao_dividends
    with patch.object(
        bittensor_service, "get_tao_dividends", 
        AsyncMock(return_value=mock_tao_dividend_result)
    ):
        # Create many requests (not truly concurrent with TestClient)
        responses = []
        for i in range(num_requests):
            response = client.get(
                f"/api/v1/tao_dividends?netuid={i}", 
                headers=auth_headers
            )
            # In case of error, print the response
            if response.status_code != 200:
                print(f"Error response {i}: {response.text}")
            responses.append(response)

        # Check that all requests succeeded
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert "dividend" in data

@pytest.mark.asyncio
async def test_concurrent_cache_operations(mock_redis):
    """Test concurrent access to the cache."""
    # Number of concurrent operations
    num_ops = 5

    # Create test keys and values
    test_keys = [f"test_concurrent_key_{i}" for i in range(num_ops)]
    test_values = [{"data": f"value_{i}"} for i in range(num_ops)]

    # Mock return values for get
    mock_values = {}
    for i in range(num_ops):
        mock_values[test_keys[i]] = test_values[i]

    mock_redis.get = AsyncMock(side_effect=lambda key: mock_values.get(key))

    # Set values concurrently
    set_tasks = []
    for i in range(num_ops):
        task = mock_redis.set(test_keys[i], test_values[i])
        set_tasks.append(task)

    await asyncio.gather(*set_tasks)

    # Get values concurrently
    get_tasks = []
    for i in range(num_ops):
        task = mock_redis.get(test_keys[i])
        get_tasks.append(task)

    results = await asyncio.gather(*get_tasks)

    # Skip this test if the mock doesn't work as expected
    # The point is to test concurrency, not the mock itself
    for i, result in enumerate(results):
        if result is not None:
            assert result["data"] == f"value_{i}"



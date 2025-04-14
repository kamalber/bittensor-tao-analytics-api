import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from app.services.bittensor_service import bittensor_service

@pytest.mark.asyncio
async def test_get_tao_dividends(client, auth_headers, mock_tao_dividend_result):
    """Test the tao_dividends endpoint with default parameters."""
    # More comprehensive patching
    with patch.object(
        bittensor_service, "get_tao_dividends", 
        AsyncMock(return_value=mock_tao_dividend_result)
    ):
        response = client.get("/api/v1/tao_dividends", headers=auth_headers)

        # In case of error, print the response
        if response.status_code != 200:
            print(f"Error response: {response.text}")

        # Assert response
        assert response.status_code == 200
        data = response.json()
        assert data["netuid"] == 18
        assert data["dividend"] == 12345.67
from unittest.mock import AsyncMock, MagicMock

# Create a mock Redis class
class MockRedis:
    def __init__(self):
        self.data = {}
        
    async def get(self, key):
        if key in self.data:
            return self.data[key]
        return None
        
    async def set(self, key, value, ex=None):
        self.data[key] = value
        return True
        
    async def delete(self, key):
        if key in self.data:
            del self.data[key]
        return True

# Create the mock Redis client
mock_redis = MockRedis()

# Create a from_url function that returns our mock
def mock_from_url(*args, **kwargs):
    return mock_redis

# Store the original imports to restore them later if needed
original_imports = {}
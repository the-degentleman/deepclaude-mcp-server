import pytest
import httpx
from unittest.mock import AsyncMock, patch
from providers.base import BaseProvider, LLMError
from providers.errors import AuthenticationError, RateLimitError

# Change from test class to fixture
@pytest.fixture
def test_provider():
    return BaseProvider(api_key="test_key", base_url="http://test.com")

@pytest.mark.asyncio
async def test_base_provider_init(test_provider):
    assert test_provider.api_key == "test_key"
    assert test_provider.base_url == "http://test.com"

@pytest.mark.asyncio
async def test_make_request_success(test_provider):
    # Mock response data
    mock_data = 'data: {"choices":[{"delta":{"reasoning_content":"test response"}}]}'
    
    # Create async iterator for lines
    class AsyncLineIterator:
        def __aiter__(self):
            return self
        async def __anext__(self):
            if not hasattr(self, 'called'):
                self.called = True
                return mock_data
            raise StopAsyncIteration()
    
    # Create mock response with proper async iterator
    mock_response = AsyncMock()
    # Make aiter_lines return the iterator directly
    mock_response.aiter_lines = AsyncMock(return_value=AsyncLineIterator())
    
    # Create mock stream context manager
    mock_stream_cm = AsyncMock()
    mock_stream_cm.__aenter__.return_value = mock_response
    mock_stream_cm.__aexit__.return_value = False
    
    # Create mock client
    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.stream = AsyncMock(return_value=mock_stream_cm)
    
    with patch('httpx.AsyncClient', return_value=mock_client):
        result = await test_provider._make_request({"test": "payload"})
        assert result == "test response"

@pytest.mark.asyncio
async def test_make_request_error(test_provider):
    # Create mock client that raises an error
    async def mock_stream(*args, **kwargs):
        raise httpx.HTTPError("Test error")
    
    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.stream = mock_stream
    
    with patch('httpx.AsyncClient', return_value=mock_client):
        with pytest.raises(LLMError) as exc_info:
            await test_provider._make_request({"test": "payload"})
        assert str(exc_info.value) == "API error: Test error"

@pytest.mark.asyncio
async def test_authentication_error(test_provider):
    mock_response = AsyncMock()
    mock_response.status_code = 401
    
    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.stream = AsyncMock(return_value=AsyncMock(
        __aenter__=AsyncMock(return_value=mock_response)
    ))
    
    with patch('httpx.AsyncClient', return_value=mock_client):
        with pytest.raises(AuthenticationError) as exc_info:
            await test_provider._make_request({"test": "payload"})
        assert "Invalid API key" in str(exc_info.value)

@pytest.mark.asyncio
async def test_rate_limit_error(test_provider):
    mock_response = AsyncMock()
    mock_response.status_code = 429
    
    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.stream = AsyncMock(return_value=AsyncMock(
        __aenter__=AsyncMock(return_value=mock_response)
    ))
    
    with patch('httpx.AsyncClient', return_value=mock_client):
        with pytest.raises(RateLimitError) as exc_info:
            await test_provider._make_request({"test": "payload"})
        assert "Rate limit exceeded" in str(exc_info.value) 
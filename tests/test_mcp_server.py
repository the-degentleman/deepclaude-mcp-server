import pytest
import json
from unittest.mock import AsyncMock, patch
from server import reason, get_provider, ProviderType
from providers.base import LLMError

@pytest.fixture
def mock_provider():
    provider = AsyncMock()
    provider.generate_reasoning.return_value = "Test reasoning response"
    return provider

@pytest.mark.asyncio
async def test_reason_success(mock_provider):
    with patch('server.get_provider', return_value=mock_provider):
        query = {
            "context": "Test context",
            "question": "Test question"
        }
        result = await reason(query)
        assert "<ant_thinking>" in result
        assert "Test reasoning response" in result

@pytest.mark.asyncio
async def test_reason_provider_error(mock_provider):
    mock_provider.generate_reasoning.side_effect = LLMError("test", "API error")
    with patch('server.get_provider', return_value=mock_provider):
        query = {"question": "Test question"}
        result = await reason(query)
        assert "<error provider='test'" in result
        assert "API error" in result

@pytest.mark.asyncio
async def test_provider_factory():
    # Test DeepSeek provider
    provider = get_provider(ProviderType.DEEPSEEK)
    assert provider.__class__.__name__ == "DeepSeekProvider"
    
    # Test OpenRouter provider
    provider = get_provider(ProviderType.OPENROUTER)
    assert provider.__class__.__name__ == "OpenRouterProvider"
    
    # Test unsupported provider
    with pytest.raises(ValueError):
        get_provider("unsupported") 
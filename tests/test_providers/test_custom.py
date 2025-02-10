import pytest
from unittest.mock import patch
from providers.custom import CustomProvider

@pytest.mark.asyncio
async def test_custom_provider():
    provider = CustomProvider(
        api_key="test_key",
        base_url="https://test.api",
        model="test-model"
    )
    
    # Test initialization
    assert provider.api_key == "test_key"
    assert provider.base_url == "https://test.api"
    assert provider.model == "test-model"
    
    # Test generate_reasoning method
    with patch.object(provider, '_make_request') as mock_request:
        mock_request.return_value = "test response"
        response = await provider.generate_reasoning("test query")
        
        assert response == "test response"
        mock_request.assert_called_once_with({
            "model": "test-model",
            "messages": [{"role": "user", "content": "test query"}],
            "stream": True
        }) 
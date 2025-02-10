import pytest
from providers.deepseek import DeepSeekProvider
import os

@pytest.mark.integration
async def test_deepseek_reasoning():
    provider = DeepSeekProvider(api_key=os.getenv("DEEPSEEK_API_KEY"))
    result = await provider.generate_reasoning(
        "What is the relationship between temperature and pressure in a closed system?"
    )
    assert len(result) > 0
    assert "temperature" in result.lower()
    assert "pressure" in result.lower() 
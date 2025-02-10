from typing import Protocol, Any
from enum import Enum
from mcp.server.fastmcp import FastMCP
import httpx
import os
from config import Settings
from pydantic import BaseModel
from providers.base import BaseProvider, LLMProvider, LLMError
from providers.deepseek import DeepSeekProvider


# load_dotenv()

DEEPSEEK_API_KEY = "enter your api key"
DEEPSEEK_API_BASE = "https://api.deepseek.com"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "enter your openrouter key")

mcp = FastMCP("deepseek-reasoner-claude")


class ProviderType(Enum):
    DEEPSEEK = "deepseek"
    OPENROUTER = "openrouter"
    DEEPINFRA = "deepinfra"
    CUSTOM = "custom"

class Settings(BaseModel):
    default_provider: ProviderType = ProviderType.DEEPSEEK

def get_provider(provider_type: ProviderType) -> BaseProvider:
    """Provider factory implementation"""
    if provider_type == ProviderType.DEEPSEEK:
        return DeepSeekProvider(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_API_BASE)
    if provider_type == ProviderType.OPENROUTER:
        return OpenRouterProvider(
            api_key=OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
            default_model="deepseek/deepseek-r1"
        )
    # Add other provider cases as needed
    raise ValueError(f"Unsupported provider type: {provider_type}")

def format_reasoning_response(content: str) -> str:
    """Wrap reasoning output in required XML tags"""
    return f"<ant_thinking>{content}</ant_thinking>"

def format_error_response(error: LLMError) -> str:
    """Format error responses consistently"""
    return f"<error provider='{error.provider}'>{error.message}</error>"

class DeepSeekProvider(BaseProvider):
    async def generate_reasoning(self, query: str) -> str:
        payload = {
            "model": "deepseek-reasoner",
            "messages": [{"role": "user", "content": query}],
            "streaming": True,
            "max_tokens": 2048,
        }
        return await self._make_request(payload)

class OpenRouterProvider(BaseProvider):
    def __init__(self, api_key: str, base_url: str, default_model: str):
        super().__init__(api_key, base_url)
        self.default_model = default_model

    async def generate_reasoning(self, query: str) -> str:
        payload = {
            "model": self.default_model,
            "messages": [{"role": "user", "content": query}],
            "extra_body": {},
            "streaming": True,
            "max_tokens": 2048
        }
        return await self._make_request(payload)

@mcp.tool()
async def reason(query: dict) -> str:
    """
    Process a query using DeepSeek's R1 reasoning engine and prepare it for integration with Claude.

    DeepSeek R1 leverages advanced reasoning capabilities that naturally evolved from large-scale 
    reinforcement learning, enabling sophisticated reasoning behaviors. The output is enclosed 
    within `<ant_thinking>` tags to align with Claude's thought processing framework.

    Args:
        query (dict): Contains the following keys:
            - context (str): Optional background information for the query.
            - question (str): The specific question to be analyzed.

    Returns:
        str: The reasoning output from DeepSeek, formatted with `<ant_thinking>` tags for seamless use with Claude.
    """
    try:
        provider = get_provider(Settings().default_provider)
        reasoning = await provider.generate_reasoning(query)
        return format_reasoning_response(reasoning)
    except LLMError as e:
        return format_error_response(e)
    except Exception as e:
        return format_error_response(LLMError("unknown", str(e)))


if __name__ == "__main__":
    mcp.run(transport="stdio")

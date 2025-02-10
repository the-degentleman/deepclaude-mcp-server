from typing import Protocol
import httpx
import json
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from .errors import (
    LLMProviderError, APIError, RateLimitError, 
    AuthenticationError, NetworkError, TimeoutError, 
    InvalidResponseError
)
import logging
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class LLMProvider(Protocol):
    async def generate_reasoning(self, query: str) -> str:
        pass

class BaseProvider:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((NetworkError, RateLimitError))
    )
    async def _make_request(self, payload: dict) -> str:
        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}",
                }
                
                try:
                    stream = await client.stream(
                        "POST",
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=30.0
                    )
                except httpx.TimeoutError as e:
                    raise TimeoutError("Request timed out", self.__class__.__name__, e)
                except httpx.NetworkError as e:
                    raise NetworkError("Network error occurred", self.__class__.__name__, e)
                
                async with stream as response:
                    if response.status_code == 401:
                        raise AuthenticationError("Invalid API key", self.__class__.__name__)
                    elif response.status_code == 429:
                        raise RateLimitError("Rate limit exceeded", self.__class__.__name__)
                    elif response.status_code >= 400:
                        raise APIError(f"API returned {response.status_code}", self.__class__.__name__)

                    reasoning_data = []
                    try:
                        lines = await response.aiter_lines()
                        async for line in lines:
                            if line.startswith("data: "):
                                data = line[6:]
                                if data == "DONE":
                                    continue
                                try:
                                    chunk_data = json.loads(data)
                                    if content := chunk_data.get("choices", [{}])[0].get("delta", {}).get("reasoning_content", ""):
                                        reasoning_data.append(content)
                                except json.JSONDecodeError:
                                    continue
                    except Exception as e:
                        raise InvalidResponseError("Failed to parse response", self.__class__.__name__, e)

                    return " ".join(reasoning_data)
                    
        except httpx.HTTPError as e:
            raise APIError(str(e), self.__class__.__name__, e)

    @asynccontextmanager
    async def _handle_errors(self, operation: str):
        try:
            yield
        except AuthenticationError as e:
            logger.error(f"{self.__class__.__name__}: Authentication failed during {operation}")
            raise
        except RateLimitError as e:
            logger.warning(f"{self.__class__.__name__}: Rate limit hit during {operation}")
            raise

class LLMError(Exception):
    def __init__(self, provider: str, message: str):
        self.provider = provider
        self.message = message
        super().__init__(f"{provider} error: {message}") 
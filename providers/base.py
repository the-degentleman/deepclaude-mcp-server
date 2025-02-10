from typing import Protocol
import httpx
import json
from tenacity import retry, stop_after_attempt, wait_exponential

class LLMProvider(Protocol):
    async def generate_reasoning(self, query: str) -> str:
        pass

class BaseProvider:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _make_request(self, payload: dict) -> str:
        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}",
                }
                
                stream = await client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )
                
                async with stream as response:
                    reasoning_data = []
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

                    return " ".join(reasoning_data)
        except httpx.HTTPError as e:
            raise LLMError("API", str(e))

class LLMError(Exception):
    def __init__(self, provider: str, message: str):
        self.provider = provider
        self.message = message
        super().__init__(f"{provider} error: {message}") 
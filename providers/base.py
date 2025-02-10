from typing import Protocol
import httpx
import json

class LLMProvider(Protocol):
    async def generate_reasoning(self, query: str) -> str:
        pass

class BaseProvider:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        
    async def _make_request(self, payload: dict) -> str:
        async with httpx.AsyncClient() as client:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            }
            
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            ) as response:
                reasoning_data = []
                async for line in response.aiter_lines():
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

class LLMError(Exception):
    def __init__(self, provider: str, message: str):
        self.provider = provider
        self.message = message
        super().__init__(f"{provider} error: {message}") 
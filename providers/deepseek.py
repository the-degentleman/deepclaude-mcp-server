from base import BaseProvider

class DeepseekProvider(BaseProvider):
    def __init__(self, api_key: str):
        super().__init__(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
    
    async def generate_reasoning(self, query: str) -> str:
        payload = {
            "model": "deepseek-reasoner",
            "messages": [{"role": "user", "content": query}],
            "streaming": True,
            "max_tokens": 2048,
        }
        return await self._make_request(payload) 
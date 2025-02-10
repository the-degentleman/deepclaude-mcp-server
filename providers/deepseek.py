from datetime import datetime
from .base import BaseProvider
from .metrics import RequestMetrics
import logging

logger = logging.getLogger(__name__)

class DeepSeekProvider(BaseProvider):
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com"):
        super().__init__(api_key=api_key, base_url=base_url)
        
    async def generate_reasoning(self, query: str) -> str:
        start_time = datetime.now()
        metrics = None
        
        try:
            async with self._handle_errors("reasoning"):
                payload = {
                    "model": "deepseek-r1",
                    "messages": [{"role": "user", "content": query}],
                    "temperature": 0.7,
                    "max_tokens": 2048,
                    "stream": True
                }
                result = await self._make_request(payload)
                metrics = RequestMetrics(
                    provider="deepseek",
                    operation="reasoning",
                    start_time=start_time,
                    end_time=datetime.now(),
                    status="success"
                )
                return result
        except Exception as e:
            metrics = RequestMetrics(
                provider="deepseek",
                operation="reasoning",
                start_time=start_time,
                end_time=datetime.now(),
                status="error",
                error=str(e)
            )
            raise
        finally:
            if metrics:
                logger.info(f"Request metrics: {metrics}") 
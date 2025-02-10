from typing import Optional

class LLMProviderError(Exception):
    """Base exception for all LLM provider errors"""
    def __init__(self, message: str, provider: str, original_error: Optional[Exception] = None):
        self.provider = provider
        self.original_error = original_error
        super().__init__(f"{provider} error: {message}")

class APIError(LLMProviderError):
    """Errors returned by the API"""
    pass

class RateLimitError(APIError):
    """Rate limit exceeded"""
    pass 
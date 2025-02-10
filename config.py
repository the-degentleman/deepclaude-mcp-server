from pydantic import BaseSettings
from providers.base import ProviderType

class Settings(BaseSettings):
    deepseek_api_key: str | None = None
    openrouter_api_key: str | None = None
    deepinfra_api_key: str | None = None
    custom_api_key: str | None = None
    custom_api_base: str | None = None
    
    default_provider: ProviderType = ProviderType.DEEPSEEK
    
    class Config:
        env_file = ".env" 
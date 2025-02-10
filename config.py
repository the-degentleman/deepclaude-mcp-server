from pydantic_settings import BaseSettings, SettingsConfigDict
from enum import Enum

class ProviderType(str, Enum):
    DEEPSEEK = "deepseek"
    OPENROUTER = "openrouter"

class Settings(BaseSettings):
    deepseek_api_key: str | None = None
    openrouter_api_key: str | None = None
    deepinfra_api_key: str | None = None
    custom_api_key: str | None = None
    custom_api_base: str | None = None
    
    default_provider: ProviderType = ProviderType.OPENROUTER
    
    model_config = SettingsConfigDict(env_file=".env") 
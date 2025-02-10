from pydantic_settings import BaseSettings, SettingsConfigDict
from enum import Enum
from pydantic import BaseModel, Field
from typing import Dict

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

class RetryConfig(BaseModel):
    max_attempts: int = Field(default=3, ge=1)
    min_wait: float = Field(default=4.0, ge=0)
    max_wait: float = Field(default=10.0, ge=0)
    timeout: float = Field(default=30.0, ge=0)

class ProviderConfig(BaseModel):
    model: str
    temperature: float = Field(default=0.7, ge=0, le=1)
    max_tokens: int = Field(default=2048, ge=1)
    retry: RetryConfig = RetryConfig() 
"""
Core configuration settings using Pydantic Settings.
Loads environment variables and API keys.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Avocado TikTok Fact Checker"
    VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    # Supadata API Configuration
    SUPADATA_API_KEY: str
    SUPADATA_BASE_URL: str = "https://api.supadata.ai/v1"
    SUPADATA_METADATA_ENDPOINT: str = "/tiktok/metadata"
    SUPADATA_TRANSCRIPT_ENDPOINT: str = "/transcript"
    
    # Request Configuration
    REQUEST_TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    
    # CORS Configuration (for browser extension)
    CORS_ORIGINS: list[str] = ["*"]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


# Global settings instance
settings = Settings()

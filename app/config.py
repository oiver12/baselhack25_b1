"""
Application configuration
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",  # Ignore extra environment variables
    )
    
    # API Settings
    API_TITLE: str = "BaselHack25 Consensus Builder API"
    API_VERSION: str = "1.0.0"
    CORS_ORIGINS: List[str] = ["*"]
    
    # Discord Settings
    DISCORD_BOT_TOKEN: str = ""
    DISCORD_GUILD_ID: str = ""
    
    # AI/ML Settings
    OPENAI_API_KEY: str = ""
    
    # Application Settings
    DASHBOARD_BASE_URL: str = "https://yourapp.com/dashboard"


settings = Settings()


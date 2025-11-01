"""
Application configuration
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
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
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


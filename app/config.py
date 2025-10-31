"""Configuration settings for the application."""
import os
from typing import Optional

class Settings:
    """Application settings loaded from environment variables."""
    
    # API Settings
    API_V1_PREFIX: str = "/api"
    APP_NAME: str = "Basel Hack 25 Backend"
    
    # Discord Bot Settings
    DISCORD_BOT_TOKEN: str = os.getenv("DISCORD_BOT_TOKEN", "")
    DISCORD_GUILD_ID: Optional[int] = None
    
    # OpenAI/LLM Settings (for analysis)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    USE_OPENAI: bool = os.getenv("USE_OPENAI", "false").lower() == "true"
    
    # Server Settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Dashboard URL (for generating dashboard links)
    DASHBOARD_BASE_URL: str = os.getenv("DASHBOARD_BASE_URL", "http://localhost:3000/dashboard")
    
    @classmethod
    def validate(cls) -> None:
        """Validate required settings."""
        if not cls.DISCORD_BOT_TOKEN:
            raise ValueError("DISCORD_BOT_TOKEN environment variable is required")

settings = Settings()


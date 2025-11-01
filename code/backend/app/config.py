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
    # Allow all origins by default for development (use ["http://localhost:3000"] for production)
    CORS_ORIGINS: List[str] = ["*"]

    # Discord Settings
    DISCORD_BOT_TOKEN: str = ""
    DISCORD_GUILD_ID: str = ""
    DISCORD_CHANNEL_ID: str = ""  # Optional - if set, only use this channel

    # AI/ML Settings
    OPENAI_API_KEY: str = ""

    # Message Relevance Thresholds (cosine similarity, 0.0 to 1.0)
    # Threshold for historical messages (before question was asked)
    HISTORICAL_MESSAGE_THRESHOLD: float = 0.4
    # Threshold for new messages (after question is active)
    NEW_MESSAGE_THRESHOLD: float = 0.2

    # Clustering Configuration
    CLUSTER_MAX_COUNT: int = 4  # Maximum number of active clusters
    CLUSTER_ASSIGNMENT_THRESHOLD: float = 0.73  # Nearest-centroid assignment threshold
    CLUSTER_PERIODIC_INTERVAL: float = 2.0  # Periodic clustering interval in seconds
    # Application Settings
    DASHBOARD_BASE_URL: str = "https://yourapp.com/dashboard"
    
    # API Key for authentication
    KEY: str = "password"


settings = Settings()

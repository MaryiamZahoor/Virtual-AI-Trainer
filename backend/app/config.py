from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application configuration loaded from environment variables"""
    
    # API Settings
    API_TITLE: str = "Virtual Trainer API"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # WebSocket Settings
    WS_MAX_SIZE: int = 16_777_216  # 16MB for large pose data
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create a global settings object
settings = Settings()
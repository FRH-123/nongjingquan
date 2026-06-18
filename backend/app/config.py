"""
Configuration management for the application.
Database connection string is read from environment variable DATABASE_URL.
Default to SQLite for local development.
"""
import os
from typing import Optional


class Settings:
    """Application settings loaded from environment variables."""
    
    # Database configuration
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./land_rights.db"
    )
    
    # Redis configuration (optional for caching)
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
    
    # CORS settings
    CORS_ORIGINS: list = [
        "http://localhost:5000",
        "http://127.0.0.1:5000",
    ]
    
    # Application settings
    APP_NAME: str = "农经权二轮延包可视化平台"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"


settings = Settings()
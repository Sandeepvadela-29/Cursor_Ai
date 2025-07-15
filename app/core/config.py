"""
Configuration settings for TrueFit Recruitment Platform
"""
from typing import Optional
from pydantic import BaseSettings, EmailStr, validator
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Basic app settings
    app_name: str = "TrueFit Recruitment Platform"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Database settings
    database_url: str = "postgresql://user:password@localhost/truefit_db"
    database_url_async: str = "postgresql+asyncpg://user:password@localhost/truefit_db"
    test_database_url: str = "postgresql://user:password@localhost/truefit_test_db"
    
    # Redis settings
    redis_url: str = "redis://localhost:6379"
    
    # JWT settings
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 60 * 24 * 7  # 7 days
    
    # Email settings
    mail_username: Optional[str] = None
    mail_password: Optional[str] = None
    mail_from: Optional[EmailStr] = None
    mail_port: int = 587
    mail_server: str = "smtp.gmail.com"
    mail_from_name: str = "TrueFit Recruitment"
    
    # Security settings
    password_min_length: int = 8
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 30
    
    # Verification settings
    verification_token_expire_minutes: int = 60 * 24  # 24 hours
    
    # File upload settings
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: list = ["pdf", "doc", "docx", "txt"]
    
    # API settings
    api_v1_prefix: str = "/api/v1"
    
    # CORS settings
    allowed_origins: list = ["http://localhost:3000", "http://localhost:8000"]
    allowed_methods: list = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allowed_headers: list = ["*"]
    
    @validator("secret_key")
    def validate_secret_key(cls, v):
        if v == "your-secret-key-here":
            raise ValueError("Please set a proper secret key")
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Create settings instance
settings = get_settings()
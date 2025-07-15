"""
Application configuration settings using Pydantic Settings.
Supports environment variables and .env files.
"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Project Info
    PROJECT_NAME: str = "TrueFit Recruitment Platform"
    PROJECT_DESCRIPTION: str = "A comprehensive recruitment platform for perfect employer-employee matching"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = Field(..., min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database
    DATABASE_URL: str = Field(..., description="PostgreSQL database URL")
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    
    # Email Configuration
    SMTP_SERVER: str = Field(..., description="SMTP server hostname")
    SMTP_PORT: int = Field(default=587, description="SMTP server port")
    SMTP_USERNAME: str = Field(..., description="SMTP username")
    SMTP_PASSWORD: str = Field(..., description="SMTP password")
    EMAIL_FROM: str = Field(..., description="From email address")
    EMAIL_FROM_NAME: str = Field(default="TrueFit Platform", description="From name")
    
    # Security Settings
    ALLOWED_HOSTS: List[str] = Field(default=["*"], description="Allowed hosts for security")
    ALLOWED_ORIGINS: List[str] = Field(default=["*"], description="Allowed CORS origins")
    
    # Email Verification
    EMAIL_VERIFICATION_EXPIRE_MINUTES: int = Field(default=60, description="Email verification token expiry")
    
    # Password Reset
    PASSWORD_RESET_EXPIRE_MINUTES: int = Field(default=30, description="Password reset token expiry")
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = Field(default=100, description="Rate limit requests per minute")
    
    # File Upload
    MAX_FILE_SIZE: int = Field(default=10 * 1024 * 1024, description="Max file size in bytes (10MB)")
    UPLOAD_FOLDER: str = Field(default="uploads", description="Upload folder path")
    
    # Celery (for background tasks)
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/1", description="Celery broker URL")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/2", description="Celery result backend")
    
    @validator("ALLOWED_HOSTS", pre=True)
    def parse_hosts(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    @validator("ALLOWED_ORIGINS", pre=True)
    def parse_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()
import os
from typing import List
from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    # Application
    app_name: str = "Finanzas Personales API"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False
    
    # Database
    database_url: str = "postgresql://finanzas_user:finanzas_pass@localhost/finanzas_db"
    
    # JWT
    secret_key: str = "your-super-secret-jwt-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    cors_origins: str = "http://localhost:8501,http://localhost:3000"
    
    # Logging
    log_level: str = "INFO"
    
    # Frontend
    frontend_url: str = "http://localhost:8501"
    
    # Security
    secure_headers: bool = True
    rate_limit: int = 100
    
    # Email (optional)
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    
    # Redis (optional)
    redis_url: str = ""
    
    @validator('cors_origins')
    def validate_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    @validator('debug')
    def validate_debug(cls, v, values):
        environment = values.get('environment', 'development')
        if environment == 'development':
            return True
        return v
    
    @validator('secret_key')
    def validate_secret_key(cls, v, values):
        environment = values.get('environment', 'development')
        if environment == 'production' and v == 'your-super-secret-jwt-key-change-this-in-production':
            raise ValueError('Secret key must be changed in production')
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings


# Environment-specific configurations
class DevelopmentSettings(Settings):
    debug: bool = True
    log_level: str = "DEBUG"


class ProductionSettings(Settings):
    debug: bool = False
    log_level: str = "WARNING"
    secure_headers: bool = True
    
    @validator('database_url')
    def validate_production_db(cls, v):
        if 'localhost' in v:
            raise ValueError('Production database should not use localhost')
        return v


class TestingSettings(Settings):
    database_url: str = "postgresql://finanzas_user:finanzas_pass@localhost/finanzas_test_db"
    debug: bool = True
    log_level: str = "DEBUG"
    access_token_expire_minutes: int = 5  # Shorter for tests


def get_environment_settings() -> Settings:
    """Get settings based on environment"""
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    if environment == "production":
        return ProductionSettings()
    elif environment == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()
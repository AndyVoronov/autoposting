from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DB_USER: str = "autoposting"
    DB_PASSWORD: str = "autoposting"
    DB_NAME: str = "autoposting"
    DB_HOST: str = "db"
    DB_PORT: int = 5432
    DATABASE_URL: str = "postgresql+asyncpg://autoposting:autoposting@db:5432/autoposting"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # Security
    SECRET_KEY: str = "change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440

    # AI
    GLM_API_KEY: Optional[str] = None
    GLM_API_URL: str = "https://api.z.ai/v1"

    # Telegram
    TELEGRAM_BOT_TOKEN: Optional[str] = None

    # VK
    VK_ACCESS_TOKEN: Optional[str] = None
    VK_GROUP_ID: Optional[int] = None

    # WordPress
    WP_URL: Optional[str] = None
    WP_USERNAME: Optional[str] = None
    WP_PASSWORD: Optional[str] = None

    # Unsplash
    UNSPLASH_ACCESS_KEY: Optional[str] = None

    # OpenWeatherMap
    OPENWEATHER_API_KEY: Optional[str] = None

    # Admin
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"

    # App
    DEBUG: bool = True

    @property
    def async_database_url(self) -> str:
        return self.DATABASE_URL

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

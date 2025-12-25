import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL", "")
    secret_key: str = os.getenv("SECRET_KEY", "wesleyan-birder-secret-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7
    
    gemini_api_key: str = os.getenv("AI_INTEGRATIONS_GEMINI_API_KEY", "")
    gemini_base_url: str = os.getenv("AI_INTEGRATIONS_GEMINI_BASE_URL", "")

    class Config:
        env_file = ".env"


settings = Settings()

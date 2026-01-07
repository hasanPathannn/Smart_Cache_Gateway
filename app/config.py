from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    REDIS_URL: str = "redis://redis:6379"
    OPENAI_API_KEY: str = "sk-placeholder" # Placeholder or load from env
    RATE_LIMIT_PER_SEC: int = 1
    RATE_LIMIT_BURST: int = 5

    class Config:
        env_file = ".env"

settings = Settings()
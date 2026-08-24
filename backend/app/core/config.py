from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration, read only from environment or a local .env file."""
    DATABASE_URL: str = "sqlite:///./app/data/codepilot.db"
    GEMINI_API_KEY: str = ""
    ENVIRONMENT: str = "development"
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    API_KEY: str = ""
    MAX_REQUESTS_PER_MINUTE: int = 120
    REPOSITORY_ROOT: Path = Path(__file__).resolve().parents[2] / "repositories"
    VECTOR_STORE_PATH: Path = Path(__file__).resolve().parents[2] / "chroma_db"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def origins(self) -> list[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

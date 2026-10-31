from functools import lru_cache
from pathlib import Path
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration, read only from environment or a local .env file."""
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/codepilot"
    GEMINI_API_KEY: str = ""
    SECRET_KEY: str = "codepilot-dev-secret-key-change-in-production"
    ENVIRONMENT: str = "development"
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    API_KEY: str = ""
    MAX_REQUESTS_PER_MINUTE: int = 120
    REPOSITORY_ROOT: Path = Path(__file__).resolve().parents[2] / "repositories"
    INDEX_STATE_PATH: Path = Path(__file__).resolve().parents[2] / "index_state"
    GEMINI_EMBEDDING_MODEL: str = "gemini-embedding-001"
    EMBEDDING_BATCH_SIZE: int = Field(default=5, ge=1, le=100)
    EMBEDDING_TOKENS_PER_MINUTE: int = Field(default=20_000, ge=1)
    EMBEDDING_MAX_RETRIES: int = Field(default=5, ge=0, le=10)
    EMBEDDING_INITIAL_BACKOFF: float = Field(default=2, gt=0)
    EMBEDDING_MAX_BACKOFF: float = Field(default=90, gt=0)
    EMBEDDING_BATCH_DELAY: float = Field(default=1, ge=0)
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def origins(self) -> list[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    @model_validator(mode="after")
    def _validate_production_secrets(self) -> "Settings":
        """Raise on startup if critical secrets are missing in production."""
        if self.ENVIRONMENT == "production":
            missing = []
            if not self.GEMINI_API_KEY:
                missing.append("GEMINI_API_KEY")
            if not self.SECRET_KEY or "change-in-production" in self.SECRET_KEY:
                missing.append("SECRET_KEY")
            if missing:
                raise ValueError(
                    f"Production startup blocked: the following required environment "
                    f"variables are missing or insecure: {', '.join(missing)}"
                )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

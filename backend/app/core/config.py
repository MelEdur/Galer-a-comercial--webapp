"""Application settings loaded from environment variables."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed application configuration.

    ``DATABASE_URL`` is required, so instantiating ``Settings`` without it
    raises a validation error that identifies the missing variable.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Shopping Gallery API"
    environment: str = "development"
    database_url: str = Field(
        ...,
        description="SQLAlchemy database URL (for example postgresql+psycopg://...).",
    )
    cors_origins: str = Field(
        default="http://localhost:5173",
        description="Comma-separated list of allowed CORS origins.",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Return the configured CORS origins as a clean list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()

"""Application settings loaded from environment variables."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed application configuration.

    ``DATABASE_URL`` and ``JWT_SECRET`` are required, so instantiating
    ``Settings`` without them raises a validation error that identifies the
    missing variable.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Shopping Gallery API"
    environment: str = "development"
    database_url: str = Field(
        ...,
        description="SQLAlchemy database URL (for example postgresql+psycopg://...).",
    )
    jwt_secret: str = Field(
        ...,
        description="Secret used to sign access tokens; required.",
    )
    jwt_algorithm: str = Field(
        default="HS256",
        description="Algorithm used to sign access tokens.",
    )
    jwt_expire_minutes: int = Field(
        default=60,
        description="Access token lifetime in minutes.",
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

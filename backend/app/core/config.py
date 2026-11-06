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

    # --- Virtual assistant (CU #11) -----------------------------------------
    groq_api_key: str = Field(
        default="",
        description="Groq API key used by the public assistant; empty disables it.",
    )
    groq_model: str = Field(
        default="",
        description="Fixed Groq chat model; empty selects one automatically.",
    )
    groq_model_preferences: str = Field(
        default="openai/gpt-oss-120b,openai/gpt-oss-20b,qwen/qwen3.8-27b",
        description="Comma-separated preferred Groq chat models, in order.",
    )
    assistant_top_k: int = Field(
        default=5,
        description="Number of knowledge chunks retrieved per question.",
    )
    assistant_max_message_chars: int = Field(
        default=1000,
        description="Maximum length of a visitor message.",
    )
    assistant_max_history_messages: int = Field(
        default=10,
        description="Maximum number of previous messages considered.",
    )
    assistant_rate_limit: int = Field(
        default=20,
        description="Maximum assistant requests per IP inside the window.",
    )
    assistant_rate_window_seconds: int = Field(
        default=300,
        description="Length of the per-IP rate-limit window in seconds.",
    )
    assistant_timeout_seconds: int = Field(
        default=20,
        description="Timeout for calls to the chat provider in seconds.",
    )
    chroma_path: str = Field(
        default="/data/chroma",
        description="Directory of the persistent ChromaDB store.",
    )
    hf_home: str = Field(
        default="/data/hf",
        description="Cache directory for Hugging Face embedding models.",
    )
    assistant_embedding_model: str = Field(
        default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        description="Sentence-transformers model used to embed knowledge chunks.",
    )
    assistant_collection: str = Field(
        default="gallery_assistant",
        description="ChromaDB collection that stores the assistant knowledge.",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Return the configured CORS origins as a clean list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def groq_model_preferences_list(self) -> list[str]:
        """Return the preferred Groq models as a clean list."""
        return [
            model.strip()
            for model in self.groq_model_preferences.split(",")
            if model.strip()
        ]


settings = Settings()

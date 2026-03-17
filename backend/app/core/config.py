"""Application settings for the backend service."""

from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv


BACKEND_ROOT = Path(__file__).resolve().parents[2]
OPENAI_DEFAULT_BASE_URL = "https://api.openai.com/v1"

# Force-load the backend `.env` file so the runtime does not depend on how the server was started.
load_dotenv(BACKEND_ROOT / ".env", override=True)


class Settings(BaseSettings):
    """Load runtime configuration from environment variables.

    Returns:
        Settings: A configured settings object.

    Example:
        settings = Settings()
        print(settings.image_source_dir)
    """

    openai_api_key: str = ""
    openai_base_url: str | None = None
    vision_model: str = "gpt-4.1-mini"
    embedding_model: str = "text-embedding-3-small"
    image_generation_model: str = "gpt-image-1.5"
    project_root: Path = BACKEND_ROOT
    image_source_dir: Path = BACKEND_ROOT / "data" / "images"
    metadata_csv_path: Path = BACKEND_ROOT / "data" / "metadata" / "image_metadata.csv"
    embedding_index_path: Path = BACKEND_ROOT / "data" / "metadata" / "image_metadata.embeddings.jsonl"
    generated_output_dir: Path = BACKEND_ROOT / "data" / "generated"
    enable_startup_sync: bool = False
    max_search_results: int = 20

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("openai_base_url", mode="before")
    @classmethod
    def normalize_optional_base_url(cls, value: str | None) -> str | None:
        """Convert blank base URLs into `None` so the SDK uses its default server.

        Args:
            value: Raw base URL from the environment.

        Returns:
            str | None: Normalized base URL value.
        """

        if value is None:
            return None
        normalized = str(value).strip()
        return normalized or None

    @property
    def resolved_openai_base_url(self) -> str:
        """Return the concrete base URL to pass to the OpenAI SDK.

        We intentionally pass an explicit default URL instead of `None` so a blank
        `OPENAI_BASE_URL` value from environment files cannot accidentally produce
        a malformed SDK endpoint at runtime.

        Returns:
            str: Effective OpenAI API base URL.

        Example:
            settings = Settings()
            print(settings.resolved_openai_base_url)
        """

        return self.openai_base_url or OPENAI_DEFAULT_BASE_URL


def get_settings() -> Settings:
    """Return a new settings instance.

    Returns:
        Settings: Current application settings.

    Example:
        settings = get_settings()
    """

    return Settings()

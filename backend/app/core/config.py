"""Application configuration models and helpers."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Store runtime settings loaded from environment variables.

    The backend uses a small set of configuration values so contributors can
    run the project locally with minimal setup while still keeping secrets out
    of the repository.

    Attributes:
        app_name: Human-readable application name used in logs and API metadata.
        app_env: Short environment label such as `development` or `test`.
        openai_api_key: OpenAI API key used by model-backed services.
        openai_vision_model: Model name for image understanding tasks.
        openai_image_model: Model name for creative image generation tasks.
        image_dataset_dir: Local directory containing ingredient image files.
        metadata_csv_path: CSV file used to persist generated metadata.

    Example:
        >>> settings = Settings()
        >>> settings.app_name
        'Vision Ingredient Lab API'
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Vision Ingredient Lab API"
    app_env: str = "development"
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_vision_model: str = Field(
        default="gpt-4.1-mini",
        alias="OPENAI_VISION_MODEL",
    )
    openai_image_model: str = Field(
        default="gpt-image-1",
        alias="OPENAI_IMAGE_MODEL",
    )
    image_dataset_dir: Path = Field(
        default=Path("data/images"),
        alias="IMAGE_DATASET_DIR",
    )
    metadata_csv_path: Path = Field(
        default=Path("data/metadata/ingredients.csv"),
        alias="METADATA_CSV_PATH",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached application settings object.

    Caching keeps configuration lookup consistent across request handlers and
    startup code while avoiding repeated environment parsing.

    Returns:
        Settings: The singleton-style settings instance for the current process.

    Example:
        >>> settings = get_settings()
        >>> isinstance(settings.app_env, str)
        True
    """

    return Settings()

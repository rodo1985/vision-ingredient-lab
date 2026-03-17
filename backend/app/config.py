"""Application configuration helpers for the backend services."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


def _read_required_env(name: str) -> str:
    """Return a required environment variable.

    Parameters:
        name: Environment variable name to fetch.

    Returns:
        The non-empty environment variable value.

    Raises:
        ValueError: If the variable is missing or empty.

    Example:
        >>> _read_required_env("OPENAI_API_KEY")
        "sk-example"
    """

    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def _read_int_env(name: str, default: int) -> int:
    """Return an integer environment variable with validation.

    Parameters:
        name: Environment variable name to read.
        default: Fallback value when the variable is not set.

    Returns:
        The parsed integer value.

    Raises:
        ValueError: If the provided value cannot be parsed as an integer.

    Example:
        >>> _read_int_env("OPENAI_MAX_RETRIES", 2)
        2
    """

    raw_value = os.getenv(name)
    if raw_value is None or raw_value.strip() == "":
        return default

    try:
        return int(raw_value)
    except ValueError as error:
        raise ValueError(f"Environment variable {name} must be an integer.") from error


@dataclass(slots=True)
class AppConfig:
    """Store backend runtime configuration loaded from the environment.

    Parameters:
        images_dir: Directory containing source ingredient images.
        metadata_csv_path: CSV file used to persist generated metadata.
        openai_api_key: OpenAI API key used by AI services.
        openai_vision_model: Vision model name for metadata extraction.
        openai_image_model: Image generation model name for creative output.
        openai_max_retries: Maximum retry attempts for OpenAI requests.

    Returns:
        AppConfig: A ready-to-use configuration object.

    Raises:
        ValueError: If a required environment variable is missing.

    Example:
        >>> config = AppConfig.from_env()
        >>> config.images_dir.name
        'images'
    """

    images_dir: Path
    metadata_csv_path: Path
    openai_api_key: str
    openai_vision_model: str
    openai_image_model: str
    openai_max_retries: int

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Build configuration from environment variables.

        Parameters:
            None.

        Returns:
            AppConfig: Parsed configuration with sensible defaults.

        Raises:
            ValueError: If required environment variables are missing or invalid.

        Example:
            >>> AppConfig.from_env()
            AppConfig(...)
        """

        # Default paths should remain stable even when commands are launched from a subdirectory.
        project_root = Path(__file__).resolve().parents[2]

        return cls(
            images_dir=Path(os.getenv("VISION_IMAGES_DIR", project_root / "data" / "images")).expanduser(),
            metadata_csv_path=Path(
                os.getenv("VISION_METADATA_CSV", project_root / "data" / "metadata.csv")
            ).expanduser(),
            openai_api_key=_read_required_env("OPENAI_API_KEY"),
            openai_vision_model=os.getenv("OPENAI_VISION_MODEL", "gpt-4.1-mini"),
            openai_image_model=os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1"),
            openai_max_retries=_read_int_env("OPENAI_MAX_RETRIES", 2),
        )

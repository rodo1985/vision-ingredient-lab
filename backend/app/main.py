"""Minimal backend entry point for local configuration validation."""

from __future__ import annotations

from backend.app.config import AppConfig


def build_startup_summary(config: AppConfig) -> str:
    """Create a human-readable startup summary for local development.

    Parameters:
        config: Loaded backend configuration.

    Returns:
        str: Summary of key runtime paths and model settings.

    Raises:
        None.

    Example:
        >>> config = AppConfig(...)
        >>> build_startup_summary(config)
        'Vision Ingredient Lab backend configured...'
    """

    return (
        "Vision Ingredient Lab backend configured with "
        f"images_dir={config.images_dir}, "
        f"metadata_csv_path={config.metadata_csv_path}, "
        f"vision_model={config.openai_vision_model}, "
        f"image_model={config.openai_image_model}."
    )


def main() -> None:
    """Load configuration and print a startup summary.

    Parameters:
        None.

    Returns:
        None.

    Raises:
        ValueError: If required configuration is missing.

    Example:
        >>> main()
    """

    config = AppConfig.from_env()
    print(build_startup_summary(config))


if __name__ == "__main__":
    main()

"""Tests for backend configuration loading."""

from __future__ import annotations

from pathlib import Path

import pytest

from backend.app.config import AppConfig


def test_from_env_reads_required_and_optional_values(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure configuration is assembled from environment variables.

    Parameters:
        monkeypatch: Pytest fixture for environment overrides.

    Returns:
        None.

    Raises:
        None.
    """

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("VISION_IMAGES_DIR", "/tmp/images")
    monkeypatch.setenv("VISION_METADATA_CSV", "/tmp/metadata.csv")
    monkeypatch.setenv("OPENAI_VISION_MODEL", "vision-model")
    monkeypatch.setenv("OPENAI_IMAGE_MODEL", "image-model")
    monkeypatch.setenv("OPENAI_MAX_RETRIES", "4")

    config = AppConfig.from_env()

    assert config.images_dir == Path("/tmp/images")
    assert config.metadata_csv_path == Path("/tmp/metadata.csv")
    assert config.openai_api_key == "test-key"
    assert config.openai_vision_model == "vision-model"
    assert config.openai_image_model == "image-model"
    assert config.openai_max_retries == 4


def test_from_env_requires_openai_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure missing API credentials fail fast with a clear error.

    Parameters:
        monkeypatch: Pytest fixture for environment overrides.

    Returns:
        None.

    Raises:
        None.
    """

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        AppConfig.from_env()


def test_from_env_rejects_invalid_retry_value(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure retry configuration fails fast when not numeric.

    Parameters:
        monkeypatch: Pytest fixture for environment overrides.

    Returns:
        None.

    Raises:
        None.
    """

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_MAX_RETRIES", "not-a-number")

    with pytest.raises(ValueError, match="OPENAI_MAX_RETRIES"):
        AppConfig.from_env()

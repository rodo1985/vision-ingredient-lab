"""Shared dependency helpers for API routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from openai import OpenAI

from backend.app.core.config import Settings, get_settings
from backend.app.services.generation_service import GenerationService
from backend.app.services.metadata_repository import MetadataCSVRepository


def get_app_settings() -> Settings:
    """Return application settings for FastAPI dependency injection.

    Parameters:
        None.

    Returns:
        Settings: Cached application settings instance.

    Raises:
        None.
    """

    return get_settings()


def get_metadata_repository(
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> MetadataCSVRepository:
    """Return the CSV metadata repository used by API routes.

    Parameters:
        settings: Injected application settings.

    Returns:
        MetadataCSVRepository: Repository instance bound to the configured CSV path.

    Raises:
        OSError: If the repository backing file cannot be initialized.
    """

    return MetadataCSVRepository(settings.metadata_csv_path)


def get_openai_client(
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> OpenAI:
    """Return an OpenAI client for API-layer services.

    Parameters:
        settings: Injected application settings.

    Returns:
        OpenAI: Client configured with the project's API key.

    Raises:
        ValueError: If `OPENAI_API_KEY` is not configured.
    """

    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is required for generation requests")
    return OpenAI(api_key=settings.openai_api_key)


def get_generation_service(
    settings: Annotated[Settings, Depends(get_app_settings)],
    client: Annotated[OpenAI, Depends(get_openai_client)],
) -> GenerationService:
    """Return the generation service used by API routes.

    Parameters:
        settings: Injected application settings.
        client: Injected OpenAI client.

    Returns:
        GenerationService: Service configured with the project's image model.

    Raises:
        ValueError: If generation prerequisites are not configured.
    """

    return GenerationService(client=client, image_model=settings.openai_image_model)

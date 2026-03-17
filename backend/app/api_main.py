"""CLI entry point for running the backend API locally."""

from __future__ import annotations

import uvicorn
from openai import OpenAI

from backend.api.app import create_app
from backend.app.config import AppConfig
from backend.clients.image_generation_client import ImageGenerationClient, OpenAIImageService


def build_api_app():
    """Build the FastAPI application with a real OpenAI image generation client.

    Parameters:
        None.

    Returns:
        FastAPI: Configured application ready for local serving.

    Raises:
        ValueError: If required OpenAI configuration is missing.
    """

    config = AppConfig.from_env()
    openai_client = OpenAI(api_key=config.openai_api_key, max_retries=config.openai_max_retries)
    image_client = ImageGenerationClient(
        image_service=OpenAIImageService(client=openai_client, model=config.openai_image_model)
    )
    return create_app(image_client=image_client)


def main() -> None:
    """Run the backend API with a local Uvicorn server.

    Parameters:
        None.

    Returns:
        None.

    Raises:
        RuntimeError: If the ASGI server cannot start.
    """

    uvicorn.run(build_api_app(), host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()

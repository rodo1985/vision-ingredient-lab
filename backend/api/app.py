"""FastAPI application factory for Vision Ingredient Lab."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI

from backend.api.routes.generation import router as generation_router
from backend.api.routes.metadata import create_metadata_router
from backend.metadata_repository import CsvMetadataRepository


def _default_metadata_repository() -> CsvMetadataRepository:
    """Create the default metadata repository without requiring OpenAI credentials.

    Parameters:
        None.

    Returns:
        CsvMetadataRepository: Repository rooted at the configured or default CSV path.

    Raises:
        None.

    Example:
        >>> repository = _default_metadata_repository()
        >>> repository.__class__.__name__
        'CsvMetadataRepository'
    """

    project_root = Path(__file__).resolve().parents[2]
    metadata_csv = Path(
        os.getenv("VISION_METADATA_CSV", project_root / "data" / "metadata.csv")
    ).expanduser()
    return CsvMetadataRepository(metadata_csv)


def create_app(
    image_client: Any | None = None,
    metadata_repository: CsvMetadataRepository | None = None,
) -> FastAPI:
    """Create and configure the FastAPI application instance.

    Parameters:
        image_client: Optional image generation client backing the generation route.
        metadata_repository: Optional repository used by metadata routes.

    Returns:
        FastAPI: Configured FastAPI instance.

    Raises:
        None.

    Example:
        >>> app = create_app()
        >>> app.title
        'Vision Ingredient Lab API'
    """

    app = FastAPI(title="Vision Ingredient Lab API")
    app.state.image_client = image_client
    app.include_router(
        create_metadata_router(metadata_repository or _default_metadata_repository()),
        prefix="/api",
    )
    app.include_router(generation_router, prefix="/api")

    @app.get("/health")
    def healthcheck() -> dict[str, str]:
        """Return a lightweight health response for local development.

        Parameters:
            None.

        Returns:
            dict[str, str]: Health payload indicating the API is responsive.

        Raises:
            None.
        """

        return {"status": "ok"}

    return app


app = create_app()

"""FastAPI application entrypoint for Vision Ingredient Lab."""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from openai import OpenAI

from backend.app.api.routes_generation import generation_router
from backend.app.api.routes_search import search_router
from backend.app.core.config import Settings, get_settings
from backend.app.core.logging import configure_logging, get_logger
from backend.app.services.enrichment_pipeline import MetadataEnrichmentPipeline
from backend.app.services.metadata_repository import MetadataCSVRepository
from backend.app.services.vision_client import VisionClient

logger = get_logger(__name__)


def _run_startup_enrichment(settings: Settings) -> None:
    """Run startup metadata enrichment when configuration is available.

    Parameters:
        settings: Resolved application settings.

    Returns:
        None

    Raises:
        OSError: If the dataset or metadata repository cannot be accessed.
    """

    if not settings.image_dataset_dir.exists():
        logger.info(
            "Skipping startup enrichment because dataset_dir=%s does not exist",
            settings.image_dataset_dir,
        )
        return

    if not settings.openai_api_key:
        logger.info("Skipping startup enrichment because OPENAI_API_KEY is not configured")
        return

    repository = MetadataCSVRepository(settings.metadata_csv_path)
    vision_client = VisionClient(
        client=OpenAI(api_key=settings.openai_api_key),
        vision_model=settings.openai_vision_model,
    )
    pipeline = MetadataEnrichmentPipeline(
        metadata_repository=repository,
        vision_client=vision_client,
    )
    result = pipeline.run(settings.image_dataset_dir)
    logger.info(
        "Startup enrichment finished: discovered=%s new=%s persisted=%s",
        result.discovered_files,
        result.new_files,
        result.persisted_records,
    )


@asynccontextmanager
async def app_lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Configure shared application concerns during startup and shutdown.

    Parameters:
        _: The FastAPI application instance. The current startup path does not
            need direct access to the app object, so the argument is unused.

    Yields:
        AsyncIterator[None]: Control back to FastAPI after startup work completes.

    Example:
        The lifespan hook is registered automatically when the application is created.
    """

    settings = get_settings()
    configure_logging()

    # Logging the resolved paths early makes local debugging easier when the
    # dataset or metadata file lives outside the repository root.
    logger.info(
        "Starting %s in %s mode with dataset_dir=%s metadata_csv=%s",
        settings.app_name,
        settings.app_env,
        settings.image_dataset_dir,
        settings.metadata_csv_path,
    )
    _run_startup_enrichment(settings)
    yield
    logger.info("Shutting down %s", settings.app_name)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance.

    Returns:
        FastAPI: The configured API application.

    Example:
        >>> app = create_app()
        >>> app.title
        'Vision Ingredient Lab API'
    """

    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        lifespan=app_lifespan,
    )
    application.include_router(search_router)
    application.include_router(generation_router)

    @application.get("/health", tags=["health"])
    def healthcheck() -> dict[str, str]:
        """Return a basic readiness signal for local development.

        Returns:
            dict[str, str]: A basic status payload.

        Example:
            >>> healthcheck()
            {'status': 'ok'}
        """

        return {"status": "ok"}

    return application


app = create_app()

"""Application entry point for the FastAPI backend."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from openai import OpenAI

from app.api.routes import create_router
from app.core.config import get_settings
from app.repositories.embedding_store import EmbeddingStore
from app.repositories.metadata_store import MetadataStore
from app.search.embeddings import EmbeddingClient
from app.services.generation import ImageGenerationService
from app.services.metadata_extractor import MetadataExtractor
from app.services.sync_service import SyncService


def create_app() -> FastAPI:
    """Build the FastAPI application and attach routes.

    Returns:
        FastAPI: Configured FastAPI application.
    """

    settings = get_settings()
    # Pass an explicit default URL so blank OPENAI_BASE_URL values in `.env` files
    # cannot degrade into opaque connection failures.
    client = OpenAI(api_key=settings.openai_api_key or None, base_url=settings.resolved_openai_base_url)
    metadata_store = MetadataStore(settings.metadata_csv_path)
    embedding_store = EmbeddingStore(settings.embedding_index_path)
    extractor = MetadataExtractor(client=client, model=settings.vision_model)
    embedder = EmbeddingClient(client=client, model=settings.embedding_model)
    generation_service = ImageGenerationService(
        client=client,
        model=settings.image_generation_model,
        output_dir=settings.generated_output_dir,
    )
    sync_service = SyncService(
        image_root=settings.image_source_dir,
        metadata_store=metadata_store,
        embedding_store=embedding_store,
        extractor=extractor,
        embedder=embedder,
        vision_model=settings.vision_model,
    )
    app = FastAPI(title="Vision Ingredient Lab Backend", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # Source and generated images are returned as `/data/...` URLs, so the backend
    # must expose that directory directly for the frontend to render them.
    app.mount("/data", StaticFiles(directory=settings.project_root / "data"), name="data")
    app.include_router(
        create_router(
            metadata_store=metadata_store,
            embedding_store=embedding_store,
            sync_service=sync_service,
            generation_service=generation_service,
            embed_query=embedder.embed_text,
            enable_startup_sync=settings.enable_startup_sync,
            max_search_results=settings.max_search_results,
            mode="api",
        )
    )

    # The startup sync stays configurable so local dev can opt in without forcing it in production.
    if settings.enable_startup_sync:

        @app.on_event("startup")
        def startup_sync() -> None:
            """Optionally run a sync during application startup.

            Returns:
                None
            """

            sync_service.run()

    return app


app = create_app()

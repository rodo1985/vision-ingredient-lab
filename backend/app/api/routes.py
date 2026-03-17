"""FastAPI route definitions for the backend service."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.models.api import (
    AppConfigResponse,
    GenerateRequest,
    GenerateResponse,
    HealthResponse,
    ImageListResponse,
    ImageRecord,
    SearchResponse,
    SearchResult,
)
from app.models.domain import ImageMetadataRecord
from app.repositories.embedding_store import EmbeddingStore
from app.repositories.metadata_store import MetadataStore
from app.search.hybrid_search import rank_records
from app.services.generation import ImageGenerationService, build_generation_prompt
from app.services.sync_service import SyncService


def build_image_record(record: ImageMetadataRecord) -> ImageRecord:
    """Convert a domain metadata record into an API image record.

    Args:
        record: Domain metadata record.

    Returns:
        ImageRecord: API response model.
    """

    return ImageRecord(
        id=record.image_id,
        filename=record.filename,
        imageUrl=record.file_url,
        description=record.description,
        tags=record.tags,
        lastModified=record.last_modified,
        status=record.status,
    )


def create_router(
    metadata_store: MetadataStore,
    embedding_store: EmbeddingStore,
    sync_service: SyncService,
    generation_service: ImageGenerationService,
    embed_query,
    enable_startup_sync: bool,
    max_search_results: int,
    mode: str,
) -> APIRouter:
    """Create and configure the public API router.

    Args:
        metadata_store: Metadata repository.
        embedding_store: Embedding repository.
        sync_service: Sync orchestrator.
        generation_service: Image generation service.
        embed_query: Callable that embeds search queries.
        enable_startup_sync: Frontend-safe sync flag.
        max_search_results: Maximum search result limit.
        mode: Runtime mode string.

    Returns:
        APIRouter: Configured API router.
    """

    router = APIRouter()

    @router.get("/health", response_model=HealthResponse)
    def get_health() -> HealthResponse:
        """Return basic health information for the backend.

        Returns:
            HealthResponse: Service health payload.
        """

        index_fresh = embedding_store.file_path.exists()
        return HealthResponse(status="ok", indexFresh=index_fresh)

    @router.post("/api/startup/sync")
    def run_sync():
        """Run a metadata and embeddings sync.

        Returns:
            SyncResponse: Sync summary.
        """

        return sync_service.run()

    @router.get("/api/images", response_model=ImageListResponse)
    def list_images(
        limit: int = Query(default=50, ge=1, le=200),
        offset: int = Query(default=0, ge=0),
    ) -> ImageListResponse:
        """List image records with simple pagination.

        Args:
            limit: Maximum number of records to return.
            offset: Pagination offset.

        Returns:
            ImageListResponse: Paginated image records.
        """

        records = metadata_store.load_all()
        page = records[offset : offset + limit]
        return ImageListResponse(items=[build_image_record(record) for record in page], total=len(records))

    @router.get("/api/images/{image_id}", response_model=ImageRecord)
    def get_image(image_id: str) -> ImageRecord:
        """Fetch one image record by id.

        Args:
            image_id: Stable image identifier.

        Returns:
            ImageRecord: Matching image record.

        Raises:
            HTTPException: Raised when the image does not exist.
        """

        record = metadata_store.get_by_id(image_id)
        if record is None:
            raise HTTPException(status_code=404, detail={"error": {"code": "not_found", "message": "Image not found."}})
        return build_image_record(record)

    @router.get("/api/search", response_model=SearchResponse)
    def search_images(q: str = Query(default=""), limit: int = Query(default=20, ge=1, le=100)) -> SearchResponse:
        """Search indexed image metadata.

        Args:
            q: Raw search query.
            limit: Maximum number of matches to return.

        Returns:
            SearchResponse: Ranked search results.
        """

        records = metadata_store.load_all()
        embedding_records = embedding_store.load_all()
        query_vector = embed_query(q) if q.strip() else []
        ranked = rank_records(q, query_vector, records, embedding_records, limit=min(limit, max_search_results))
        items = [
            SearchResult(
                image=build_image_record(match.image),
                score=match.score,
                matchReasons=match.match_reasons,
                matchedTags=match.matched_tags,
            )
            for match in ranked
        ]
        return SearchResponse(query=q, items=items)

    @router.post("/api/generate", response_model=GenerateResponse)
    def generate_image(request: GenerateRequest) -> GenerateResponse:
        """Generate a creative image from selected ingredient ids.

        Args:
            request: Validated generation request.

        Returns:
            GenerateResponse: Generated image payload.

        Raises:
            HTTPException: Raised when one or more ingredient ids are missing.
        """

        selected_records = []
        for image_id in request.ingredientIds:
            record = metadata_store.get_by_id(image_id)
            if record is None:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": {
                            "code": "not_found",
                            "message": "One or more ingredient ids were not found.",
                            "details": {"imageId": image_id},
                        }
                    },
                )
            selected_records.append(record)
        prompt = build_generation_prompt(selected_records, request.creativeDirection)
        generation_id, image_url, created_at = generation_service.generate(prompt)
        return GenerateResponse(
            generationId=generation_id,
            imageUrl=image_url,
            prompt=prompt,
            ingredientIds=request.ingredientIds,
            createdAt=created_at,
        )

    @router.get("/api/config", response_model=AppConfigResponse)
    def get_config() -> AppConfigResponse:
        """Return frontend-safe runtime config values.

        Returns:
            AppConfigResponse: Configuration payload.
        """

        return AppConfigResponse(
            mode=mode,
            enableStartupSync=enable_startup_sync,
            maxSearchResults=max_search_results,
        )

    return router

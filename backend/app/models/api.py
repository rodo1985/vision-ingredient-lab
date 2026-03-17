"""Public API schemas for FastAPI routes."""

from datetime import datetime

from pydantic import BaseModel, Field


class ImageRecord(BaseModel):
    """Define the frontend-facing image shape.

    Returns:
        ImageRecord: Serialized image record for the API.
    """

    id: str
    filename: str
    imageUrl: str
    description: str
    tags: list[str]
    lastModified: datetime
    status: str


class SearchResult(BaseModel):
    """Define one search result payload item.

    Returns:
        SearchResult: Search result for the frontend.
    """

    image: ImageRecord
    score: float
    matchReasons: list[str]
    matchedTags: list[str]


class SearchResponse(BaseModel):
    """Define the search response envelope.

    Returns:
        SearchResponse: Search response for the API.
    """

    query: str
    items: list[SearchResult]


class ImageListResponse(BaseModel):
    """Define a paginated image list payload.

    Returns:
        ImageListResponse: Image list response.
    """

    items: list[ImageRecord]
    total: int


class SyncResponse(BaseModel):
    """Define the sync response payload.

    Returns:
        SyncResponse: Sync status response.
    """

    scannedCount: int
    newCount: int
    updatedCount: int
    failedCount: int
    startedAt: datetime
    completedAt: datetime


class GenerateRequest(BaseModel):
    """Define the image generation request body.

    Returns:
        GenerateRequest: Validated generation request.
    """

    ingredientIds: list[str] = Field(min_length=1)
    creativeDirection: str | None = None


class GenerateResponse(BaseModel):
    """Define the image generation response body.

    Returns:
        GenerateResponse: Generation response payload.
    """

    generationId: str
    imageUrl: str
    prompt: str
    ingredientIds: list[str]
    createdAt: datetime


class AppConfigResponse(BaseModel):
    """Define the frontend-safe config response.

    Returns:
        AppConfigResponse: Configuration response payload.
    """

    mode: str
    enableStartupSync: bool
    maxSearchResults: int


class HealthResponse(BaseModel):
    """Define the health check response body.

    Returns:
        HealthResponse: Health response payload.
    """

    status: str
    indexFresh: bool

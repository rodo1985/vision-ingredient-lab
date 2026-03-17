"""Search and metadata listing API endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from backend.app.api.dependencies import get_metadata_repository
from backend.app.api.schemas import MetadataResponse
from backend.app.services.metadata_repository import MetadataCSVRepository
from backend.app.services.search_service import search_metadata

search_router = APIRouter(prefix="/api", tags=["search"])


@search_router.get("/search/health")
def search_health() -> dict[str, str]:
    """Return a simple status response for the search API slice.

    Parameters:
        None.

    Returns:
        dict[str, str]: A small status payload that confirms the search router is mounted.

    Raises:
        None.

    Example:
        >>> search_health()
        {'status': 'ok'}
    """

    return {"status": "ok"}


@search_router.get("/images", response_model=list[MetadataResponse], summary="List stored metadata")
def list_metadata(
    repository: Annotated[MetadataCSVRepository, Depends(get_metadata_repository)],
    max_results: Annotated[
        int | None,
        Query(ge=1, description="Optional limit on the number of returned metadata rows."),
    ] = None,
) -> list[MetadataResponse]:
    """Return stored metadata rows from the CSV repository.

    Parameters:
        repository: Injected metadata repository instance.
        max_results: Optional maximum number of rows to return.

    Returns:
        list[MetadataResponse]: Serialized metadata rows in repository order.

    Raises:
        OSError: If the repository cannot be read.
    """

    records = repository.load_all()
    if max_results is not None:
        records = records[:max_results]
    return [MetadataResponse.from_record(record) for record in records]


@search_router.get("/search", response_model=list[MetadataResponse], summary="Search metadata")
def search_metadata_endpoint(
    repository: Annotated[MetadataCSVRepository, Depends(get_metadata_repository)],
    query: Annotated[str | None, Query(description="Ingredient term to search for.")] = None,
    max_results: Annotated[
        int | None,
        Query(ge=1, description="Optional limit on the number of returned metadata rows."),
    ] = None,
) -> list[MetadataResponse]:
    """Return metadata rows matching the provided query text.

    Parameters:
        repository: Injected metadata repository instance.
        query: Search query supplied by the client.
        max_results: Optional maximum number of rows to return.

    Returns:
        list[MetadataResponse]: Matching metadata rows sorted by search relevance.

    Raises:
        OSError: If the repository cannot be read.
    """

    records = repository.load_all()
    matches = search_metadata(records, query=query, max_results=max_results)
    return [MetadataResponse.from_record(record) for record in matches]

"""Metadata-related API routes and helpers."""

from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, HTTPException, Query

from backend.metadata_repository import CsvMetadataRepository
from backend.search.service import search_metadata


def create_metadata_router(
    repository: CsvMetadataRepository,
) -> APIRouter:
    """Build an APIRouter exposing metadata listing and search endpoints.

    Parameters:
        repository: CSV repository used to load metadata rows.

    Returns:
        APIRouter: Router that can be mounted onto a FastAPI application.

    Raises:
        None.
    """

    router = APIRouter(prefix="/metadata", tags=["metadata"])

    @router.get("/")
    def list_metadata() -> list[dict]:
        """Return all persisted metadata rows.

        Returns:
            list[dict]: All metadata rows serialized as dictionaries.

        Raises:
            None.
        """

        rows = repository.read_all()
        return [asdict(row) for row in rows]

    @router.get("/search")
    def search_metadata_endpoint(q: str = Query(..., min_length=1)) -> list[dict]:
        """Return metadata rows matching the provided query.

        Parameters:
            q: Query term to match against keywords or description.

        Returns:
            list[dict]: Matching metadata rows sorted by relevance.

        Raises:
            HTTPException: When the query is empty or invalid.
        """

        try:
            matches = search_metadata(repository, q)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return [asdict(row) for row in matches]

    return router

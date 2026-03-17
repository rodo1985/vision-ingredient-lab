"""Search API endpoints."""

from fastapi import APIRouter

search_router = APIRouter(prefix="/api", tags=["search"])


@search_router.get("/search/health")
def search_health() -> dict[str, str]:
    """Return a simple status response for the search API slice.

    Returns:
        dict[str, str]: A small status payload that confirms the search router is mounted.

    Example:
        >>> search_health()
        {'status': 'ok'}
    """

    return {"status": "ok"}

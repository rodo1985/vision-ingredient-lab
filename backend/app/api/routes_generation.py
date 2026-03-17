"""Generation API endpoints."""

from fastapi import APIRouter

generation_router = APIRouter(prefix="/api", tags=["generation"])


@generation_router.get("/generate/health")
def generation_health() -> dict[str, str]:
    """Return a simple status response for the generation API slice.

    Returns:
        dict[str, str]: A small status payload that confirms the generation router is mounted.

    Example:
        >>> generation_health()
        {'status': 'ok'}
    """

    return {"status": "ok"}

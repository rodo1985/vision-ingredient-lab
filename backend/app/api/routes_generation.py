"""Generation API endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.api.dependencies import get_generation_service
from backend.app.api.schemas import GenerationRequest, GenerationResponse
from backend.app.services.generation_service import GenerationService

generation_router = APIRouter(prefix="/api", tags=["generation"])


@generation_router.get("/generate/health")
def generation_health() -> dict[str, str]:
    """Return a simple status response for the generation API slice.

    Parameters:
        None.

    Returns:
        dict[str, str]: A small status payload that confirms the generation router is mounted.

    Raises:
        None.

    Example:
        >>> generation_health()
        {'status': 'ok'}
    """

    return {"status": "ok"}


@generation_router.post(
    "/generate",
    response_model=GenerationResponse,
    summary="Generate a creative image from selected ingredients",
)
def generate_image(
    payload: GenerationRequest,
    generation_service: Annotated[GenerationService, Depends(get_generation_service)],
) -> GenerationResponse:
    """Generate an image from the submitted ingredient selection.

    Parameters:
        payload: Validated generation request body.
        generation_service: Injected service that wraps the OpenAI image API.

    Returns:
        GenerationResponse: Prompt and generated image payload metadata.

    Raises:
        HTTPException: If request validation or generation fails.
    """

    try:
        result = generation_service.generate(
            payload.selected_ingredients,
            base_style=payload.base_style,
            creativity=payload.creativity,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    return GenerationResponse(
        prompt=result.prompt,
        image_base64=result.image_base64,
        image_url=result.image_url,
        revised_prompt=result.revised_prompt,
        model=result.model,
    )

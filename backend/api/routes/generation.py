"""Image generation route for Vision Ingredient Lab."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from backend.app.prompt_builder import build_default_prompt
from backend.clients.image_generation_client import ImageGenerationClient

router = APIRouter()


class GenerationRequest(BaseModel):
    """Request payload used to trigger creative image generation.

    Parameters:
        ingredients: Selected ingredient names that should shape the prompt.
        size: Optional image size override for the generation call.

    Returns:
        GenerationRequest: Validated request body for the endpoint.

    Raises:
        None.
    """

    ingredients: list[str] = Field(..., min_length=2)
    size: str | None = None


class GenerationResponse(BaseModel):
    """Response payload returned after generation completes.

    Parameters:
        prompt: Prompt sent to the image generation client.
        image_url: URL or data URI for the generated image.
        metadata: Additional metadata returned by the generation client.

    Returns:
        GenerationResponse: Serialized success payload for the endpoint.

    Raises:
        None.
    """

    prompt: str
    image_url: str
    metadata: dict[str, Any]


def _get_image_client(request: Request) -> ImageGenerationClient:
    """Retrieve the configured image generation client from the FastAPI app state.

    Parameters:
        request: Incoming FastAPI request with application state access.

    Returns:
        ImageGenerationClient: Configured client stored on the application state.

    Raises:
        HTTPException: If the application has no configured image client.
    """

    client = getattr(request.app.state, "image_client", None)
    if client is None:
        raise HTTPException(status_code=503, detail="Image generation client is unavailable.")
    return client


@router.post("/generation", response_model=GenerationResponse)
def generate_image_route(
    request: GenerationRequest,
    image_client: Annotated[ImageGenerationClient, Depends(_get_image_client)],
) -> GenerationResponse:
    """Generate an image for the provided ingredients and return the result.

    Parameters:
        request: Request body containing the selected ingredients and optional size.
        image_client: Injected image generation client.

    Returns:
        GenerationResponse: Prompt, image URL, and auxiliary generation metadata.

    Raises:
        HTTPException: If prompt construction or image generation fails.
    """

    try:
        prompt = build_default_prompt(request.ingredients)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    try:
        result = image_client.generate_image(prompt, size=request.size)
    except ValueError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error

    return GenerationResponse(
        prompt=result.prompt,
        image_url=result.image_url,
        metadata={
            "description": result.metadata.get("description"),
            "keywords": result.metadata.get("keywords"),
        },
    )

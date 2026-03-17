"""Client wrapper for creative image generation services."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol

from openai import OpenAI


class ImageService(Protocol):
    """Describe the external image generation callable used by the client.

    Parameters:
        None.

    Returns:
        ImageService: Static typing protocol for image services.

    Raises:
        None.
    """

    def generate(self, prompt: str, size: str | None = None) -> Mapping[str, Any]:
        """Generate an image for the provided prompt."""


@dataclass(slots=True)
class OpenAIImageService:
    """Wrap the OpenAI SDK image generation surface behind the `ImageService` protocol.

    Parameters:
        client: OpenAI SDK client instance.
        model: Image generation model name to call.

    Returns:
        OpenAIImageService: Adapter compatible with `ImageGenerationClient`.

    Raises:
        None.
    """

    client: OpenAI
    model: str

    def generate(self, prompt: str, size: str | None = None) -> Mapping[str, Any]:
        """Generate an image using the configured OpenAI client and model.

        Parameters:
            prompt: Prompt string used for image generation.
            size: Optional image size forwarded to the OpenAI API.

        Returns:
            Mapping[str, Any]: Normalized mapping with a `data` list for the wrapper client.

        Raises:
            ValueError: If the OpenAI response does not include image data.
        """

        response = self.client.images.generate(
            model=self.model,
            prompt=prompt,
            size=size,
        )

        entries: list[dict[str, Any]] = []
        for item in getattr(response, "data", []):
            image_url = getattr(item, "url", None)
            b64_json = getattr(item, "b64_json", None)
            if image_url is None and b64_json is None:
                continue
            entries.append({"url": image_url or f"data:image/png;base64,{b64_json}"})

        if not entries:
            raise ValueError("Image service returned an invalid payload.")

        return {"data": entries}


@dataclass(frozen=True, slots=True)
class ImageGenerationResult:
    """Normalized result returned by the image generation client.

    Parameters:
        prompt: Prompt that was sent to the image generation service.
        image_url: URL or identifier of the generated image.
        metadata: Additional data returned by the service.

    Returns:
        ImageGenerationResult: Normalized payload returned to API handlers.

    Raises:
        None.
    """

    prompt: str
    image_url: str
    metadata: Mapping[str, Any]


class ImageGenerationClient:
    """Delegate image generation to an injected service and normalize the response.

    Parameters:
        image_service: Concrete image generation service implementation.
        default_size: Optional default canvas size passed to the service.

    Returns:
        ImageGenerationClient: Testable adapter for route handlers and workflows.

    Raises:
        None.
    """

    def __init__(self, image_service: ImageService, default_size: str | None = None) -> None:
        """Initialize the client with a concrete image service implementation.

        Parameters:
            image_service: Callable implementing the image generation surface.
            default_size: Optional canvas size parameter forwarded to the service.

        Returns:
            None.

        Raises:
            None.
        """

        self._image_service = image_service
        self._default_size = default_size or "1024x1024"

    def generate_image(self, prompt: str, size: str | None = None) -> ImageGenerationResult:
        """Generate an image from the provided prompt.

        Parameters:
            prompt: Prompt string crafted by the prompt builder.
            size: Optional canvas size override for this request.

        Returns:
            ImageGenerationResult: Structured result containing the image URL and metadata.

        Raises:
            ValueError: If the image service returns an unexpected payload.
        """

        response = self._image_service.generate(prompt=prompt, size=size or self._default_size)
        data = response.get("data")
        if not data or not isinstance(data, list) or not data[0]:
            raise ValueError("Image service returned an invalid payload.")

        entry = data[0]
        image_url = entry.get("url") or entry.get("image_url")
        if not isinstance(image_url, str):
            raise ValueError("Image service response missing image URL.")

        metadata = {"description": entry.get("description"), "keywords": entry.get("keywords")}
        return ImageGenerationResult(prompt=prompt, image_url=image_url, metadata=metadata)

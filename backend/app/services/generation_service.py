"""Image generation service that wraps OpenAI image generation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from openai import OpenAI

from backend.app.services.prompt_builder import PromptBuilderConfig, build_prompt


@dataclass(frozen=True)
class GenerationResult:
    """Represent the output of a creative image generation request.

    Parameters:
        prompt: Final prompt sent to the OpenAI image model.
        image_base64: Base64-encoded image payload when returned by the provider.
        image_url: Remote image URL when returned by the provider.
        revised_prompt: Provider-adjusted prompt when available.
        model: Model identifier used for the generation request.

    Returns:
        GenerationResult: Immutable generation payload.

    Raises:
        None.
    """

    prompt: str
    image_base64: str | None
    image_url: str | None
    revised_prompt: str | None
    model: str


class GenerationService:
    """Generate creative images from selected ingredient terms.

    Parameters:
        client: OpenAI client instance used for image generation.
        image_model: Image generation model identifier.

    Returns:
        GenerationService: Reusable generation service instance.

    Raises:
        None.
    """

    def __init__(self, client: OpenAI, image_model: str = "gpt-image-1") -> None:
        """Initialize the generation service.

        Parameters:
            client: OpenAI client instance.
            image_model: OpenAI image model used for generation.

        Returns:
            None

        Raises:
            None.
        """

        self._client = client
        self._image_model = image_model

    def generate(
        self,
        selected_ingredients: Iterable[str],
        *,
        base_style: str = "dramatic food photography",
        creativity: float = 0.65,
    ) -> GenerationResult:
        """Generate an image from a selected ingredient list.

        Parameters:
            selected_ingredients: Ingredient terms selected by the user.
            base_style: Visual style instruction used for prompt composition.
            creativity: Creativity scalar between 0 and 1 for prompt composition.

        Returns:
            GenerationResult: Parsed generation response from OpenAI.

        Raises:
            ValueError: If prompt validation fails or the provider response has no image.
        """

        prompt = build_prompt(
            selected_ingredients,
            PromptBuilderConfig(base_style=base_style, creativity=creativity),
        )
        response = self._client.images.generate(
            model=self._image_model,
            prompt=prompt,
        )
        return self._parse_response(response, prompt)

    def _parse_response(self, response: Any, prompt: str) -> GenerationResult:
        """Parse an OpenAI image-generation response into a stable result object.

        Parameters:
            response: Raw response object returned by the OpenAI SDK.
            prompt: Prompt originally sent to the provider.

        Returns:
            GenerationResult: Parsed generation payload.

        Raises:
            ValueError: If the provider returns no image payload.
        """

        data = getattr(response, "data", None)
        if isinstance(response, dict):
            data = response.get("data", data)

        first_image = data[0] if isinstance(data, list) and data else None
        if first_image is None:
            raise ValueError("image generation response did not contain any image data")

        image_base64 = self._read_attribute(first_image, "b64_json")
        image_url = self._read_attribute(first_image, "url")
        revised_prompt = self._read_attribute(first_image, "revised_prompt")
        if not image_base64 and not image_url:
            raise ValueError("image generation response did not contain an image payload")

        return GenerationResult(
            prompt=prompt,
            image_base64=image_base64,
            image_url=image_url,
            revised_prompt=revised_prompt,
            model=self._image_model,
        )

    @staticmethod
    def _read_attribute(item: Any, attribute_name: str) -> str | None:
        """Read a named attribute from either an SDK object or plain dictionary.

        Parameters:
            item: Raw provider item returned inside the image response.
            attribute_name: Name of the field to extract.

        Returns:
            str | None: Extracted string value when present.

        Raises:
            None.
        """

        if isinstance(item, dict):
            value = item.get(attribute_name)
        else:
            value = getattr(item, attribute_name, None)
        return value if isinstance(value, str) else None

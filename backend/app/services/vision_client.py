"""Vision metadata enrichment client backed by OpenAI vision models."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

from openai import OpenAI


@dataclass(frozen=True)
class VisionMetadata:
    """Structured metadata produced for a single ingredient image.

    Attributes:
        description: Human-facing explanation of the ingredient image.
        keywords: Normalized keywords extracted from the response.
        source_path: Local path that was described.

    Example:
        >>> VisionMetadata("fresh basil", ("basil",), Path("basil.jpg"))
    """

    description: str
    keywords: tuple[str, ...]
    source_path: Path


class VisionClient:
    """Wrap OpenAI vision-enabled responses for ingredient metadata extraction.

    Parameters:
        client: Authenticated OpenAI client instance.
        vision_model: Model name used for vision analysis requests.
        prompt: Prompt instructing the model how to describe the image.

    Returns:
        VisionClient: Reusable service instance for image description requests.

    Raises:
        None.
    """

    def __init__(
        self,
        client: OpenAI,
        vision_model: str = "gpt-4.1-mini",
        prompt: str = "Describe the food ingredients in this image and list keywords.",
    ) -> None:
        """Create a vision client.

        Parameters:
            client: Authenticated OpenAI client instance.
            vision_model: Model name to use for the vision request.
            prompt: Text prompt instructing the vision model what to return.

        Returns:
            None

        Raises:
            None.
        """

        self._client = client
        self._model = vision_model
        self._prompt = prompt

    def describe_image(self, image_path: Path) -> VisionMetadata:
        """Query OpenAI for structured metadata about an image file.

        Parameters:
            image_path: Path to the local image file to analyze.

        Returns:
            VisionMetadata: Parsed metadata for downstream pipelines.

        Raises:
            FileNotFoundError: If the provided path does not exist.

        Example:
            >>> client.describe_image(Path("ingredients/tomato.jpg"))
        """

        path = image_path.expanduser()
        if not path.exists():
            raise FileNotFoundError(f"{path} does not exist")

        response = self._client.responses.create(
            model=self._model,
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": self._prompt},
                        {"type": "input_image", "image_url": f"file://{path.absolute()}"},
                    ],
                }
            ],
        )

        return self._parse_response(response, path)

    def _parse_response(self, response: Any, source_path: Path) -> VisionMetadata:
        """Convert a raw OpenAI response into VisionMetadata.

        Parameters:
            response: Raw response object returned by OpenAI.
            source_path: Image path that was described.

        Returns:
            VisionMetadata: Metadata derived from the response.

        Raises:
            ValueError: If the response payload cannot be normalized.
        """
        output = getattr(response, "output", None)
        metadata = getattr(response, "metadata", None)
        if isinstance(response, dict):
            output = response.get("output", output)
            metadata = response.get("metadata", metadata)

        normalized_output = output if isinstance(output, Sequence) else []
        normalized_metadata = metadata if isinstance(metadata, dict) else {}

        description = self._extract_description(normalized_output)
        keywords = self._extract_keywords(normalized_metadata, description)

        return VisionMetadata(description=description, keywords=keywords, source_path=source_path)

    @staticmethod
    def _extract_description(output: Sequence[Any]) -> str:
        """Concatenate response output fragments into a single description string.

        Parameters:
            output: OpenAI output fragments or content blocks.

        Returns:
            str: Combined description text.

        Raises:
            None.
        """

        fragments: list[str] = []

        for entry in output:
            if isinstance(entry, str):
                fragment = entry.strip()
            elif isinstance(entry, dict):
                fragment = (
                    entry.get("text")
                    or entry.get("content")
                    or entry.get("message")
                    or ""
                )
            else:
                fragment = ""

            if fragment:
                fragments.append(fragment.strip())

        return " ".join(fragments).strip() or "No description provided."

    @staticmethod
    def _extract_keywords(metadata: dict[str, Any], fallback_description: str) -> tuple[str, ...]:
        """Derive a tuple of keywords from metadata or fallback text.

        Parameters:
            metadata: Response metadata dictionary that may include keywords.
            fallback_description: Description used when structured keywords are unavailable.

        Returns:
            tuple[str, ...]: Normalized keyword tuple in stable order.

        Raises:
            None.
        """

        raw_keywords = metadata.get("keywords")
        if isinstance(raw_keywords, Iterable) and not isinstance(raw_keywords, (str, bytes, dict)):
            parsed = tuple(
                term.strip().lower()
                for term in raw_keywords
                if isinstance(term, str) and term.strip()
            )
            if parsed:
                return tuple(dict.fromkeys(parsed))

        # fallback heuristic splits the description on commas and spaces.
        fallback_terms = (
            term.strip().lower()
            for term in fallback_description.replace(".", "").split(",")
        )
        return tuple(dict.fromkeys(term for term in fallback_terms if term))

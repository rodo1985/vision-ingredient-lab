"""OpenAI-backed image metadata extraction helpers."""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from pathlib import Path

from openai import OpenAI


@dataclass(slots=True)
class ExtractedMetadata:
    """Represent parsed metadata from an image analysis response.

    Args:
        description: Generated image description.
        tags: Normalized ingredient tags.

    Returns:
        ExtractedMetadata: Parsed metadata values.
    """

    description: str
    tags: list[str]


class MetadataExtractor:
    """Wrap OpenAI Responses calls for image metadata extraction.

    Args:
        client: OpenAI client instance.
        model: Vision-capable model name.

    Returns:
        MetadataExtractor: Configured extractor instance.
    """

    def __init__(self, client: OpenAI, model: str) -> None:
        """Initialize the extractor.

        Args:
            client: OpenAI client instance.
            model: Vision-capable model name.

        Returns:
            None
        """

        self.client = client
        self.model = model

    def extract(self, image_path: Path) -> ExtractedMetadata:
        """Analyze an image and return normalized metadata.

        Args:
            image_path: Path to the source image.

        Returns:
            ExtractedMetadata: Parsed description and tags.

        Raises:
            ValueError: Raised when the model response is not valid JSON.
        """

        # The response is requested as strict JSON so downstream services can stay simple.
        response = self.client.responses.create(
            model=self.model,
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "Analyze this ingredient image and return strict JSON with keys "
                                "`description` and `tags`. Keep the description short and the tags "
                                "normalized, lowercase, and ingredient-focused."
                            ),
                        },
                        {"type": "input_image", "image_url": encode_image_as_data_url(image_path)},
                    ],
                }
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "ingredient_image_metadata",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "description": {"type": "string"},
                            "tags": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["description", "tags"],
                        "additionalProperties": False,
                    },
                }
            },
        )
        payload = response.output_text
        return parse_extracted_metadata(payload)


def encode_image_as_data_url(image_path: Path) -> str:
    """Encode a local image file as a Base64 data URL for the Responses API.

    Args:
        image_path: Path to the source image file.

    Returns:
        str: Base64-encoded data URL.
    """

    mime_type = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }.get(image_path.suffix.lower(), "application/octet-stream")
    encoded_bytes = base64.b64encode(image_path.read_bytes()).decode("utf-8")
    return f"data:{mime_type};base64,{encoded_bytes}"


def parse_extracted_metadata(payload: str) -> ExtractedMetadata:
    """Parse strict JSON returned by the metadata model.

    Args:
        payload: JSON string returned by the OpenAI response.

    Returns:
        ExtractedMetadata: Parsed metadata values.

    Raises:
        ValueError: Raised when required fields are missing or invalid.
    """

    data = json.loads(payload)
    description = str(data["description"]).strip()
    raw_tags = data["tags"]
    tags = sorted({str(tag).strip().lower() for tag in raw_tags if str(tag).strip()})
    if not description:
        raise ValueError("Metadata extraction returned an empty description.")
    return ExtractedMetadata(description=description, tags=tags)

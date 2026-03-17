"""Pydantic schemas for REST API request and response payloads."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from backend.app.models.metadata import MetadataRecord


class MetadataResponse(BaseModel):
    """Represent a metadata record returned through the API.

    Parameters:
        filename: Image file name including the extension.
        filepath: File path associated with the metadata row.
        description: AI-generated description of the image.
        keywords: Ingredient keywords associated with the image.
        processed_at: Timestamp for when the image was processed.
        last_modified: Timestamp for when the source image last changed.

    Returns:
        MetadataResponse: Serializable API model.

    Raises:
        None.
    """

    filename: str
    filepath: str
    description: str
    keywords: list[str]
    processed_at: datetime
    last_modified: datetime

    @classmethod
    def from_record(cls, record: MetadataRecord) -> "MetadataResponse":
        """Convert a domain metadata record into an API response object.

        Parameters:
            record: Domain record loaded from the metadata repository.

        Returns:
            MetadataResponse: API-facing representation of the record.

        Raises:
            None.
        """

        return cls(
            filename=record.filename,
            filepath=record.filepath,
            description=record.description,
            keywords=record.keywords,
            processed_at=record.processed_at,
            last_modified=record.last_modified,
        )


class GenerationRequest(BaseModel):
    """Represent a generation request submitted by the frontend.

    Parameters:
        selected_ingredients: Ingredient terms selected by the user.
        base_style: Optional high-level style instruction for prompt generation.
        creativity: Optional creativity scalar between 0 and 1.

    Returns:
        GenerationRequest: Validated generation payload.

    Raises:
        None.
    """

    selected_ingredients: list[str] = Field(min_length=2)
    base_style: str = "dramatic food photography"
    creativity: float = Field(default=0.65, ge=0.0, le=1.0)


class GenerationResponse(BaseModel):
    """Represent the result of an image generation request.

    Parameters:
        prompt: Final prompt sent to the model.
        image_base64: Base64-encoded generated image payload when available.
        revised_prompt: Optional provider-revised prompt returned by the model.
        image_url: URL for the generated image when the provider returns a URL.
        model: OpenAI model used for the generation request.

    Returns:
        GenerationResponse: Serializable generation response object.

    Raises:
        None.
    """

    prompt: str
    image_base64: str | None = None
    image_url: str | None = None
    revised_prompt: str | None = None
    model: str

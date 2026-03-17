"""Domain models used throughout the backend."""

from datetime import datetime

from pydantic import BaseModel, Field


class ImageMetadataRecord(BaseModel):
    """Represent one canonical metadata row for an image.

    Args:
        image_id: Stable image identifier.
        filename: Original image filename.
        filepath: Absolute file path.
        file_url: URL or relative path exposed to clients.
        mime_type: MIME type for the file.
        description: Generated description text.
        tags: Normalized ingredient tags.
        search_text: Combined searchable text.
        processed_at: Processing timestamp.
        last_modified: Source file modification timestamp.
        embedding_version: Version of the embedding derivation scheme.
        model_version: Version or name of the vision model used.
        status: Current record status.
        error_message: Optional failure information.

    Returns:
        ImageMetadataRecord: Validated metadata record.
    """

    image_id: str
    filename: str
    filepath: str
    file_url: str
    mime_type: str
    description: str
    tags: list[str] = Field(default_factory=list)
    search_text: str
    processed_at: datetime
    last_modified: datetime
    embedding_version: str
    model_version: str
    status: str
    error_message: str = ""


class EmbeddingRecord(BaseModel):
    """Represent one derived embedding row.

    Args:
        image_id: Stable image identifier.
        vector: Embedding vector values.
        embedding_version: Version of the embedding schema.
        updated_at: Write timestamp.

    Returns:
        EmbeddingRecord: Validated embedding record.
    """

    image_id: str
    vector: list[float]
    embedding_version: str
    updated_at: datetime


class SearchMatch(BaseModel):
    """Represent a ranked hybrid search match.

    Args:
        image: Matched image metadata.
        score: Combined relevance score.
        match_reasons: Human-readable match reasons.
        matched_tags: Exact matched tags.

    Returns:
        SearchMatch: A ranked result for the API layer.
    """

    image: ImageMetadataRecord
    score: float
    match_reasons: list[str]
    matched_tags: list[str]

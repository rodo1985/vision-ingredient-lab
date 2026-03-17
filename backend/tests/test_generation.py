"""Unit tests for prompt building and generation behavior."""

from datetime import UTC, datetime

from app.models.domain import ImageMetadataRecord
from app.services.generation import build_generation_prompt


def build_record(image_id: str, tag: str) -> ImageMetadataRecord:
    """Build a metadata record for generation tests.

    Args:
        image_id: Stable image identifier.
        tag: Primary tag value.

    Returns:
        ImageMetadataRecord: Metadata record for testing.
    """

    return ImageMetadataRecord(
        image_id=image_id,
        filename=f"{image_id}.jpg",
        filepath=f"/tmp/{image_id}.jpg",
        file_url=f"/data/images/{image_id}.jpg",
        mime_type="image/jpeg",
        description=f"{tag} ingredient",
        tags=[tag],
        search_text=tag,
        processed_at=datetime.now(tz=UTC),
        last_modified=datetime.now(tz=UTC),
        embedding_version="v1",
        model_version="vision-test",
        status="ready",
        error_message="",
    )


def test_build_generation_prompt_uses_selected_ingredients():
    """Prompt builder should mention selected ingredients and creative direction."""

    prompt = build_generation_prompt(
        [build_record("img_tomato", "tomato"), build_record("img_basil", "basil")],
        "Plate them like a pizza concept",
    )
    assert "tomato, basil" in prompt
    assert "pizza concept" in prompt

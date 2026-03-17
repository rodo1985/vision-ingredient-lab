"""Unit tests for hybrid ranking behavior."""

from datetime import UTC, datetime

from app.models.domain import EmbeddingRecord, ImageMetadataRecord
from app.search.hybrid_search import rank_records


def build_image(image_id: str, description: str, tags: list[str]) -> ImageMetadataRecord:
    """Build a metadata record for search tests.

    Args:
        image_id: Stable image identifier.
        description: Description text.
        tags: Tag list.

    Returns:
        ImageMetadataRecord: Metadata record for testing.
    """

    return ImageMetadataRecord(
        image_id=image_id,
        filename=f"{image_id}.jpg",
        filepath=f"/tmp/{image_id}.jpg",
        file_url=f"/data/images/{image_id}.jpg",
        mime_type="image/jpeg",
        description=description,
        tags=tags,
        search_text=f"{description} {' '.join(tags)}",
        processed_at=datetime.now(tz=UTC),
        last_modified=datetime.now(tz=UTC),
        embedding_version="v1",
        model_version="vision-test",
        status="ready",
        error_message="",
    )


def test_exact_tag_hits_rank_above_weak_semantic_matches():
    """Keyword-heavy matches should outrank weaker semantic-only results."""

    exact = build_image("img_tomato", "A ripe tomato ingredient photo.", ["tomato"])
    semantic = build_image("img_sauce", "A savory dish image.", ["sauce"])
    embeddings = [
        EmbeddingRecord(image_id="img_tomato", vector=[0.1, 0.1], embedding_version="v1", updated_at=datetime.now(tz=UTC)),
        EmbeddingRecord(image_id="img_sauce", vector=[0.8, 0.2], embedding_version="v1", updated_at=datetime.now(tz=UTC)),
    ]
    ranked = rank_records("tomato", [1.0, 0.0], [exact, semantic], embeddings)
    assert ranked[0].image.image_id == "img_tomato"


def test_semantic_search_can_return_relevant_results_without_keyword_overlap():
    """Semantic similarity should still surface results when keywords do not overlap."""

    record = build_image("img_pizza", "A baked Italian flatbread with melted cheese.", ["cheese", "baked"])
    embeddings = [
        EmbeddingRecord(image_id="img_pizza", vector=[1.0, 0.0], embedding_version="v1", updated_at=datetime.now(tz=UTC))
    ]
    ranked = rank_records("pizza", [1.0, 0.0], [record], embeddings)
    assert ranked[0].match_reasons == ["semantic"]

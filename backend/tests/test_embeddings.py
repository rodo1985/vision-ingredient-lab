"""Unit tests for embedding-side helpers."""

from datetime import UTC, datetime

from app.models.domain import ImageMetadataRecord
from app.search.embeddings import build_embedding_records


class FakeEmbedder:
    """Return deterministic vectors for tests."""

    def embed_text(self, text: str) -> list[float]:
        """Return a fixed-size deterministic vector for the given text.

        Args:
            text: Text being embedded.

        Returns:
            list[float]: Deterministic vector.
        """

        return [float(len(text)), 1.0]


def build_record(image_id: str, status: str) -> ImageMetadataRecord:
    """Build a metadata record for embedding tests.

    Args:
        image_id: Stable image identifier.
        status: Record status.

    Returns:
        ImageMetadataRecord: Metadata record for testing.
    """

    return ImageMetadataRecord(
        image_id=image_id,
        filename=f"{image_id}.jpg",
        filepath=f"/tmp/{image_id}.jpg",
        file_url=f"/data/images/{image_id}.jpg",
        mime_type="image/jpeg",
        description="Ingredient description",
        tags=["ingredient"],
        search_text="ingredient description",
        processed_at=datetime.now(tz=UTC),
        last_modified=datetime.now(tz=UTC),
        embedding_version="v1",
        model_version="vision-test",
        status=status,
        error_message="",
    )


def test_build_embedding_records_only_embeds_ready_rows():
    """Only ready records should be turned into embedding rows."""

    records = [build_record("img_ready", "ready"), build_record("img_stale", "stale")]
    embedding_records = build_embedding_records(records, FakeEmbedder())
    assert [record.image_id for record in embedding_records] == ["img_ready"]

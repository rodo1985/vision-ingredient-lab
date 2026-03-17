"""Unit tests for CSV metadata persistence."""

from datetime import UTC, datetime

from app.models.domain import ImageMetadataRecord
from app.repositories.metadata_store import MetadataStore


def test_metadata_store_round_trip(tmp_path):
    """CSV store should preserve tags and timestamps during a round trip."""

    store = MetadataStore(tmp_path / "image_metadata.csv")
    record = ImageMetadataRecord(
        image_id="img_tomato",
        filename="tomato.jpg",
        filepath="/tmp/tomato.jpg",
        file_url="/data/images/tomato.jpg",
        mime_type="image/jpeg",
        description="A tomato on a table.",
        tags=["red", "tomato"],
        search_text="tomato red",
        processed_at=datetime(2026, 3, 16, tzinfo=UTC),
        last_modified=datetime(2026, 3, 16, 12, 0, tzinfo=UTC),
        embedding_version="v1",
        model_version="vision-test",
        status="ready",
        error_message="",
    )
    store.save_all([record])
    loaded = store.load_all()
    assert loaded == [record]

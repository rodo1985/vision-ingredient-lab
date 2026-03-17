"""Unit tests for folder scanning behavior."""

from datetime import UTC, datetime

from app.models.domain import ImageMetadataRecord
from app.services.folder_scanner import build_image_id, scan_image_folder


def build_record(path, last_modified: datetime) -> ImageMetadataRecord:
    """Build a minimal metadata record for scanner tests.

    Args:
        path: Source image path.
        last_modified: Timestamp stored in metadata.

    Returns:
        ImageMetadataRecord: Minimal test record.
    """

    return ImageMetadataRecord(
        image_id=build_image_id(path),
        filename=path.name,
        filepath=str(path.resolve()),
        file_url=f"/data/images/{path.name}",
        mime_type="image/jpeg",
        description="Existing description",
        tags=["tomato"],
        search_text="tomato",
        processed_at=datetime.now(tz=UTC),
        last_modified=last_modified,
        embedding_version="v1",
        model_version="test-model",
        status="ready",
        error_message="",
    )


def test_scan_detects_new_files(tmp_path):
    """Scanner should report new files from an empty metadata store."""

    image_path = tmp_path / "tomato.jpg"
    image_path.write_bytes(b"image")
    result = scan_image_folder(tmp_path, [])
    assert result.new_paths == [image_path]
    assert result.updated_paths == []
    assert result.stale_ids == []


def test_scan_ignores_unchanged_files(tmp_path):
    """Scanner should skip files whose stored modification time is unchanged."""

    image_path = tmp_path / "tomato.jpg"
    image_path.write_bytes(b"image")
    modified_at = datetime.fromtimestamp(image_path.stat().st_mtime, tz=UTC)
    existing = [build_record(image_path, modified_at)]
    result = scan_image_folder(tmp_path, existing)
    assert result.new_paths == []
    assert result.updated_paths == []


def test_scan_flags_modified_files(tmp_path):
    """Scanner should mark files for reprocessing when modified times change."""

    image_path = tmp_path / "tomato.jpg"
    image_path.write_bytes(b"image")
    existing = [build_record(image_path, datetime(2020, 1, 1, tzinfo=UTC))]
    result = scan_image_folder(tmp_path, existing)
    assert result.updated_paths == [image_path]


def test_scan_marks_missing_files_stale(tmp_path):
    """Scanner should mark metadata rows stale when files are missing."""

    missing_path = tmp_path / "missing.jpg"
    existing = [build_record(missing_path, datetime(2020, 1, 1, tzinfo=UTC))]
    result = scan_image_folder(tmp_path, existing)
    assert result.stale_ids == [build_image_id(missing_path)]

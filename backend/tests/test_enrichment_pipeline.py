"""Tests for startup enrichment and new-image detection."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from backend.app.models.metadata import ImageFileRecord, MetadataRecord
from backend.app.services.enrichment_pipeline import MetadataEnrichmentPipeline
from backend.app.services.metadata_repository import MetadataCSVRepository
from backend.app.services.vision_client import VisionMetadata


class StubVisionClient:
    """Provide deterministic image descriptions for pipeline tests.

    Parameters:
        None.

    Returns:
        StubVisionClient: Simple fake object with a `describe_image` method.

    Raises:
        None.
    """

    def describe_image(self, image_path: Path) -> VisionMetadata:
        """Return deterministic metadata for a supplied image path.

        Parameters:
            image_path: File path passed by the enrichment pipeline.

        Returns:
            VisionMetadata: Fixed structured metadata for assertions.

        Raises:
            None.
        """

        ingredient_name = image_path.stem.lower()
        return VisionMetadata(
            description=f"A close-up of {ingredient_name}",
            keywords=(ingredient_name, "ingredient"),
            source_path=image_path,
        )


def _build_file_record(filepath: str) -> ImageFileRecord:
    """Create a deterministic image file record for tests.

    Parameters:
        filepath: Image file path to embed in the returned record.

    Returns:
        ImageFileRecord: Static file record with a UTC timestamp.

    Raises:
        None.
    """

    return ImageFileRecord(
        filename=Path(filepath).name,
        filepath=filepath,
        last_modified=datetime(2024, 1, 2, 3, 4, 5, tzinfo=timezone.utc),
    )


def _build_metadata_record(filepath: str) -> MetadataRecord:
    """Create a stored metadata record used for repository setup.

    Parameters:
        filepath: File path to use as the deduplication key.

    Returns:
        MetadataRecord: Persisted-style metadata record.

    Raises:
        None.
    """

    timestamp = datetime(2024, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
    return MetadataRecord(
        filename=Path(filepath).name,
        filepath=filepath,
        description="existing metadata",
        keywords=["existing"],
        processed_at=timestamp,
        last_modified=timestamp,
    )


def test_identify_new_images_returns_only_unprocessed_files(tmp_path: Path) -> None:
    """Verify startup sync returns only files missing from the repository.

    Parameters:
        tmp_path: Pytest temporary directory fixture.

    Returns:
        None

    Raises:
        AssertionError: If processed files are not filtered out correctly.
    """

    repository = MetadataCSVRepository(tmp_path / "metadata.csv")
    repository.append_records([_build_metadata_record("/dataset/tomato.jpg")])
    scanner_output = [
        _build_file_record("/dataset/tomato.jpg"),
        _build_file_record("/dataset/basil.jpg"),
    ]
    pipeline = MetadataEnrichmentPipeline(
        metadata_repository=repository,
        vision_client=StubVisionClient(),
        scanner=lambda _: scanner_output,
    )

    new_files = pipeline.identify_new_images(Path("/dataset"))

    assert [record.filepath for record in new_files] == ["/dataset/basil.jpg"]


def test_run_persists_metadata_for_new_images(tmp_path: Path) -> None:
    """Verify the pipeline enriches and stores records for new files only.

    Parameters:
        tmp_path: Pytest temporary directory fixture.

    Returns:
        None

    Raises:
        AssertionError: If created records are not persisted correctly.
    """

    repository = MetadataCSVRepository(tmp_path / "metadata.csv")
    pipeline = MetadataEnrichmentPipeline(
        metadata_repository=repository,
        vision_client=StubVisionClient(),
        scanner=lambda _: [
            _build_file_record("/dataset/tomato.jpg"),
            _build_file_record("/dataset/basil.jpg"),
        ],
    )

    result = pipeline.run(Path("/dataset"))
    stored_records = repository.load_all()

    assert result.discovered_files == 2
    assert result.new_files == 2
    assert result.persisted_records == 2
    assert len(result.records) == 2
    assert {record.filepath for record in stored_records} == {
        "/dataset/tomato.jpg",
        "/dataset/basil.jpg",
    }

"""Tests for the startup synchronization service."""

from __future__ import annotations

from pathlib import Path

from backend.ingestion.scanner import ImageFileRecord, ImageScanner
from backend.metadata_repository import CsvMetadataRepository, MetadataRow
from backend.services.startup_sync import StartupSyncService


def _create_metadata_row(image_path: Path) -> MetadataRow:
    """Build a metadata row matching the provided image path.

    Parameters:
        image_path: Image path to mirror in the metadata row.

    Returns:
        MetadataRow: Persistable row used by startup sync tests.

    Raises:
        None.
    """

    return MetadataRow(
        filename=image_path.name,
        filepath=str(image_path.resolve()),
        description="Description",
        keywords=["keyword"],
        processed_at="2024-01-01T00:00:00",
        last_modified="2024-01-01T00:00:00",
    )


def test_detect_new_files_returns_only_unprocessed(tmp_path: Path) -> None:
    """Ensure persisted images are not returned as new files.

    Parameters:
        tmp_path: Temporary directory fixture.

    Returns:
        None.

    Raises:
        None.
    """

    images_dir = tmp_path / "images"
    image = images_dir / "tomato.png"
    image.parent.mkdir(parents=True)
    image.write_text("image")

    repo = CsvMetadataRepository(tmp_path / "metadata.csv")
    repo.append(_create_metadata_row(image))

    service = StartupSyncService(scanner=ImageScanner(), repository=repo)
    assert service.detect_new_files(images_dir) == []


def test_detect_new_files_includes_missing_entries(tmp_path: Path) -> None:
    """Ensure images missing from metadata are returned for enrichment.

    Parameters:
        tmp_path: Temporary directory fixture.

    Returns:
        None.

    Raises:
        None.
    """

    images_dir = tmp_path / "images"
    image = images_dir / "tomato.png"
    alternate = images_dir / "basil.png"
    image.parent.mkdir(parents=True)
    image.write_text("one")
    alternate.write_text("two")

    repo = CsvMetadataRepository(tmp_path / "metadata.csv")
    repo.append(_create_metadata_row(image))

    service = StartupSyncService(scanner=ImageScanner(), repository=repo)
    missing = service.detect_new_files(images_dir)

    assert len(missing) == 1
    assert missing[0].filepath == str(alternate.resolve())


def test_detect_new_files_accepts_multiple_directories(tmp_path: Path) -> None:
    """Ensure startup sync can scan multiple directories in a single run.

    Parameters:
        tmp_path: Temporary directory fixture.

    Returns:
        None.

    Raises:
        None.
    """

    first = tmp_path / "a"
    second = tmp_path / "b"
    first.mkdir()
    second.mkdir()
    (first / "one.png").write_text("one")
    (second / "two.png").write_text("two")

    repo = CsvMetadataRepository(tmp_path / "metadata.csv")
    service = StartupSyncService(scanner=ImageScanner(), repository=repo)

    missing = service.detect_new_files((first, second))
    assert {record.filename for record in missing} == {"one.png", "two.png"}


def test_identify_new_files_filters_preloaded_scan_results(tmp_path: Path) -> None:
    """Ensure the pure comparison helper filters already known filepaths.

    Parameters:
        tmp_path: Temporary directory fixture.

    Returns:
        None.

    Raises:
        None.
    """

    service = StartupSyncService(
        scanner=ImageScanner(),
        repository=CsvMetadataRepository(tmp_path / "metadata.csv"),
    )
    scanned_files = [
        ImageFileRecord("existing.png", "/tmp/existing.png", 1.0),
        ImageFileRecord("new.png", "/tmp/new.png", 2.0),
    ]
    existing = [
        MetadataRow("existing.png", "/tmp/existing.png", "desc", ["tag"], "now", "1.0")
    ]

    detected = service.identify_new_files(
        scanned_files=scanned_files,
        existing_metadata=existing,
    )

    assert detected == [ImageFileRecord("new.png", "/tmp/new.png", 2.0)]

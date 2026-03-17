"""Tests for the preserved legacy CSV metadata repository."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from backend.metadata_repository import CsvMetadataRepository, MetadataRow


def _sample_row(filepath: Path, keywords: list[str] | None = None) -> MetadataRow:
    """Create a sample metadata row for repository tests.

    Parameters:
        filepath: Path used to populate file-specific fields.
        keywords: Optional keyword override for the sample row.

    Returns:
        MetadataRow: Test metadata row.

    Raises:
        None.
    """

    now = datetime.now(UTC).isoformat()
    return MetadataRow(
        filename=filepath.name,
        filepath=str(filepath),
        description="tasty ingredient",
        keywords=["tomato", "basil"] if keywords is None else keywords,
        processed_at=now,
        last_modified=now,
    )


def test_legacy_initialize_creates_file(tmp_path: Path) -> None:
    """Ensure repository initialization creates the target CSV with headers."""

    repo = CsvMetadataRepository(tmp_path / "meta.csv")
    repo.initialize()
    assert repo._path.exists()
    assert repo._path.read_text().splitlines()[0].split(",")[0] == "filename"


def test_legacy_append_and_read_roundtrip(tmp_path: Path) -> None:
    """Ensure a stored metadata row can be read back without data loss."""

    repo = CsvMetadataRepository(tmp_path / "meta.csv")
    row = _sample_row(tmp_path / "tomato.png")
    repo.append(row)
    stored = repo.read_all()
    assert len(stored) == 1
    assert stored[0].filename == "tomato.png"
    assert stored[0].keywords == ["tomato", "basil"]


def test_legacy_append_updates_existing_entry(tmp_path: Path) -> None:
    """Ensure appending an existing filepath replaces the previous row."""

    repo = CsvMetadataRepository(tmp_path / "meta.csv")
    row = _sample_row(tmp_path / "lettuce.png")
    repo.append(row)
    updated = MetadataRow(
        filename="lettuce.png",
        filepath=str(tmp_path / "lettuce.png"),
        description="very green",
        keywords=["lettuce"],
        processed_at=datetime.now(UTC).isoformat(),
        last_modified=datetime.now(UTC).isoformat(),
    )
    repo.append(updated)
    entries = repo.read_all()
    assert len(entries) == 1
    assert entries[0].description == "very green"
    assert entries[0].keywords == ["lettuce"]


def test_legacy_keywords_serialization_handles_empty(tmp_path: Path) -> None:
    """Ensure empty keyword lists round-trip through the CSV representation."""

    repo = CsvMetadataRepository(tmp_path / "meta.csv")
    row = _sample_row(tmp_path / "cheese.png", keywords=[])
    repo.append(row)
    loaded = repo.read_all()
    assert loaded[0].keywords == []


def test_legacy_read_empty_file_returns_empty(tmp_path: Path) -> None:
    """Ensure reading a newly initialized repository returns no rows."""

    repo = CsvMetadataRepository(tmp_path / "meta.csv")
    entries = repo.read_all()
    assert entries == []

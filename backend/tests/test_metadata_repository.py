"""Tests for the metadata CSV repository and keyword helpers."""

from datetime import datetime, timezone
from pathlib import Path

from backend.app.models.metadata import MetadataRecord, serialize_keywords
from backend.app.services.metadata_repository import MetadataCSVRepository


def _build_record(filepath: str, description: str = "sample") -> MetadataRecord:
    """Create a deterministic MetadataRecord for testing."""

    timestamp = datetime(2024, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
    return MetadataRecord(
        filename=Path(filepath).name,
        filepath=filepath,
        description=description,
        keywords=["tomato", "basil", "tomato"],
        processed_at=timestamp,
        last_modified=timestamp,
    )


def test_serialize_keywords_returns_sorted_unique():
    """Keywords are normalized to a sorted, deduplicated JSON string."""

    serialized = serialize_keywords(["basil", "Tomato", "basil", "  ", "basil "])
    assert serialized == "[\"Tomato\", \"basil\"]"


def test_append_records_skips_duplicates(tmp_path: Path):
    """Append honors filepath uniqueness and only writes truly new rows."""

    repo = MetadataCSVRepository(tmp_path / "meta.csv")
    record = _build_record("images/tomato.png")
    assert repo.append_records([record]) == 1
    assert repo.append_records([record]) == 0
    entries = repo.load_all()
    assert len(entries) == 1
    assert entries[0].filepath == record.filepath


def test_upsert_record_overwrites_existing_entry(tmp_path: Path):
    """Upsert replaces the matching filepath and preserves ordering."""

    repo = MetadataCSVRepository(tmp_path / "meta.csv")
    original = _build_record("images/base.png", description="first")
    repo.append_records([original])
    updated = _build_record("images/base.png", description="second")
    repo.upsert_record(updated)
    entries = repo.load_all()
    assert len(entries) == 1
    assert entries[0].description == "second"


def test_load_all_returns_records_in_csv(tmp_path: Path):
    """Load all returns the records that were written to disk."""

    repo = MetadataCSVRepository(tmp_path / "meta.csv")
    repo.append_records([_build_record("images/a.png"), _build_record("images/b.png")])
    entries = repo.load_all()
    assert {entry.filepath for entry in entries} == {"images/a.png", "images/b.png"}

"""Tests for the metadata search service."""

from datetime import datetime, timezone

from backend.app.models.metadata import MetadataRecord
from backend.app.services.search_service import search_metadata


def _build_record(
    filepath: str,
    description: str,
    keywords: list[str],
) -> MetadataRecord:
    """Create a deterministic MetadataRecord for search tests."""

    timestamp = datetime(2025, 1, 1, tzinfo=timezone.utc)
    return MetadataRecord(
        filename=filepath.split("/")[-1],
        filepath=filepath,
        description=description,
        keywords=keywords,
        processed_at=timestamp,
        last_modified=timestamp,
    )


def test_search_prioritizes_keyword_matches() -> None:
    """Ensure keyword hits rank higher than mere description matches."""

    tomato_record = _build_record(
        "data/tomato.jpg",
        "Fresh tomato slices with basil.",
        keywords=["tomato", "basil"],
    )
    basil_record = _build_record(
        "data/basil.jpg",
        "Basil leaves arranged artfully.",
        keywords=["basil"],
    )

    results = search_metadata([tomato_record, basil_record], "TOMATO")

    assert results == [tomato_record]


def test_search_falls_back_to_description() -> None:
    """Verify description tokens provide matches when keywords are absent."""

    description_only = _build_record(
        "data/arugula.jpg",
        "Crunchy arugula and roasted peppers.",
        keywords=[],
    )
    other = _build_record(
        "data/cheese.jpg",
        "Soft cheese rounds.",
        keywords=["cheese"],
    )

    results = search_metadata([description_only, other], "arugula")

    assert results == [description_only]


def test_search_empty_query_returns_all_sorted() -> None:
    """Ensure empty queries return all records sorted by filepath."""

    record_b = _build_record(
        "data/basil.jpg",
        "Basil overview.",
        keywords=["basil"],
    )
    record_a = _build_record(
        "data/apple.jpg",
        "Apple slices.",
        keywords=["apple"],
    )

    results = search_metadata([record_b, record_a], "")

    assert len(results) == 2
    assert results[0].filepath == "data/apple.jpg"
    assert results[1].filepath == "data/basil.jpg"

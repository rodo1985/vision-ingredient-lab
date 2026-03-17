"""Tests for the preserved legacy search service."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from backend.metadata_repository import CsvMetadataRepository, MetadataRow
from backend.search.service import search_metadata


def _now_timestamp() -> str:
    """Return a timezone-aware ISO timestamp for legacy test rows."""

    return datetime.now(UTC).isoformat()


def _add_row(
    repo: CsvMetadataRepository,
    filename: str,
    description: str,
    keywords: list[str],
) -> MetadataRow:
    """Persist a metadata row to the repository for testing."""

    filepath = str(Path(filename).resolve())
    row = MetadataRow(
        filename=filename,
        filepath=filepath,
        description=description,
        keywords=keywords,
        processed_at=_now_timestamp(),
        last_modified=_now_timestamp(),
    )
    repo.append(row)
    return row


def test_legacy_search_matches_keyword(tmp_path: Path) -> None:
    """Ensure keyword matches are surfaced by the legacy search service."""

    repo = CsvMetadataRepository(tmp_path / "meta.csv")
    _add_row(repo, "tomato.png", "Chef's tomato", ["tomato"])

    results = search_metadata(repo, "tomato")

    assert len(results) == 1
    assert results[0].filename == "tomato.png"


def test_legacy_search_matches_description(tmp_path: Path) -> None:
    """Ensure description matches are surfaced when keywords do not match."""

    repo = CsvMetadataRepository(tmp_path / "meta.csv")
    _add_row(repo, "basil.png", "Fresh basil leaves", ["herb"])

    results = search_metadata(repo, "fresh")

    assert len(results) == 1
    assert results[0].filename == "basil.png"


def test_legacy_search_returns_empty_for_no_match(tmp_path: Path) -> None:
    """Ensure searches that hit nothing return an empty list."""

    repo = CsvMetadataRepository(tmp_path / "meta.csv")
    _add_row(repo, "cheese.png", "Creamy cheese layer", ["cheese"])

    results = search_metadata(repo, "pepper")

    assert results == []


def test_legacy_search_orders_by_score_and_filepath(tmp_path: Path) -> None:
    """Ensure matches are sorted by keyword score first, then filepath."""

    repo = CsvMetadataRepository(tmp_path / "meta.csv")
    first = _add_row(repo, "alpha.png", "Ingredient A", ["pepper"])
    second = _add_row(repo, "beta.png", "Pepper is spicy", ["spice"])

    results = search_metadata(repo, "pepper")

    assert results == [first, second]


def test_legacy_search_raises_on_empty_query(tmp_path: Path) -> None:
    """Ensure empty queries raise a ValueError."""

    repo = CsvMetadataRepository(tmp_path / "meta.csv")

    with pytest.raises(ValueError):
        search_metadata(repo, "  ")

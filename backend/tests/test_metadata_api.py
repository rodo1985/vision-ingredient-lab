"""Tests for the metadata API routes."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.api.routes.metadata import create_metadata_router
from backend.metadata_repository import CsvMetadataRepository, MetadataRow


def _add_row(
    repo: CsvMetadataRepository,
    filename: str,
    description: str,
    keywords: list[str],
) -> MetadataRow:
    """Persist a metadata row used by the API tests.

    Parameters:
        repo: Repository used by the API under test.
        filename: Source file name for the metadata.
        description: Description stored in the metadata row.
        keywords: Keywords stored in the metadata row.

    Returns:
        MetadataRow: Row stored in the repository.
    """

    row = MetadataRow(
        filename=filename,
        filepath=str(Path(filename).resolve()),
        description=description,
        keywords=keywords,
        processed_at="2026-03-17T00:00:00+00:00",
        last_modified="1.0",
    )
    repo.append(row)
    return row


def _build_app(repo: CsvMetadataRepository) -> FastAPI:
    """Create a FastAPI app wired to the metadata routes.

    Parameters:
        repo: Repository instance used by the metadata endpoints.

    Returns:
        FastAPI: Application ready for TestClient usage.
    """

    app = FastAPI()
    app.include_router(create_metadata_router(repo))
    return app


def test_list_metadata_returns_persisted_rows(tmp_path: Path) -> None:
    """Ensure listing metadata exposes the persisted data."""

    repo = CsvMetadataRepository(tmp_path / "meta.csv")
    row = _add_row(repo, "tomato.png", "Fresh tomato", ["tomato"])
    client = TestClient(_build_app(repo))

    response = client.get("/metadata/")
    assert response.status_code == 200
    assert response.json() == [asdict(row)]


def test_search_metadata_returns_keyword_matches(tmp_path: Path) -> None:
    """Ensure the search endpoint returns keyword matches sorted by relevance."""

    repo = CsvMetadataRepository(tmp_path / "meta.csv")
    first = _add_row(repo, "alpha.png", "First entry", ["pepper"])
    _add_row(repo, "beta.png", "Second entry", ["spice"])
    client = TestClient(_build_app(repo))

    response = client.get("/metadata/search", params={"q": "pepper"})
    assert response.status_code == 200
    assert response.json()[0]["filename"] == first.filename


def test_search_metadata_handles_empty_query(tmp_path: Path) -> None:
    """Ensure the search endpoint rejects empty queries with an error."""

    repo = CsvMetadataRepository(tmp_path / "meta.csv")
    client = TestClient(_build_app(repo))

    response = client.get("/metadata/search", params={"q": "  "})
    assert response.status_code == 400

"""Tests for the search API endpoints."""

from datetime import datetime, timezone
from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.api.dependencies import get_metadata_repository
from backend.app.main import app
from backend.app.models.metadata import MetadataRecord
from backend.app.services.metadata_repository import MetadataCSVRepository


def _build_record(
    filepath: str,
    description: str,
    keywords: list[str],
) -> MetadataRecord:
    """Create a deterministic metadata record for HTTP tests.

    Parameters:
        filepath: File path stored in the metadata row.
        description: Description stored in the metadata row.
        keywords: Keyword list stored in the metadata row.

    Returns:
        MetadataRecord: Stable record used by API tests.

    Raises:
        None.
    """

    timestamp = datetime(2025, 1, 1, tzinfo=timezone.utc)
    return MetadataRecord(
        filename=Path(filepath).name,
        filepath=filepath,
        description=description,
        keywords=keywords,
        processed_at=timestamp,
        last_modified=timestamp,
    )


def _using_repository(tmp_path: Path) -> MetadataCSVRepository:
    """Return a repository backed by a temporary CSV file.

    Parameters:
        tmp_path: Pytest temporary directory fixture.

    Returns:
        MetadataCSVRepository: Temporary repository for test isolation.

    Raises:
        None.
    """

    return MetadataCSVRepository(tmp_path / "metadata.csv")


def test_list_metadata_returns_all_records(tmp_path: Path) -> None:
    """Verify `/api/images` returns every metadata row.

    Parameters:
        tmp_path: Pytest temporary directory fixture.

    Returns:
        None

    Raises:
        AssertionError: If the endpoint omits or mutates stored rows.
    """

    repository = _using_repository(tmp_path)
    repository.append_records(
        [
            _build_record("data/tomato.jpg", "Tomato slices", ["tomato"]),
            _build_record("data/basil.jpg", "Fresh basil", ["basil"]),
        ]
    )

    app.dependency_overrides[get_metadata_repository] = lambda: repository
    client = TestClient(app)

    response = client.get("/api/images")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 2
    assert {item["filepath"] for item in payload} == {
        "data/tomato.jpg",
        "data/basil.jpg",
    }

    app.dependency_overrides.pop(get_metadata_repository, None)


def test_search_metadata_filters_by_query(tmp_path: Path) -> None:
    """Verify `/api/search` returns rows matching the query term.

    Parameters:
        tmp_path: Pytest temporary directory fixture.

    Returns:
        None

    Raises:
        AssertionError: If the endpoint returns the wrong search results.
    """

    repository = _using_repository(tmp_path)
    repository.append_records(
        [
            _build_record("data/tomato.jpg", "Tomato slices", ["tomato"]),
            _build_record("data/mozzarella.jpg", "Mozzarella", ["cheese"]),
        ]
    )

    app.dependency_overrides[get_metadata_repository] = lambda: repository
    client = TestClient(app)

    response = client.get("/api/search", params={"query": "tomato"})

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["filepath"] == "data/tomato.jpg"

    app.dependency_overrides.pop(get_metadata_repository, None)


def test_list_metadata_respects_max_results(tmp_path: Path) -> None:
    """Verify `/api/images` honors the `max_results` query parameter.

    Parameters:
        tmp_path: Pytest temporary directory fixture.

    Returns:
        None

    Raises:
        AssertionError: If the endpoint ignores the result limit.
    """

    repository = _using_repository(tmp_path)
    repository.append_records(
        [
            _build_record("data/apple.jpg", "Apple slices", ["apple"]),
            _build_record("data/basil.jpg", "Fresh basil", ["basil"]),
        ]
    )

    app.dependency_overrides[get_metadata_repository] = lambda: repository
    client = TestClient(app)

    response = client.get("/api/images", params={"max_results": 1})

    assert response.status_code == 200
    assert len(response.json()) == 1

    app.dependency_overrides.pop(get_metadata_repository, None)

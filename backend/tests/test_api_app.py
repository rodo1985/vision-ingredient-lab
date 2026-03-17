"""Tests for the shared FastAPI application wiring."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from backend.api.app import create_app
from backend.metadata_repository import CsvMetadataRepository


def test_healthcheck_returns_ok(tmp_path: Path) -> None:
    """Ensure the shared application wiring exposes the health endpoint.

    Parameters:
        tmp_path: Temporary directory fixture.

    Returns:
        None.

    Raises:
        None.
    """

    repository = CsvMetadataRepository(tmp_path / "metadata.csv")
    client = TestClient(create_app(metadata_repository=repository))

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_app_mounts_metadata_routes_under_api_prefix(tmp_path: Path) -> None:
    """Ensure the integrated application exposes metadata routes under `/api`.

    Parameters:
        tmp_path: Temporary directory fixture.

    Returns:
        None.

    Raises:
        None.
    """

    repository = CsvMetadataRepository(tmp_path / "metadata.csv")
    client = TestClient(create_app(metadata_repository=repository))

    response = client.get("/api/metadata/")

    assert response.status_code == 200
    assert response.json() == []

"""Tests for the FastAPI application entrypoint."""

from fastapi.testclient import TestClient

from backend.app.main import app


def test_healthcheck_returns_ok() -> None:
    """Verify the root health endpoint responds successfully.

    Returns:
        None

    Raises:
        AssertionError: If the API does not return the expected success payload.

    Example:
        This test runs as part of `uv run pytest`.
    """

    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_search_router_healthcheck_returns_ok() -> None:
    """Verify the search router is mounted on the API application.

    Returns:
        None

    Raises:
        AssertionError: If the router is not mounted or returns an unexpected payload.

    Example:
        This test runs as part of `uv run pytest`.
    """

    client = TestClient(app)

    response = client.get("/api/search/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_generation_router_healthcheck_returns_ok() -> None:
    """Verify the generation router is mounted on the API application.

    Returns:
        None

    Raises:
        AssertionError: If the router is not mounted or returns an unexpected payload.

    Example:
        This test runs as part of `uv run pytest`.
    """

    client = TestClient(app)

    response = client.get("/api/generate/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

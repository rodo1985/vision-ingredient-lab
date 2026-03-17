"""Route tests for the FastAPI application."""

from datetime import UTC, datetime
from pathlib import Path

from fastapi.testclient import TestClient

from app.api.routes import create_router
from app.repositories.embedding_store import EmbeddingStore
from app.repositories.metadata_store import MetadataStore
from fastapi import FastAPI


class FakeSyncService:
    """Return a deterministic sync payload for route tests."""

    def run(self):
        """Return a fixed sync result payload.

        Returns:
            dict: Sync response payload.
        """

        return {
            "scannedCount": 0,
            "newCount": 0,
            "updatedCount": 0,
            "failedCount": 0,
            "startedAt": datetime.now(tz=UTC),
            "completedAt": datetime.now(tz=UTC),
        }


class FakeGenerationService:
    """Return a deterministic generation payload for route tests."""

    def generate(self, prompt: str):
        """Return a deterministic generation tuple.

        Args:
            prompt: Generated prompt.

        Returns:
            tuple[str, str, datetime]: Mock generation payload.
        """

        return "gen_test", "/data/generated/gen_test.png", datetime.now(tz=UTC)


def create_test_client(tmp_path: Path) -> TestClient:
    """Build a test client with empty repositories.

    Args:
        tmp_path: Temporary path for repositories.

    Returns:
        TestClient: Configured test client.
    """

    metadata_store = MetadataStore(tmp_path / "metadata.csv")
    embedding_store = EmbeddingStore(tmp_path / "embeddings.jsonl")
    app = FastAPI()
    app.include_router(
        create_router(
            metadata_store=metadata_store,
            embedding_store=embedding_store,
            sync_service=FakeSyncService(),
            generation_service=FakeGenerationService(),
            embed_query=lambda query: [1.0, 0.0] if query else [],
            enable_startup_sync=False,
            max_search_results=20,
            mode="api",
        )
    )
    return TestClient(app)


def test_health_route_returns_ok(tmp_path):
    """Health route should return a successful payload."""

    client = create_test_client(tmp_path)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_generate_route_validates_missing_ids(tmp_path):
    """Generate route should reject unknown ingredient ids."""

    client = create_test_client(tmp_path)
    response = client.post("/api/generate", json={"ingredientIds": ["img_missing"]})
    assert response.status_code == 404


def test_generate_route_rejects_empty_selection(tmp_path):
    """Generate route should reject empty ingredient selections."""

    client = create_test_client(tmp_path)
    response = client.post("/api/generate", json={"ingredientIds": []})
    assert response.status_code == 422

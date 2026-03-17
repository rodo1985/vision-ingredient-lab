"""Tests for the preserved legacy generation API stack."""

from __future__ import annotations

from typing import Mapping

from fastapi.testclient import TestClient

from backend.api.app import create_app
from backend.clients.image_generation_client import ImageGenerationClient


class FakeImageService:
    """Test double for the legacy external image generation service."""

    def __init__(self) -> None:
        """Initialize call recorder state."""

        self.calls: list[tuple[str, str | None]] = []

    def generate(self, prompt: str, size: str | None = None) -> Mapping[str, object]:
        """Return a canned image payload while recording the call."""

        self.calls.append((prompt, size))
        return {
            "data": [
                {
                    "url": "https://example.com/generated.png",
                    "description": "Generated food image",
                    "keywords": ["tomato", "basil"],
                }
            ]
        }


def test_legacy_generation_route_returns_image_url() -> None:
    """Ensure the legacy API returns a generated image payload for valid requests."""

    service = FakeImageService()
    client = ImageGenerationClient(image_service=service)
    app = create_app(client)
    test_client = TestClient(app)

    response = test_client.post("/api/generation", json={"ingredients": ["tomato", "basil"]})

    assert response.status_code == 200
    body = response.json()
    assert body["image_url"] == "https://example.com/generated.png"
    assert "prompt" in body
    assert body["metadata"]["description"] == "Generated food image"


def test_legacy_generation_route_passes_requested_size() -> None:
    """Ensure the legacy endpoint forwards an explicit size override to the image client."""

    service = FakeImageService()
    client = ImageGenerationClient(image_service=service)
    app = create_app(client)
    test_client = TestClient(app)

    response = test_client.post(
        "/api/generation",
        json={"ingredients": ["tomato", "basil"], "size": "512x512"},
    )

    assert response.status_code == 200
    assert service.calls[0][1] == "512x512"


def test_legacy_generation_route_validates_ingredients() -> None:
    """Ensure the legacy API rejects requests with insufficient ingredients."""

    image_service = FakeImageService()
    client = ImageGenerationClient(image_service=image_service)
    app = create_app(client)
    test_client = TestClient(app)

    response = test_client.post("/api/generation", json={"ingredients": ["tomato"]})

    assert response.status_code == 422

"""Unit tests for the image generation client wrapper."""

from __future__ import annotations

from typing import Mapping

import pytest

from backend.clients.image_generation_client import ImageGenerationClient, ImageService


class _FakeImageServiceMissingUrl:
    """Stubbed image service that returns malformed payloads."""

    def generate(self, prompt: str, size: str | None = None) -> Mapping[str, object]:
        """Return a response lacking URL data."""

        return {"data": [{"description": "no url"}]}


class _FakeImageServiceEmptyData:
    """Stubbed image service that returns an empty list of entries."""

    def generate(self, prompt: str, size: str | None = None) -> Mapping[str, object]:
        """Return a response without data entries."""

        return {"data": []}


class _FakeImageService:
    """Simple pass-through image service used for success paths."""

    def generate(self, prompt: str, size: str | None = None) -> Mapping[str, object]:
        """Return a minimal successful payload."""

        return {"data": [{"url": "https://example.com/img.png"}]}


def _build_client(service: ImageService) -> ImageGenerationClient:
    """Create a client configured with the supplied image service stub."""

    return ImageGenerationClient(image_service=service)


def test_generate_image_raises_without_url() -> None:
    """Ensure the client raises when the service does not return an image URL."""

    client = _build_client(_FakeImageServiceMissingUrl())

    with pytest.raises(ValueError, match="missing image URL"):
        client.generate_image("ingredients")


def test_generate_image_raises_on_empty_data() -> None:
    """Ensure the client rejects responses without entries."""

    client = _build_client(_FakeImageServiceEmptyData())

    with pytest.raises(ValueError, match="invalid payload"):
        client.generate_image("ingredients")


def test_generate_image_success() -> None:
    """Ensure the client returns a structured result when the service is healthy."""

    client = _build_client(_FakeImageService())
    result = client.generate_image("ingredients")

    assert result.image_url == "https://example.com/img.png"
    assert result.prompt == "ingredients"

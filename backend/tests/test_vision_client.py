"""Tests for the OpenAI vision client wrapper."""

from pathlib import Path

import pytest

from backend.app.services.vision_client import VisionClient, VisionMetadata


class DummyResponses:
    """Minimal stub for the OpenAI responses API."""

    def __init__(self, payload: dict[str, object]) -> None:
        self._payload = payload

    def create(self, **kwargs: object) -> dict[str, object]:
        """Return the configured payload without performing network I/O."""

        return self._payload


class DummyOpenAIClient:
    """Simple container exposing a `responses` attribute."""

    def __init__(self, payload: dict[str, object]) -> None:
        self.responses = DummyResponses(payload)


def test_describe_image_parses_mock_response(tmp_path: Path) -> None:
    """Verify the client extracts description and keywords from the response.

    Parameters:
        tmp_path: Pytest temporary directory fixture.

    Returns:
        None

    Raises:
        AssertionError: If the parsed metadata does not match the stubbed response.
    """

    image_file = tmp_path / "ingredient.jpg"
    image_file.write_text("placeholder")

    payload = {
        "output": [
            {"text": "Fresh tomato slices with basil"},
            "Creamy mozzarella on the side.",
        ],
        "metadata": {"keywords": ["tomato", "Mozzarella", "basil"]},
    }

    client = VisionClient(DummyOpenAIClient(payload))

    metadata = client.describe_image(image_file)

    assert isinstance(metadata, VisionMetadata)
    assert metadata.description.startswith("Fresh tomato slices")
    assert metadata.keywords == ("tomato", "mozzarella", "basil")
    assert metadata.source_path == image_file


def test_describe_image_fallback_keywords(tmp_path: Path) -> None:
    """Ensure keywords fall back to the description when metadata lacks keywords.

    Parameters:
        tmp_path: Pytest temporary directory fixture.

    Returns:
        None

    Raises:
        AssertionError: If fallback keyword extraction does not occur.
    """

    image_file = tmp_path / "ingredient.jpg"
    image_file.write_text("placeholder")

    payload = {
        "output": ["Crunchy arugula and roasted peppers."],
        "metadata": {},
    }

    client = VisionClient(DummyOpenAIClient(payload))

    metadata = client.describe_image(image_file)

    assert "crunchy arugula and roasted peppers" in metadata.description.lower()
    assert metadata.keywords == ("crunchy arugula and roasted peppers",)


def test_describe_image_missing_path_raises() -> None:
    """Ensure missing image files produce a `FileNotFoundError`.

    Parameters:
        None.

    Returns:
        None

    Raises:
        AssertionError: If the missing path does not raise the expected exception.
    """

    payload = {"output": ["ignored"], "metadata": {}}
    client = VisionClient(DummyOpenAIClient(payload))

    with pytest.raises(FileNotFoundError):
        client.describe_image(Path("nope.jpg"))

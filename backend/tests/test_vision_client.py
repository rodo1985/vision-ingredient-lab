from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

from backend.clients.vision_client import VisionClient, VisionMetadata


@dataclass
class DummyResponse:
    """Minimal response stub that mimics a JSON-capable HTTP response.

    Parameters:
        payload: JSON payload to return from `json()`.

    Returns:
        DummyResponse: Stub response instance for tests.

    Raises:
        None.
    """

    payload: dict[str, Any]

    def json(self) -> dict[str, Any]:
        """Return the stored JSON payload.

        Parameters:
            None.

        Returns:
            dict[str, Any]: Stored payload for assertions.

        Raises:
            None.
        """

        return self.payload


class DummyHttpClient:
    """Minimal HTTP client stub that records outgoing requests for assertions.

    Parameters:
        None.

    Returns:
        DummyHttpClient: Stub transport object.

    Raises:
        None.
    """

    def __init__(self) -> None:
        """Initialize the stub transport state.

        Parameters:
            None.

        Returns:
            None.

        Raises:
            None.
        """

        self.calls: list[dict[str, Any]] = []
        self.response: Any = DummyResponse({"data": []})

    def post(self, url: str, json: Any, headers: Any) -> Any:
        """Record the outgoing request and return the configured response.

        Parameters:
            url: Target URL used by the client.
            json: JSON payload sent by the client.
            headers: Request headers sent by the client.

        Returns:
            Any: Configured stub response.

        Raises:
            None.
        """

        self.calls.append({"url": url, "json": json, "headers": headers})
        return self.response


def test_build_payload_valid(tmp_path: Path) -> None:
    """Ensure payload construction includes the expected model and file metadata.

    Parameters:
        tmp_path: Temporary directory fixture.

    Returns:
        None.

    Raises:
        None.
    """

    file_path = tmp_path / "ingredient.png"
    file_path.write_bytes(b"PNGDATA")
    client = VisionClient(model="vision-model", http_client=DummyHttpClient())

    payload = client._build_payload(file_path)

    assert payload["model"] == "vision-model"
    assert payload["files"][0]["name"] == "ingredient.png"


def test_analyze_image_parses_response(tmp_path: Path) -> None:
    """Ensure successful responses are normalized into `VisionMetadata`.

    Parameters:
        tmp_path: Temporary directory fixture.

    Returns:
        None.

    Raises:
        None.
    """

    file_path = tmp_path / "ingredient.jpg"
    file_path.write_bytes(b"JPGDATA")
    http = DummyHttpClient()
    http.response = DummyResponse(
        {
            "data": [
                {
                    "description": "Fresh basil and tomato",
                    "keywords": ["basil", "tomato"],
                }
            ]
        }
    )
    client = VisionClient(model="vision-model", http_client=http)

    metadata = client.analyze_image(file_path)

    assert isinstance(metadata, VisionMetadata)
    assert metadata.description == "Fresh basil and tomato"
    assert metadata.keywords == ("basil", "tomato")
    assert len(http.calls) == 1


def test_analyze_image_rejects_malformed_response(tmp_path: Path) -> None:
    """Ensure malformed payloads raise a validation error.

    Parameters:
        tmp_path: Temporary directory fixture.

    Returns:
        None.

    Raises:
        None.
    """

    file_path = tmp_path / "ingredient.jpg"
    file_path.write_bytes(b"JPGDATA")
    http = DummyHttpClient()
    http.response = DummyResponse({"data": [None]})
    client = VisionClient(model="vision-model", http_client=http)

    with pytest.raises(ValueError):
        client.analyze_image(file_path)


def test_analyze_image_requires_client(tmp_path: Path) -> None:
    """Ensure the client fails fast when no HTTP transport is configured.

    Parameters:
        tmp_path: Temporary directory fixture.

    Returns:
        None.

    Raises:
        None.
    """

    file_path = tmp_path / "ingredient.jpg"
    file_path.write_bytes(b"JPGDATA")
    client = VisionClient(model="vision-model")

    with pytest.raises(RuntimeError):
        client.analyze_image(file_path)

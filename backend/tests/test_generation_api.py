"""Tests for the generation API endpoint."""

from __future__ import annotations

from fastapi.testclient import TestClient

from backend.app.api.dependencies import get_generation_service
from backend.app.main import app
from backend.app.services.generation_service import GenerationResult


class StubGenerationService:
    """Provide deterministic generation results for API tests.

    Parameters:
        None.

    Returns:
        StubGenerationService: Fake service with the production `generate` interface.

    Raises:
        None.
    """

    def generate(
        self,
        selected_ingredients: list[str],
        *,
        base_style: str,
        creativity: float,
    ) -> GenerationResult:
        """Return a fixed generation result for assertions.

        Parameters:
            selected_ingredients: Ingredient selection submitted by the client.
            base_style: Requested image style.
            creativity: Requested creativity level.

        Returns:
            GenerationResult: Deterministic fake result for test assertions.

        Raises:
            ValueError: If the request would be invalid in production.
        """

        if len({ingredient.strip().lower() for ingredient in selected_ingredients}) < 2:
            raise ValueError("at least two unique ingredients are required")
        return GenerationResult(
            prompt=f"{base_style} :: {creativity:.2f}",
            image_base64="ZmFrZS1pbWFnZQ==",
            image_url=None,
            revised_prompt="Refined prompt",
            model="gpt-image-1",
        )


def test_generate_image_returns_image_payload() -> None:
    """Verify `/api/generate` returns the generated image payload.

    Parameters:
        None.

    Returns:
        None

    Raises:
        AssertionError: If the endpoint fails to serialize the generation result.
    """

    app.dependency_overrides[get_generation_service] = lambda: StubGenerationService()
    client = TestClient(app)

    response = client.post(
        "/api/generate",
        json={
            "selected_ingredients": ["tomato", "basil"],
            "base_style": "editorial food photography",
            "creativity": 0.7,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["image_base64"] == "ZmFrZS1pbWFnZQ=="
    assert payload["model"] == "gpt-image-1"
    assert payload["revised_prompt"] == "Refined prompt"

    app.dependency_overrides.pop(get_generation_service, None)


def test_generate_image_returns_422_for_invalid_selection() -> None:
    """Verify `/api/generate` surfaces generation validation failures cleanly.

    Parameters:
        None.

    Returns:
        None

    Raises:
        AssertionError: If invalid selections do not produce a 422 response.
    """

    app.dependency_overrides[get_generation_service] = lambda: StubGenerationService()
    client = TestClient(app)

    response = client.post(
        "/api/generate",
        json={
            "selected_ingredients": ["tomato", " tomato "],
            "base_style": "editorial food photography",
            "creativity": 0.7,
        },
    )

    assert response.status_code == 422
    assert "at least two unique ingredients" in response.json()["detail"]

    app.dependency_overrides.pop(get_generation_service, None)

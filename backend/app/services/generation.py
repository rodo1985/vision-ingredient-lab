"""Image prompt building and generation helpers."""

from __future__ import annotations

import base64
from datetime import UTC, datetime
from pathlib import Path

from openai import OpenAI

from app.models.domain import ImageMetadataRecord


def build_generation_prompt(
    selected_records: list[ImageMetadataRecord], creative_direction: str | None = None
) -> str:
    """Build a deterministic image-generation prompt from ingredient records.

    Args:
        selected_records: Selected ingredient records.
        creative_direction: Optional user guidance.

    Returns:
        str: Prompt sent to the image generation model.

    Raises:
        ValueError: Raised when no ingredient records are provided.
    """

    if not selected_records:
        raise ValueError("At least one ingredient must be selected.")
    ingredient_names = ", ".join(record.tags[0] if record.tags else record.filename for record in selected_records)
    prompt = (
        "Create a food-focused creative composition using only these selected ingredients: "
        f"{ingredient_names}. Keep each selected ingredient visually recognizable, and do not add extra ingredients "
        "that are not in the selected list unless the user explicitly asks for them."
    )
    if creative_direction:
        prompt += f" Additional direction: {creative_direction.strip()}."
    return prompt


class ImageGenerationService:
    """Wrap OpenAI Images calls for generated outputs.

    Args:
        client: OpenAI client instance.
        model: Image generation model name.
        output_dir: Directory where generated images are stored.

    Returns:
        ImageGenerationService: Configured generation service.
    """

    def __init__(self, client: OpenAI, model: str, output_dir: Path) -> None:
        """Initialize the generation service.

        Args:
            client: OpenAI client instance.
            model: Image generation model name.
            output_dir: Directory where generated images are stored.

        Returns:
            None
        """

        self.client = client
        self.model = model
        self.output_dir = output_dir

    def generate(self, prompt: str) -> tuple[str, str, datetime]:
        """Generate an image and save it to disk.

        Args:
            prompt: Prompt to send to the image model.

        Returns:
            tuple[str, str, datetime]: Generation id, image URL, and creation time.
        """

        created_at = datetime.now(tz=UTC)
        generation_id = created_at.strftime("gen_%Y%m%d_%H%M%S")
        response = self.client.images.generate(model=self.model, prompt=prompt)
        image_bytes = base64.b64decode(response.data[0].b64_json)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        output_path = self.output_dir / f"{generation_id}.png"
        output_path.write_bytes(image_bytes)
        return generation_id, f"/data/generated/{output_path.name}", created_at

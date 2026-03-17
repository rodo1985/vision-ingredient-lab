"""Helpers for converting selected ingredients into generation prompts."""

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class PromptBuilderConfig:
    """Configuration for composing generation prompts.

    Args:
        base_style: High-level visual style or mood for generation.
        creativity: Float between 0 and 1 describing how bold the combination should feel.

    Example:
        >>> PromptBuilderConfig(base_style="studio food photo", creativity=0.5)
    """

    base_style: str = "dramatic food photography"
    creativity: float = 0.65


def _normalize_ingredient(term: str) -> str:
    """Normalize an ingredient term to a stable form.

    Args:
        term: Raw ingredient name from the UI.

    Returns:
        str: A lowercase, trimmed term suitable for deduplication and prompt usage.

    Raises:
        ValueError: If the normalized term is empty.
    """
    normalized = " ".join(part.strip() for part in term.split()).lower()
    if not normalized:
        raise ValueError("each ingredient must be a non-empty string")
    return normalized


def build_prompt(
    selected_ingredients: Iterable[str],
    config: PromptBuilderConfig | None = None,
) -> str:
    """Build a creative generation prompt from selected ingredients.

    Args:
        selected_ingredients: Ordered iterable of ingredient names chosen by the user.
        config: PromptBuilderConfig that controls the voice of the prompt.

    Returns:
        str: A polished string that can be sent to an image generation model.

    Raises:
        ValueError: If ingredient validation fails or config creativity is outside [0, 1].
    """

    resolved_config = config or PromptBuilderConfig()

    if not 0 <= resolved_config.creativity <= 1:
        raise ValueError("creativity must be between 0 and 1")

    normalized: list[str] = []
    seen = set()

    for raw in selected_ingredients:
        if not raw or not raw.strip():
            raise ValueError("each ingredient must be a non-empty string")
        normalized_term = _normalize_ingredient(raw)
        if normalized_term in seen:
            continue
        seen.add(normalized_term)
        normalized.append(normalized_term)

    if len(normalized) < 2:
        raise ValueError("at least two unique ingredients are required")

    ingredient_phrase = ", ".join(normalized[:-1]) + f" and {normalized[-1]}"

    # Map creativity to descriptive words to influence prompt tone.
    if resolved_config.creativity < 0.3:
        tone = "balanced"
    elif resolved_config.creativity < 0.7:
        tone = "playful"
    else:
        tone = "adventurous"

    return (
        f"A {resolved_config.base_style} scene that artfully combines {ingredient_phrase}, "
        f"rendered with {tone} energy and {resolved_config.creativity:.2f} creativity."
    )

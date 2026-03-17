"""Prompt composition utilities for creative ingredient image generation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


def _normalize_ingredients(ingredients: Iterable[str]) -> list[str]:
    """Normalize ingredient names while preserving input order.

    Parameters:
        ingredients: Raw ingredient labels received from the UI or backend flow.

    Returns:
        list[str]: Cleaned, de-duplicated ingredient names in first-seen order.

    Raises:
        None.

    Example:
        >>> _normalize_ingredients([" Tomato ", "basil", "tomato"])
        ['tomato', 'basil']
    """

    normalized: list[str] = []
    seen: set[str] = set()

    for ingredient in ingredients:
        candidate = ingredient.strip().lower()
        if not candidate or candidate in seen:
            continue
        seen.add(candidate)
        normalized.append(candidate)

    return normalized


@dataclass(slots=True)
class PromptBuilderSettings:
    """Configure how creative image prompts are composed.

    Parameters:
        minimum_ingredients: Minimum number of unique ingredients required.
        visual_style: Art direction appended to the base prompt.
        scene_guidance: High-level composition hint for the generated scene.

    Returns:
        PromptBuilderSettings: Immutable prompt settings.

    Raises:
        None.

    Example:
        >>> PromptBuilderSettings()
        PromptBuilderSettings(...)
    """

    minimum_ingredients: int = 2
    visual_style: str = "editorial food photography with cinematic lighting"
    scene_guidance: str = "a cohesive dish concept that naturally connects the selected ingredients"


@dataclass(slots=True)
class IngredientPromptBuilder:
    """Create stable creative prompts from a list of selected ingredients.

    Parameters:
        settings: Prompt builder settings that tune validation and style.

    Returns:
        IngredientPromptBuilder: Builder ready to generate prompts.

    Raises:
        None.

    Example:
        >>> builder = IngredientPromptBuilder(PromptBuilderSettings())
        >>> builder.build_prompt(["tomato", "mozzarella"])
        'Create a visually rich food image...'
    """

    settings: PromptBuilderSettings

    def build_prompt(self, ingredients: Iterable[str]) -> str:
        """Build a generation prompt from the provided ingredients.

        Parameters:
            ingredients: Ingredient names selected by the user.

        Returns:
            str: A deterministic creative prompt for image generation.

        Raises:
            ValueError: If there are not enough unique ingredients to build a prompt.

        Example:
            >>> builder = IngredientPromptBuilder(PromptBuilderSettings())
            >>> builder.build_prompt(["tomato", "basil", "dough"])
            'Create a visually rich food image...'
        """

        normalized = _normalize_ingredients(ingredients)
        if len(normalized) < self.settings.minimum_ingredients:
            raise ValueError(
                "At least "
                f"{self.settings.minimum_ingredients} unique ingredients are required "
                "to generate an image."
            )

        if len(normalized) > 2:
            ingredient_phrase = ", ".join(normalized[:-1]) + f", and {normalized[-1]}"
        else:
            ingredient_phrase = " and ".join(normalized)

        # The prompt stays deterministic so later tests and product tuning stay stable.
        return (
            "Create a visually rich food image that combines "
            f"{ingredient_phrase} into {self.settings.scene_guidance}. "
            "The result should feel intentional, appetizing, and grounded in "
            f"{self.settings.visual_style}. "
            "Avoid text overlays, packaging, watermarks, and split-screen layouts."
        )


def build_default_prompt(ingredients: Iterable[str]) -> str:
    """Build a prompt with the default application settings.

    Parameters:
        ingredients: Ingredient names selected for generation.

    Returns:
        str: Prompt string ready for the image generation client.

    Raises:
        ValueError: If there are not enough unique ingredients.

    Example:
        >>> build_default_prompt(["tomato", "mozzarella"])
        'Create a visually rich food image...'
    """

    builder = IngredientPromptBuilder(settings=PromptBuilderSettings())
    return builder.build_prompt(ingredients)

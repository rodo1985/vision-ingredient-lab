"""Tests for creative ingredient prompt composition."""

from __future__ import annotations

import pytest

from backend.app.prompt_builder import build_default_prompt


def test_build_default_prompt_normalizes_and_deduplicates_ingredients() -> None:
    """Ensure prompt generation normalizes user input before composition.

    Parameters:
        None.

    Returns:
        None.

    Raises:
        None.
    """

    prompt = build_default_prompt([" Tomato ", "basil", "tomato", "mozzarella"])

    assert "tomato, basil, and mozzarella" in prompt


def test_build_default_prompt_requires_multiple_unique_ingredients() -> None:
    """Ensure prompt generation rejects insufficient ingredient selections.

    Parameters:
        None.

    Returns:
        None.

    Raises:
        None.
    """

    with pytest.raises(ValueError, match="At least 2 unique ingredients"):
        build_default_prompt(["tomato", " tomato "])

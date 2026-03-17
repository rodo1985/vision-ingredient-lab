"""Tests for prompt building behavior."""

from backend.app.services.prompt_builder import PromptBuilderConfig, build_prompt


def test_build_prompt_success() -> None:
    """Verify prompt construction includes style, ingredients, and tone."""

    config = PromptBuilderConfig(base_style="ethereal collage", creativity=0.7)
    prompt = build_prompt(["Tomato", "Basil ", "Mozzarella"], config)
    assert "ethereal collage" in prompt
    assert "tomato, basil and mozzarella" in prompt
    assert "adventurous" in prompt
    assert "0.70" in prompt


def test_build_prompt_dedup_and_normalize() -> None:
    """Verify normalization removes duplicates before prompt composition."""

    config = PromptBuilderConfig()
    prompt = build_prompt(["Tomato", "tomato ", "Basil"], config)
    assert "tomato and basil" in prompt


def test_build_prompt_creativity_bounds() -> None:
    """Verify out-of-range creativity values raise a clear validation error."""

    config = PromptBuilderConfig(creativity=1.1)
    try:
        build_prompt(["A", "B"], config)
        raise AssertionError("ValueError was not raised")
    except ValueError as exc:
        assert "creativity must be between 0 and 1" in str(exc)


def test_build_prompt_minimum_ingredients() -> None:
    """Verify at least two unique ingredients are required."""

    config = PromptBuilderConfig()
    try:
        build_prompt(["Tomato"], config)
        raise AssertionError("ValueError was not raised")
    except ValueError as exc:
        assert "at least two unique ingredients" in str(exc)


def test_build_prompt_disallows_empty_names() -> None:
    """Verify blank ingredient names are rejected before prompt composition."""

    config = PromptBuilderConfig()
    try:
        build_prompt(["Tomato", ""], config)
        raise AssertionError("ValueError was not raised")
    except ValueError as exc:
        assert "non-empty string" in str(exc)

"""Unit tests for backend configuration normalization."""

from app.core.config import OPENAI_DEFAULT_BASE_URL, Settings


def test_blank_openai_base_url_uses_default_sdk_behavior():
    """Blank base URLs should normalize to `None`."""

    settings = Settings(openai_base_url="")
    assert settings.openai_base_url is None


def test_resolved_openai_base_url_falls_back_to_default():
    """Resolved base URL should use the OpenAI default when no override is configured."""

    settings = Settings(openai_base_url="")
    assert settings.resolved_openai_base_url == OPENAI_DEFAULT_BASE_URL


def test_resolved_openai_base_url_uses_custom_override():
    """Resolved base URL should honor explicit custom endpoints."""

    custom_base_url = "https://example-proxy.local/v1"
    settings = Settings(openai_base_url=custom_base_url)
    assert settings.resolved_openai_base_url == custom_base_url

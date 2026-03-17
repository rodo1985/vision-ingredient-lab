"""Unit tests for local image encoding helpers."""

from app.services.metadata_extractor import encode_image_as_data_url


def test_encode_image_as_data_url_uses_supported_prefix(tmp_path):
    """Local images should be converted into Base64 data URLs."""

    image_path = tmp_path / "ingredient.png"
    image_path.write_bytes(b"png-bytes")
    data_url = encode_image_as_data_url(image_path)
    assert data_url.startswith("data:image/png;base64,")

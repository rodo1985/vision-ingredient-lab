"""Unit tests for metadata extraction parsing."""

from app.services.metadata_extractor import parse_extracted_metadata


def test_parse_extracted_metadata_returns_normalized_values():
    """Parser should normalize tags and keep the description intact."""

    payload = '{"description":"Fresh basil leaves in a close-up shot.","tags":["Basil"," green ","basil"]}'
    result = parse_extracted_metadata(payload)
    assert result.description == "Fresh basil leaves in a close-up shot."
    assert result.tags == ["basil", "green"]

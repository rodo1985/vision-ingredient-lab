"""Tests for the primary scanner implementation."""

from datetime import datetime, timezone

import pytest

from backend.app.services.scanner import scan_image_folder


def test_scan_finds_supported_images(tmp_path) -> None:
    """Ensure supported image files are returned with proper metadata.

    Parameters:
        tmp_path: Pytest temporary directory fixture.

    Returns:
        None

    Raises:
        AssertionError: If supported images are not discovered with UTC timestamps.
    """

    jpg = tmp_path / "tomato.jpg"
    png = tmp_path / "subdir" / "basil.PNG"
    png.parent.mkdir()
    jpg.write_bytes(b"tomato")
    png.write_bytes(b"basil")

    records = scan_image_folder(tmp_path)
    # Both files should be discovered, but non-image files do not exist here.
    assert len(records) == 2
    filenames = {record.filename for record in records}
    assert filenames == {"tomato.jpg", "basil.PNG"}
    assert all(isinstance(record.last_modified, datetime) for record in records)
    # Metadata timestamps must include UTC timezone information.
    assert all(record.last_modified.tzinfo is timezone.utc for record in records)


def test_scan_is_deterministic_by_filepath(tmp_path) -> None:
    """Verify that sorting by filepath yields deterministic record ordering.

    Parameters:
        tmp_path: Pytest temporary directory fixture.

    Returns:
        None

    Raises:
        AssertionError: If files are not returned in stable sorted order.
    """

    higher = tmp_path / "zzz.png"
    lower = tmp_path / "aaa.png"
    higher.write_bytes(b"high")
    lower.write_bytes(b"low")

    records = scan_image_folder(tmp_path)
    assert records[0].filename == "aaa.png"
    assert records[1].filename == "zzz.png"


def test_scan_raises_for_invalid_directory(tmp_path) -> None:
    """Confirm that scanning a non-existent path raises a `ValueError`.

    Parameters:
        tmp_path: Pytest temporary directory fixture.

    Returns:
        None

    Raises:
        AssertionError: If invalid paths do not produce the expected exception.
    """

    missing = tmp_path / "nope"
    with pytest.raises(ValueError):
        scan_image_folder(missing)

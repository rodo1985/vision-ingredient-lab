"""Unit tests for the image scanner service."""

from pathlib import Path

from backend.ingestion.scanner import ImageFileRecord, ImageScanner


def test_scan_empty_directory(tmp_path: Path) -> None:
    """Ensure an empty folder yields no image records.

    Parameters:
        tmp_path: Temporary directory fixture.

    Returns:
        None.

    Raises:
        None.
    """

    scanner = ImageScanner()
    assert scanner.scan_folder(tmp_path) == []


def test_scan_filters_unsupported_files(tmp_path: Path) -> None:
    """Ensure unsupported file extensions are ignored during scans.

    Parameters:
        tmp_path: Temporary directory fixture.

    Returns:
        None.

    Raises:
        None.
    """

    unsupported = tmp_path / "document.txt"
    unsupported.write_text("not an image")

    scanner = ImageScanner()
    assert scanner.scan_folder(tmp_path) == []


def test_scan_recursive_nested_files(tmp_path: Path) -> None:
    """Ensure supported nested files are discovered recursively.

    Parameters:
        tmp_path: Temporary directory fixture.

    Returns:
        None.

    Raises:
        None.
    """

    nested = tmp_path / "level1" / "level2"
    nested.mkdir(parents=True)
    image = nested / "tomato.png"
    image.write_text("fake image")

    scanner = ImageScanner()
    records = scanner.scan_folder(tmp_path)

    assert records == [
        ImageFileRecord(
            filename="tomato.png",
            filepath=str(image.resolve()),
            last_modified=image.stat().st_mtime,
        )
    ]


def test_scan_deterministic_order(tmp_path: Path) -> None:
    """Ensure scan results are sorted consistently by filepath.

    Parameters:
        tmp_path: Temporary directory fixture.

    Returns:
        None.

    Raises:
        None.
    """

    # Create files in a different creation order than absolute path sorting.
    (tmp_path / "b.png").write_text("b")
    (tmp_path / "a.png").write_text("a")

    scanner = ImageScanner()
    results = scanner.scan_folder(tmp_path)

    assert [record.filename for record in results] == ["a.png", "b.png"]

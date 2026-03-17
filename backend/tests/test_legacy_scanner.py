"""Tests for the preserved legacy image scanner."""

from pathlib import Path

from backend.ingestion.scanner import ImageFileRecord, ImageScanner


def test_legacy_scan_empty_directory(tmp_path: Path) -> None:
    """Ensure an empty folder yields no image records."""

    scanner = ImageScanner()
    assert scanner.scan_folder(tmp_path) == []


def test_legacy_scan_filters_unsupported_files(tmp_path: Path) -> None:
    """Ensure unsupported file extensions are ignored during scans."""

    unsupported = tmp_path / "document.txt"
    unsupported.write_text("not an image")

    scanner = ImageScanner()
    assert scanner.scan_folder(tmp_path) == []


def test_legacy_scan_recursive_nested_files(tmp_path: Path) -> None:
    """Ensure supported nested files are discovered recursively."""

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


def test_legacy_scan_deterministic_order(tmp_path: Path) -> None:
    """Ensure scan results are sorted consistently by filepath."""

    (tmp_path / "b.png").write_text("b")
    (tmp_path / "a.png").write_text("a")

    scanner = ImageScanner()
    results = scanner.scan_folder(tmp_path)

    assert [record.filename for record in results] == ["a.png", "b.png"]

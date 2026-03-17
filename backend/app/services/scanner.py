"""Dataset scanning helpers for ingredient image ingestion."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence

from backend.app.models.metadata import ImageFileRecord

DEFAULT_IMAGE_EXTENSIONS: Sequence[str] = (
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".bmp",
    ".webp",
    ".tiff",
)


def scan_image_folder(
    root: Path, supported_extensions: Iterable[str] | None = None
) -> list[ImageFileRecord]:
    """Recursively scan a directory tree for supported image files.

    Parameters:
        root: Root directory to scan for ingredient images.
        supported_extensions: Optional override for the file extensions to accept.

    Returns:
        list[ImageFileRecord]: Sorted image records for each supported file.

    Raises:
        ValueError: If `root` does not exist or is not a directory.

    Example:
        >>> scan_image_folder(Path("/data/ingredients"))
    """
    if not root.exists():
        raise ValueError(f"Scan path does not exist: {root}")
    if not root.is_dir():
        raise ValueError(f"Scan path is not a directory: {root}")

    extensions = {ext.lower() for ext in (supported_extensions or DEFAULT_IMAGE_EXTENSIONS)}
    found_files = [
        path
        for path in root.rglob("*")
        if _is_supported_image(path, extensions)
    ]

    # Sort by absolute filepath to guarantee deterministic results regardless of OS traversal order.
    found_files.sort(key=lambda path: str(path.resolve()))
    return [ImageFileRecord.from_path(path) for path in found_files]


def _is_supported_image(path: Path, extensions: set[str]) -> bool:
    """Return whether a path points to a supported image file.

    Parameters:
        path: Candidate filesystem path.
        extensions: Lowercase extensions that are considered images.

    Returns:
        bool: True when the path is a file using one of the allowed extensions.

    Raises:
        None.
    """

    if not path.is_file():
        return False
    return path.suffix.lower() in extensions

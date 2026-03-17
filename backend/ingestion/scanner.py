"""Helper module to scan ingredient image datasets."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

SUPPORTED_EXTENSIONS: set[str] = {".gif", ".jpeg", ".jpg", ".png", ".webp"}


@dataclass(frozen=True, slots=True)
class ImageFileRecord:
    """Represent a single image file discovered in the local dataset.

    Parameters:
        filename: File name of the image.
        filepath: Absolute path to the image file.
        last_modified: File modification timestamp expressed as epoch seconds.

    Returns:
        ImageFileRecord: Immutable file record for downstream ingestion steps.

    Raises:
        None.

    Example:
        >>> ImageFileRecord("tomato.png", "/tmp/tomato.png", 123.0)
        ImageFileRecord(filename='tomato.png', filepath='/tmp/tomato.png', last_modified=123.0)
    """

    filename: str
    filepath: str
    last_modified: float


class ImageScanner:
    """Walk a folder tree and return deterministic metadata for supported images.

    Parameters:
        supported_extensions: Optional iterable of lowercase or mixed-case file extensions.

    Returns:
        ImageScanner: Scanner configured for the selected set of file extensions.

    Raises:
        None.

    Example:
        >>> scanner = ImageScanner()
        >>> scanner.scan_folder(Path("data/images"))
        []
    """

    def __init__(self, supported_extensions: Iterable[str] | None = None) -> None:
        """Initialize the scanner with an optional extension override.

        Parameters:
            supported_extensions: Iterable of extensions, each including a leading dot.

        Returns:
            None.

        Raises:
            None.

        Example:
            >>> ImageScanner({'.png', '.jpg'})
            <...ImageScanner object...>
        """

        self._extensions = {
            extension.lower()
            for extension in (supported_extensions or SUPPORTED_EXTENSIONS)
        }

    def scan_folder(self, root: Path) -> list[ImageFileRecord]:
        """Scan a directory recursively and return deterministic image file records.

        Parameters:
            root: Directory to search for supported image files.

        Returns:
            list[ImageFileRecord]: Sorted records for all supported files under `root`.

        Raises:
            None.

        Example:
            >>> ImageScanner().scan_folder(Path("data/images"))
            []
        """

        if not root.exists():
            # Missing directories behave like empty datasets so startup remains idempotent.
            return []

        records: list[ImageFileRecord] = []
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            if not self._is_supported_extension(path.suffix):
                continue

            records.append(
                ImageFileRecord(
                    filename=path.name,
                    filepath=str(path.resolve()),
                    last_modified=path.stat().st_mtime,
                )
            )

        # Sorting by resolved path prevents platform-specific directory iteration differences.
        records.sort(key=lambda record: record.filepath)
        return records

    def _is_supported_extension(self, extension: str) -> bool:
        """Return whether a file extension is accepted by the scanner.

        Parameters:
            extension: File extension including its leading dot.

        Returns:
            bool: `True` when the extension is supported, otherwise `False`.

        Raises:
            None.

        Example:
            >>> ImageScanner()._is_supported_extension('.png')
            True
        """

        return extension.lower() in self._extensions

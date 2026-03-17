"""Startup synchronization helpers for Vision Ingredient Lab."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from backend.ingestion.scanner import ImageFileRecord, ImageScanner
from backend.metadata_repository import CsvMetadataRepository, MetadataRow


@dataclass(slots=True)
class StartupSyncService:
    """Determine which dataset images still need metadata enrichment.

    Parameters:
        scanner: ImageScanner used to enumerate files on disk.
        repository: CsvMetadataRepository storing enriched metadata.
        compare_keys: Tuple of metadata attributes used for equivalence.

    Returns:
        StartupSyncService: Configured service ready to detect new files.

    Raises:
        None.

    Example:
        >>> service = StartupSyncService(ImageScanner(), CsvMetadataRepository("meta.csv"))
        >>> service.detect_new_files(Path("images"))
        []
    """

    scanner: ImageScanner
    repository: CsvMetadataRepository
    compare_keys: tuple[str, ...] = ("filepath",)

    def detect_new_files(
        self,
        root: str | Path | Sequence[str | Path] | Iterable[str | Path],
    ) -> list[ImageFileRecord]:
        """Return image records that lack persisted metadata entries.

        Parameters:
            root: Directory path or iterable of paths to scan for images.

        Returns:
            list[ImageFileRecord]: Deterministic list of images where metadata is absent.

        Raises:
            None.

        Example:
            >>> service.detect_new_files("data/images")
            []
        """

        if isinstance(root, (str, Path)):
            directories = [root]
        else:
            directories = list(root)

        existing_rows = self.repository.read_all()
        scanned_records: list[ImageFileRecord] = []

        for directory in directories:
            path = Path(directory)
            scanned_records.extend(self.scanner.scan_folder(path))

        return self.identify_new_files(scanned_records, existing_rows)

    def identify_new_files(
        self,
        scanned_files: Sequence[ImageFileRecord],
        existing_metadata: Sequence[MetadataRow],
    ) -> list[ImageFileRecord]:
        """Return only scanned files that do not yet exist in persisted metadata.

        Parameters:
            scanned_files: File records produced by the image scanner.
            existing_metadata: Persisted rows already stored in the repository.

        Returns:
            list[ImageFileRecord]: Deterministic list of files that still need enrichment.

        Raises:
            None.

        Example:
            >>> service.identify_new_files([], [])
            []
        """

        seen = {self._row_key(row) for row in existing_metadata}
        missing = [
            record for record in scanned_files if self._record_key(record) not in seen
        ]
        missing.sort(key=lambda record: record.filepath)
        return missing

    def _row_key(self, row: MetadataRow) -> tuple[str, ...]:
        """Compute a canonical key for metadata rows using configured attributes.

        Parameters:
            row: Persisted metadata row to normalize.

        Returns:
            tuple[str, ...]: Comparable key for de-duplication decisions.

        Raises:
            AttributeError: If a configured comparison key does not exist on the row.
        """

        return tuple(getattr(row, attribute) for attribute in self.compare_keys)

    def _record_key(self, record: ImageFileRecord) -> tuple[str, ...]:
        """Compute a canonical key for image records using configured attributes.

        Parameters:
            record: Scanned file record to normalize.

        Returns:
            tuple[str, ...]: Comparable key for de-duplication decisions.

        Raises:
            AttributeError: If a configured comparison key does not exist on the record.
        """

        return tuple(getattr(record, attribute) for attribute in self.compare_keys)

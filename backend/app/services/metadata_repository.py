"""CSV-backed metadata repository for Vision Ingredient Lab."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, List

from backend.app.models.metadata import MetadataRecord


class MetadataCSVRepository:
    """Manage CSV persistence, read, append, and update operations for metadata.

    Parameters:
        csv_path: Path to the metadata CSV file.

    Returns:
        MetadataCSVRepository: Repository instance ready for file-backed operations.

    Raises:
        OSError: If the repository cannot create parent directories or files.

    Example:
        >>> repo = MetadataCSVRepository(Path("data/metadata.csv"))
        >>> repo.load_all()
        []
    """

    def __init__(self, csv_path: Path) -> None:
        """Initialize the repository and ensure the CSV exists with headers.

        Parameters:
            csv_path: Location where metadata CSV should live.

        Returns:
            None

        Raises:
            OSError: If the CSV directory or file cannot be created.
        """

        self.csv_path = Path(csv_path)
        self.headers = MetadataRecord.HEADER_ORDER
        self._ensure_csv()

    def _ensure_csv(self) -> None:
        """Create the CSV file and parent directories if they do not exist.

        Parameters:
            None.

        Returns:
            None

        Raises:
            OSError: If the repository cannot create the backing file.
        """

        if not self.csv_path.exists():
            self.csv_path.parent.mkdir(parents=True, exist_ok=True)
            with self.csv_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=self.headers)
                writer.writeheader()

    def load_all(self) -> List[MetadataRecord]:
        """Read all metadata entries already stored in the CSV file.

        Parameters:
            None.

        Returns:
            List[MetadataRecord]: Stored records in on-disk order.

        Raises:
            ValueError: If a CSV row contains malformed metadata.
            OSError: If the CSV file cannot be read.
        """

        self._ensure_csv()
        records: List[MetadataRecord] = []
        with self.csv_path.open("r", newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row.get("filepath"):
                    # Skip malformed rows without a filepath so downstream logic
                    # stays deterministic.
                    continue
                records.append(MetadataRecord.from_csv_row(row))
        return records

    def append_records(self, new_records: Iterable[MetadataRecord]) -> int:
        """Append metadata records that do not yet exist, protecting by filepath.

        Parameters:
            new_records: Iterable of records to append.

        Returns:
            int: Number of records actually appended.

        Raises:
            OSError: If the CSV file cannot be written.
        """

        existing = {record.filepath for record in self.load_all()}
        to_append = [record for record in new_records if record.filepath not in existing]
        if not to_append:
            return 0

        with self.csv_path.open("a", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=self.headers)
            for record in to_append:
                writer.writerow(record.to_csv_row())
        return len(to_append)

    def upsert_record(self, record: MetadataRecord) -> None:
        """Insert or update a single record, rewriting the CSV to keep order stable.

        Parameters:
            record: Metadata record to insert or replace.

        Returns:
            None

        Raises:
            OSError: If the CSV file cannot be rewritten.
        """

        records = self.load_all()
        replaced = False
        for idx, existing in enumerate(records):
            if existing.filepath == record.filepath:
                records[idx] = record
                replaced = True
                break
        if not replaced:
            records.append(record)
        self._rewrite(records)

    def _rewrite(self, records: List[MetadataRecord]) -> None:
        """Overwrite the CSV file with the provided records in order.

        Parameters:
            records: Fully materialized list of rows to write back to disk.

        Returns:
            None

        Raises:
            OSError: If the CSV file cannot be rewritten.
        """

        with self.csv_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=self.headers)
            writer.writeheader()
            for record in records:
                writer.writerow(record.to_csv_row())

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


_CSV_HEADERS = [
    "filename",
    "filepath",
    "description",
    "keywords",
    "processed_at",
    "last_modified",
]


@dataclass
class MetadataRow:
    """Represent a single persisted metadata record.

    Parameters:
        filename: Source image file name.
        filepath: Absolute or repo-relative image path.
        description: Natural-language description generated for the image.
        keywords: Search tags associated with the image.
        processed_at: Timestamp describing when enrichment completed.
        last_modified: Source file modification timestamp captured during ingestion.

    Returns:
        MetadataRow: Serializable metadata row.

    Raises:
        None.

    Example:
        >>> MetadataRow("tomato.png", "/tmp/tomato.png", "red tomato", ["tomato"], "now", "later")
        MetadataRow(filename='tomato.png', filepath='/tmp/tomato.png', description='red tomato', keywords=['tomato'], processed_at='now', last_modified='later')
    """

    filename: str
    filepath: str
    description: str
    keywords: list[str]
    processed_at: str
    last_modified: str


class CsvMetadataRepository:
    """Persist ingredient metadata in a CSV file with stable schema handling.

    Parameters:
        csv_path: Filesystem path where metadata should be stored.

    Returns:
        CsvMetadataRepository: Repository instance bound to a single CSV path.

    Raises:
        None.

    Example:
        >>> CsvMetadataRepository(Path("data/metadata.csv"))
        <...CsvMetadataRepository object...>
    """

    def __init__(self, csv_path: Path | str) -> None:
        """Initialize the repository with a target CSV path.

        Parameters:
            csv_path: Filesystem path where metadata should be stored.

        Returns:
            None.

        Raises:
            None.

        Example:
            >>> CsvMetadataRepository("data/metadata.csv")
            <...CsvMetadataRepository object...>
        """
        self._path = Path(csv_path)

    def initialize(self) -> None:
        """Ensure the CSV file exists with the required schema header.

        Parameters:
            None.

        Returns:
            None.

        Raises:
            OSError: If the target directory or file cannot be created.

        Example:
            >>> repo = CsvMetadataRepository("data/metadata.csv")
            >>> repo.initialize()
        """

        if not self._path.exists():
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with self._path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(_CSV_HEADERS)

    def read_all(self) -> list[MetadataRow]:
        """Read all metadata rows from the CSV in deterministic filepath order.

        Parameters:
            None.

        Returns:
            list[MetadataRow]: All persisted metadata rows.

        Raises:
            OSError: If the CSV file cannot be read.

        Example:
            >>> CsvMetadataRepository("data/metadata.csv").read_all()
            []
        """

        self.initialize()
        rows: list[MetadataRow] = []
        with self._path.open("r", newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for entry in reader:
                keywords = self._deserialize_keywords(entry.get("keywords", ""))
                rows.append(
                    MetadataRow(
                        filename=entry["filename"],
                        filepath=entry["filepath"],
                        description=entry["description"],
                        keywords=keywords,
                        processed_at=entry["processed_at"],
                        last_modified=entry["last_modified"],
                    )
                )
        rows.sort(key=lambda row: row.filepath)
        return rows

    def append(self, row: MetadataRow) -> None:
        """Append or update a metadata row while enforcing filepath uniqueness.

        Parameters:
            row: Metadata row to append or upsert.

        Returns:
            None.

        Raises:
            OSError: If the CSV cannot be written.

        Example:
            >>> repo = CsvMetadataRepository("data/metadata.csv")
            >>> repo.append(MetadataRow("a.png", "/tmp/a.png", "desc", ["a"], "now", "now"))
        """

        existing = self.read_all()
        filtered = [r for r in existing if r.filepath != row.filepath]
        filtered.append(row)
        filtered.sort(key=lambda item: item.filepath)
        self._write_rows(filtered)

    def _write_rows(self, rows: Iterable[MetadataRow]) -> None:
        """Overwrite the CSV with the provided rows.

        Parameters:
            rows: Sequence of metadata rows to persist.

        Returns:
            None.

        Raises:
            OSError: If the CSV cannot be written.

        Example:
            >>> repo = CsvMetadataRepository("data/metadata.csv")
            >>> repo._write_rows([])
        """
        with self._path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(_CSV_HEADERS)
            for row in rows:
                writer.writerow(
                    [
                        row.filename,
                        row.filepath,
                        row.description,
                        self._serialize_keywords(row.keywords),
                        row.processed_at,
                        row.last_modified,
                    ]
                )

    @staticmethod
    def _serialize_keywords(keywords: list[str]) -> str:
        """Convert a keyword list into a JSON string for CSV storage.

        Parameters:
            keywords: Ordered keyword list to serialize.

        Returns:
            str: JSON string representation of the keyword list.

        Raises:
            TypeError: If the provided keywords cannot be serialized.

        Example:
            >>> CsvMetadataRepository._serialize_keywords(["tomato"])
            '["tomato"]'
        """

        return json.dumps(keywords, ensure_ascii=False)

    @staticmethod
    def _deserialize_keywords(raw: str | None) -> list[str]:
        """Turn a stored JSON string back into a keyword list.

        Parameters:
            raw: Stored JSON string or empty value from the CSV.

        Returns:
            list[str]: Parsed keyword list or an empty list on malformed data.

        Raises:
            None.

        Example:
            >>> CsvMetadataRepository._deserialize_keywords('[\"tomato\"]')
            ['tomato']
        """

        if not raw:
            return []
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            return []
        if isinstance(parsed, list):
            return [str(item) for item in parsed]
        return []

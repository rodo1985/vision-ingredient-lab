"""CSV-backed repository for canonical image metadata."""

from __future__ import annotations

import csv
from datetime import UTC, datetime
from pathlib import Path

from app.models.domain import ImageMetadataRecord

CSV_FIELDS = [
    "image_id",
    "filename",
    "filepath",
    "file_url",
    "mime_type",
    "description",
    "tags",
    "search_text",
    "processed_at",
    "last_modified",
    "embedding_version",
    "model_version",
    "status",
    "error_message",
]


class MetadataStore:
    """Persist and load metadata records from a CSV file.

    Args:
        csv_path: Destination path for the metadata CSV.

    Returns:
        MetadataStore: Repository instance.
    """

    def __init__(self, csv_path: Path) -> None:
        """Initialize the metadata store.

        Args:
            csv_path: Destination path for the metadata CSV.

        Returns:
            None
        """

        self.csv_path = csv_path

    def load_all(self) -> list[ImageMetadataRecord]:
        """Load every metadata row from disk.

        Returns:
            list[ImageMetadataRecord]: Parsed metadata records.

        Raises:
            ValueError: Raised if the CSV contains invalid data.
        """

        if not self.csv_path.exists():
            return []

        with self.csv_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            records = []
            for row in reader:
                records.append(
                    ImageMetadataRecord(
                        image_id=row["image_id"],
                        filename=row["filename"],
                        filepath=row["filepath"],
                        file_url=row["file_url"],
                        mime_type=row["mime_type"],
                        description=row["description"],
                        tags=[tag for tag in row["tags"].split("|") if tag],
                        search_text=row["search_text"],
                        processed_at=datetime.fromisoformat(row["processed_at"]),
                        last_modified=datetime.fromisoformat(row["last_modified"]),
                        embedding_version=row["embedding_version"],
                        model_version=row["model_version"],
                        status=row["status"],
                        error_message=row["error_message"],
                    )
                )
            return records

    def save_all(self, records: list[ImageMetadataRecord]) -> None:
        """Write every metadata record to disk.

        Args:
            records: Records to persist.

        Returns:
            None
        """

        self.csv_path.parent.mkdir(parents=True, exist_ok=True)
        with self.csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
            writer.writeheader()
            for record in records:
                writer.writerow(
                    {
                        "image_id": record.image_id,
                        "filename": record.filename,
                        "filepath": record.filepath,
                        "file_url": record.file_url,
                        "mime_type": record.mime_type,
                        "description": record.description,
                        "tags": "|".join(record.tags),
                        "search_text": record.search_text,
                        "processed_at": record.processed_at.astimezone(UTC).isoformat(),
                        "last_modified": record.last_modified.astimezone(UTC).isoformat(),
                        "embedding_version": record.embedding_version,
                        "model_version": record.model_version,
                        "status": record.status,
                        "error_message": record.error_message,
                    }
                )

    def get_by_id(self, image_id: str) -> ImageMetadataRecord | None:
        """Return one metadata record by image identifier.

        Args:
            image_id: Stable image identifier.

        Returns:
            ImageMetadataRecord | None: Matching record or `None`.
        """

        return next((record for record in self.load_all() if record.image_id == image_id), None)

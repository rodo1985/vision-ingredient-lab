"""JSONL-backed repository for derived embedding records."""

from __future__ import annotations

import json
from pathlib import Path

from app.models.domain import EmbeddingRecord


class EmbeddingStore:
    """Persist and load embedding records from a JSONL file.

    Args:
        file_path: Destination path for the JSONL sidecar.

    Returns:
        EmbeddingStore: Repository instance.
    """

    def __init__(self, file_path: Path) -> None:
        """Initialize the embedding store.

        Args:
            file_path: Destination path for the JSONL sidecar.

        Returns:
            None
        """

        self.file_path = file_path

    def load_all(self) -> list[EmbeddingRecord]:
        """Load all embedding records from disk.

        Returns:
            list[EmbeddingRecord]: Parsed embedding records.
        """

        if not self.file_path.exists():
            return []

        records: list[EmbeddingRecord] = []
        with self.file_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                records.append(EmbeddingRecord.model_validate_json(line))
        return records

    def save_all(self, records: list[EmbeddingRecord]) -> None:
        """Write all embedding records to disk.

        Args:
            records: Records to persist.

        Returns:
            None
        """

        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with self.file_path.open("w", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record.model_dump(mode="json")) + "\n")

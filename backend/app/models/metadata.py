"""Shared metadata models for image ingestion and persistence."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


def _normalize_keyword(keyword: str) -> str:
    """Normalize a keyword while preserving its original letter casing.

    Parameters:
        keyword: Raw keyword value from a model response or test input.

    Returns:
        str: A trimmed keyword with collapsed internal whitespace.

    Raises:
        ValueError: If the provided keyword is empty after trimming.

    Example:
        >>> _normalize_keyword("  pizza   dough ")
        'pizza dough'
    """

    normalized = " ".join(part.strip() for part in keyword.split())
    if not normalized:
        raise ValueError("keyword must contain at least one non-whitespace character")
    return normalized


def serialize_keywords(keywords: Iterable[str]) -> str:
    """Serialize keywords into a deterministic JSON array string.

    Parameters:
        keywords: Keyword values that may include duplicates or blank entries.

    Returns:
        str: A JSON string containing sorted, unique keyword values.

    Raises:
        TypeError: If a non-string keyword is provided.

    Example:
        >>> serialize_keywords(["basil", "Tomato", "basil"])
        '["Tomato", "basil"]'
    """

    normalized_keywords: dict[str, str] = {}
    for keyword in keywords:
        if not isinstance(keyword, str):
            raise TypeError("keywords must be strings")
        collapsed = " ".join(part.strip() for part in keyword.split())
        if not collapsed:
            continue

        # Use a lowercase key for deduplication so search behavior stays stable
        # even when the model varies the casing of ingredient names.
        dedupe_key = collapsed.lower()
        if dedupe_key not in normalized_keywords:
            normalized_keywords[dedupe_key] = collapsed

    sorted_keywords = sorted(normalized_keywords.values())
    return json.dumps(sorted_keywords, ensure_ascii=True)


def deserialize_keywords(serialized_keywords: str) -> list[str]:
    """Deserialize keywords from the repository's JSON string representation.

    Parameters:
        serialized_keywords: JSON array string stored in the CSV file.

    Returns:
        list[str]: Parsed keyword values in stored order.

    Raises:
        ValueError: If the stored value is not a JSON list of strings.

    Example:
        >>> deserialize_keywords('["tomato", "basil"]')
        ['tomato', 'basil']
    """

    loaded = json.loads(serialized_keywords or "[]")
    if not isinstance(loaded, list) or not all(isinstance(item, str) for item in loaded):
        raise ValueError("serialized_keywords must decode to a list of strings")
    return loaded


@dataclass(frozen=True)
class ImageFileRecord:
    """Represent a single image file discovered in the dataset directory.

    Parameters:
        filename: Image file name including the extension.
        filepath: Absolute path to the image file.
        last_modified: Last modified timestamp in UTC.

    Returns:
        ImageFileRecord: Dataclass instance describing the image file.

    Raises:
        OSError: When `from_path` cannot read file metadata from disk.

    Example:
        >>> record = ImageFileRecord.from_path(Path("pizza.jpg"))
        >>> record.filename
        'pizza.jpg'
    """

    filename: str
    filepath: str
    last_modified: datetime

    @staticmethod
    def from_path(path: Path) -> "ImageFileRecord":
        """Build an image record directly from a filesystem path.

        Parameters:
            path: Path to an image file on disk.

        Returns:
            ImageFileRecord: File metadata normalized for backend services.

        Raises:
            OSError: If the file metadata cannot be read.

        Example:
            >>> ImageFileRecord.from_path(Path("/tmp/pizza.jpg"))
        """

        stat = path.stat()
        last_modified = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
        return ImageFileRecord(
            filename=path.name,
            filepath=str(path.resolve()),
            last_modified=last_modified,
        )


@dataclass(frozen=True)
class MetadataRecord:
    """Represent an enriched metadata row stored in the CSV repository.

    Parameters:
        filename: Image file name including extension.
        filepath: File path used as the repository's deduplication key.
        description: AI-generated description of the image contents.
        keywords: Ingredient-related keywords extracted from the image.
        processed_at: UTC timestamp recording when enrichment completed.
        last_modified: UTC timestamp reflecting the image file's latest change.

    Returns:
        MetadataRecord: Dataclass instance ready for service or repository use.

    Raises:
        ValueError: When deserialization encounters malformed timestamp data.

    Example:
        >>> record = MetadataRecord(
        ...     filename="pizza.jpg",
        ...     filepath="/tmp/pizza.jpg",
        ...     description="Fresh basil on pizza dough",
        ...     keywords=["basil", "dough"],
        ...     processed_at=datetime.now(timezone.utc),
        ...     last_modified=datetime.now(timezone.utc),
        ... )
    """

    HEADER_ORDER = [
        "filename",
        "filepath",
        "description",
        "keywords",
        "processed_at",
        "last_modified",
    ]

    filename: str
    filepath: str
    description: str
    keywords: list[str]
    processed_at: datetime
    last_modified: datetime

    def to_csv_row(self) -> dict[str, str]:
        """Convert the record to a CSV-friendly dictionary.

        Parameters:
            None.

        Returns:
            dict[str, str]: Serialized row values in repository column format.

        Raises:
            ValueError: If any keyword contains only whitespace.

        Example:
            >>> row = MetadataRecord(
            ...     filename="pizza.jpg",
            ...     filepath="/tmp/pizza.jpg",
            ...     description="desc",
            ...     keywords=["basil"],
            ...     processed_at=datetime.now(timezone.utc),
            ...     last_modified=datetime.now(timezone.utc),
            ... ).to_csv_row()
        """

        cleaned_keywords = [_normalize_keyword(keyword) for keyword in self.keywords]
        return {
            "filename": self.filename,
            "filepath": self.filepath,
            "description": self.description,
            "keywords": serialize_keywords(cleaned_keywords),
            "processed_at": self.processed_at.isoformat(),
            "last_modified": self.last_modified.isoformat(),
        }

    @classmethod
    def from_csv_row(cls, row: dict[str, str]) -> "MetadataRecord":
        """Create a metadata record from a CSV row dictionary.

        Parameters:
            row: Raw CSV row keyed by repository header names.

        Returns:
            MetadataRecord: Parsed metadata record instance.

        Raises:
            ValueError: If timestamp fields cannot be parsed.

        Example:
            >>> MetadataRecord.from_csv_row({
            ...     "filename": "pizza.jpg",
            ...     "filepath": "/tmp/pizza.jpg",
            ...     "description": "desc",
            ...     "keywords": "[\"basil\"]",
            ...     "processed_at": "2024-01-01T00:00:00+00:00",
            ...     "last_modified": "2024-01-01T00:00:00+00:00",
            ... })
        """

        return cls(
            filename=row["filename"],
            filepath=row["filepath"],
            description=row["description"],
            keywords=deserialize_keywords(row.get("keywords", "[]")),
            processed_at=datetime.fromisoformat(row["processed_at"]),
            last_modified=datetime.fromisoformat(row["last_modified"]),
        )

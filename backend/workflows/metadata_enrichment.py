"""Workflow for enriching newly discovered ingredient images with metadata."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable, Protocol, Sequence

from backend.ingestion.scanner import ImageFileRecord
from backend.metadata_repository import MetadataRow


def _default_timestamp_factory() -> str:
    """Return an ISO timestamp for metadata processing events.

    Parameters:
        None.

    Returns:
        str: Current UTC timestamp in ISO 8601 format.

    Raises:
        None.

    Example:
        >>> timestamp = _default_timestamp_factory()
        >>> "T" in timestamp
        True
    """

    return datetime.now(UTC).isoformat()


class SupportsImageScanner(Protocol):
    """Describe the image scanner interface required by the enrichment workflow.

    Parameters:
        None.

    Returns:
        SupportsImageScanner: Protocol for static type-checking only.

    Raises:
        None.
    """

    def scan_folder(self, root: Path) -> list[ImageFileRecord]:
        """Scan a folder and return discovered image files."""


class SupportsMetadataRepository(Protocol):
    """Describe the metadata repository interface required by the workflow.

    Parameters:
        None.

    Returns:
        SupportsMetadataRepository: Protocol for static type-checking only.

    Raises:
        None.
    """

    def read_all(self) -> list[MetadataRow]:
        """Return all persisted metadata rows."""

    def append(self, row: MetadataRow) -> None:
        """Persist or update a metadata row."""


class SupportsVisionMetadata(Protocol):
    """Describe the minimum metadata shape returned by a vision client.

    Parameters:
        None.

    Returns:
        SupportsVisionMetadata: Protocol for static type-checking only.

    Raises:
        None.
    """

    description: str
    keywords: Sequence[str]


class SupportsVisionClient(Protocol):
    """Describe the vision client interface required by the workflow.

    Parameters:
        None.

    Returns:
        SupportsVisionClient: Protocol for static type-checking only.

    Raises:
        None.
    """

    def analyze_image(self, image_path: Path) -> SupportsVisionMetadata:
        """Analyze an image and return normalized description and keywords."""


class SupportsStartupSync(Protocol):
    """Describe the startup sync interface required by the enrichment workflow.

    Parameters:
        None.

    Returns:
        SupportsStartupSync: Protocol for static type-checking only.

    Raises:
        None.
    """

    def identify_new_files(
        self,
        scanned_files: Sequence[ImageFileRecord],
        existing_metadata: Sequence[MetadataRow],
    ) -> list[ImageFileRecord]:
        """Return only files that are not yet represented in persisted metadata."""


@dataclass(slots=True)
class MetadataEnrichmentResult:
    """Summarize a single metadata enrichment run.

    Parameters:
        scanned_count: Total number of image files discovered by the scanner.
        new_file_count: Number of files identified as new by startup sync.
        processed_rows: Metadata rows appended during this run.

    Returns:
        MetadataEnrichmentResult: Immutable summary of the enrichment pass.

    Raises:
        None.

    Example:
        >>> MetadataEnrichmentResult(3, 1, [])
        MetadataEnrichmentResult(scanned_count=3, new_file_count=1, processed_rows=[])
    """

    scanned_count: int
    new_file_count: int
    processed_rows: list[MetadataRow]


@dataclass(slots=True)
class MetadataEnrichmentPipeline:
    """Orchestrate startup scanning, new-file detection, and metadata persistence.

    Parameters:
        scanner: Service that enumerates local ingredient images.
        repository: CSV-backed metadata repository.
        startup_sync: Service that filters already processed files.
        vision_client: Client used to generate descriptions and keywords.
        timestamp_factory: Callable returning ISO timestamps for processed rows.

    Returns:
        MetadataEnrichmentPipeline: Reusable enrichment workflow instance.

    Raises:
        None.

    Example:
        >>> MetadataEnrichmentPipeline(
        ...     scanner=...,
        ...     repository=...,
        ...     startup_sync=...,
        ...     vision_client=...,
        ... )
        MetadataEnrichmentPipeline(...)
    """

    scanner: SupportsImageScanner
    repository: SupportsMetadataRepository
    startup_sync: SupportsStartupSync
    vision_client: SupportsVisionClient
    timestamp_factory: Callable[[], str] = _default_timestamp_factory

    def run(self, images_dir: Path) -> MetadataEnrichmentResult:
        """Run the startup enrichment workflow for the given image directory.

        Parameters:
            images_dir: Local directory containing ingredient images.

        Returns:
            MetadataEnrichmentResult: Summary of scanned files and appended rows.

        Raises:
            OSError: If image files cannot be accessed.
            ValueError: If downstream clients reject scanned files or metadata payloads.

        Example:
            >>> pipeline = MetadataEnrichmentPipeline(
            ...     scanner=...,
            ...     repository=...,
            ...     startup_sync=...,
            ...     vision_client=...,
            ... )
            >>> pipeline.run(Path("data/images"))
            MetadataEnrichmentResult(scanned_count=0, new_file_count=0, processed_rows=[])
        """

        scanned_files = self.scanner.scan_folder(images_dir)
        existing_metadata = self.repository.read_all()
        new_files = self.startup_sync.identify_new_files(scanned_files, existing_metadata)

        processed_rows: list[MetadataRow] = []
        for file_record in new_files:
            metadata = self.vision_client.analyze_image(Path(file_record.filepath))
            # A single timestamp source keeps the workflow deterministic in tests
            # and traceable in logs.
            processed_at = self.timestamp_factory()
            row = MetadataRow(
                filename=file_record.filename,
                filepath=file_record.filepath,
                description=metadata.description,
                keywords=[str(keyword) for keyword in metadata.keywords],
                processed_at=processed_at,
                last_modified=str(file_record.last_modified),
            )
            self.repository.append(row)
            processed_rows.append(row)

        return MetadataEnrichmentResult(
            scanned_count=len(scanned_files),
            new_file_count=len(new_files),
            processed_rows=processed_rows,
        )

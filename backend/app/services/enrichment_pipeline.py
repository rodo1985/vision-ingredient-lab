"""Startup enrichment pipeline for discovering and processing new images."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from backend.app.models.metadata import ImageFileRecord, MetadataRecord
from backend.app.services.metadata_repository import MetadataCSVRepository
from backend.app.services.scanner import scan_image_folder
from backend.app.services.vision_client import VisionClient, VisionMetadata


@dataclass(frozen=True)
class EnrichmentRunResult:
    """Summarize the outcome of a single enrichment pass.

    Parameters:
        discovered_files: Count of supported image files found in the dataset.
        new_files: Count of files not yet represented in the metadata repository.
        persisted_records: Count of metadata rows written during the run.
        records: Metadata records created during the run.

    Returns:
        EnrichmentRunResult: Immutable summary of the startup sync pass.

    Raises:
        None.
    """

    discovered_files: int
    new_files: int
    persisted_records: int
    records: tuple[MetadataRecord, ...]


class MetadataEnrichmentPipeline:
    """Coordinate dataset scanning, new-file detection, and metadata persistence.

    Parameters:
        metadata_repository: Repository used for reading and writing CSV metadata.
        vision_client: OpenAI-backed client that describes new image files.
        scanner: Callable used to scan the dataset directory for image files.

    Returns:
        MetadataEnrichmentPipeline: Orchestrator for startup sync behavior.

    Raises:
        None.

    Example:
        >>> pipeline = MetadataEnrichmentPipeline(repo, vision_client)
        >>> result = pipeline.run(Path("data/images"))
    """

    def __init__(
        self,
        metadata_repository: MetadataCSVRepository,
        vision_client: VisionClient,
        scanner: Callable[[Path], list[ImageFileRecord]] = scan_image_folder,
    ) -> None:
        """Initialize the enrichment pipeline.

        Parameters:
            metadata_repository: Repository used for CSV persistence.
            vision_client: Client used for image understanding.
            scanner: Dataset scanner function. Defaults to `scan_image_folder`.

        Returns:
            None

        Raises:
            None.
        """

        self._metadata_repository = metadata_repository
        self._vision_client = vision_client
        self._scanner = scanner

    def identify_new_images(self, dataset_root: Path) -> list[ImageFileRecord]:
        """Return only image files that have not been processed before.

        Parameters:
            dataset_root: Root directory containing ingredient image files.

        Returns:
            list[ImageFileRecord]: Deterministically ordered new image files.

        Raises:
            ValueError: If the dataset path is invalid.
            OSError: If the repository cannot load existing metadata.
        """

        discovered_files = self._scanner(dataset_root)
        processed_paths = {
            record.filepath
            for record in self._metadata_repository.load_all()
        }
        return [
            file_record
            for file_record in discovered_files
            if file_record.filepath not in processed_paths
        ]

    def run(self, dataset_root: Path) -> EnrichmentRunResult:
        """Scan the dataset, enrich new images, and persist their metadata.

        Parameters:
            dataset_root: Root directory containing ingredient image files.

        Returns:
            EnrichmentRunResult: Counts and records produced during the sync pass.

        Raises:
            FileNotFoundError: If a new image disappears before it can be described.
            OSError: If the repository cannot read or write metadata.
            ValueError: If the dataset path is invalid.
        """

        discovered_files = self._scanner(dataset_root)
        processed_paths = {
            record.filepath
            for record in self._metadata_repository.load_all()
        }
        new_files = [
            file_record
            for file_record in discovered_files
            if file_record.filepath not in processed_paths
        ]

        created_records = tuple(
            self._build_metadata_record(file_record)
            for file_record in new_files
        )
        persisted_records = self._metadata_repository.append_records(created_records)

        return EnrichmentRunResult(
            discovered_files=len(discovered_files),
            new_files=len(new_files),
            persisted_records=persisted_records,
            records=created_records,
        )

    def _build_metadata_record(self, file_record: ImageFileRecord) -> MetadataRecord:
        """Build a metadata record for a newly discovered image file.

        Parameters:
            file_record: Image file discovered during the scan phase.

        Returns:
            MetadataRecord: Enriched metadata ready for CSV persistence.

        Raises:
            FileNotFoundError: If the image file no longer exists when described.
        """

        vision_metadata: VisionMetadata = self._vision_client.describe_image(
            Path(file_record.filepath)
        )
        return MetadataRecord(
            filename=file_record.filename,
            filepath=file_record.filepath,
            description=vision_metadata.description,
            keywords=list(vision_metadata.keywords),
            processed_at=datetime.now(timezone.utc),
            last_modified=file_record.last_modified,
        )

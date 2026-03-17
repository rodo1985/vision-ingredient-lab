"""Tests for the metadata enrichment workflow."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from backend.ingestion.scanner import ImageFileRecord
from backend.metadata_repository import MetadataRow
from backend.workflows.metadata_enrichment import MetadataEnrichmentPipeline


@dataclass(slots=True)
class FakeVisionMetadata:
    """Represent a fake vision response used by workflow tests.

    Parameters:
        description: Description returned for the image.
        keywords: Keywords returned for the image.

    Returns:
        FakeVisionMetadata: Simple metadata container for tests.

    Raises:
        None.
    """

    description: str
    keywords: tuple[str, ...]


class FakeScanner:
    """Provide a deterministic scanner stub for enrichment tests.

    Parameters:
        scanned_files: Files that should be returned during the scan.

    Returns:
        FakeScanner: Scanner stub.

    Raises:
        None.
    """

    def __init__(self, scanned_files: list[ImageFileRecord]) -> None:
        """Store the files that this scanner should return.

        Parameters:
            scanned_files: Files to expose during the workflow run.

        Returns:
            None.

        Raises:
            None.
        """

        self.scanned_files = scanned_files
        self.calls: list[Path] = []

    def scan_folder(self, root: Path) -> list[ImageFileRecord]:
        """Record the scan directory and return prepared file records.

        Parameters:
            root: Directory passed into the workflow.

        Returns:
            list[ImageFileRecord]: Prepared scan records.

        Raises:
            None.
        """

        self.calls.append(root)
        return list(self.scanned_files)


class FakeRepository:
    """Provide an in-memory metadata repository stub for workflow tests.

    Parameters:
        existing_rows: Metadata rows already stored before the workflow runs.

    Returns:
        FakeRepository: Repository stub.

    Raises:
        None.
    """

    def __init__(self, existing_rows: list[MetadataRow] | None = None) -> None:
        """Initialize the repository stub with optional seed rows.

        Parameters:
            existing_rows: Rows that should already exist before processing.

        Returns:
            None.

        Raises:
            None.
        """

        self.rows = list(existing_rows or [])
        self.appended_rows: list[MetadataRow] = []

    def read_all(self) -> list[MetadataRow]:
        """Return the stored rows.

        Parameters:
            None.

        Returns:
            list[MetadataRow]: Current metadata rows.

        Raises:
            None.
        """

        return list(self.rows)

    def append(self, row: MetadataRow) -> None:
        """Record a new row as appended and update in-memory storage.

        Parameters:
            row: Metadata row to append.

        Returns:
            None.

        Raises:
            None.
        """

        self.rows = [existing for existing in self.rows if existing.filepath != row.filepath]
        self.rows.append(row)
        self.appended_rows.append(row)


class FakeStartupSync:
    """Provide a startup sync stub that returns a preselected new-file list.

    Parameters:
        new_files: Files the startup sync step should consider unprocessed.

    Returns:
        FakeStartupSync: Startup sync stub.

    Raises:
        None.
    """

    def __init__(self, new_files: list[ImageFileRecord]) -> None:
        """Initialize the startup sync stub with prepared new files.

        Parameters:
            new_files: Files to return from `identify_new_files`.

        Returns:
            None.

        Raises:
            None.
        """

        self.new_files = new_files
        self.calls: list[tuple[list[ImageFileRecord], list[MetadataRow]]] = []

    def identify_new_files(
        self,
        scanned_files: list[ImageFileRecord],
        existing_metadata: list[MetadataRow],
    ) -> list[ImageFileRecord]:
        """Record the inputs and return the prepared new-file list.

        Parameters:
            scanned_files: Files returned by the scanner.
            existing_metadata: Rows returned by the repository.

        Returns:
            list[ImageFileRecord]: Files to process during the workflow.

        Raises:
            None.
        """

        self.calls.append((list(scanned_files), list(existing_metadata)))
        return list(self.new_files)


class FakeVisionClient:
    """Provide a deterministic vision client stub for enrichment tests.

    Parameters:
        metadata_by_path: Mapping from file path to fake metadata result.

    Returns:
        FakeVisionClient: Vision client stub.

    Raises:
        None.
    """

    def __init__(self, metadata_by_path: dict[str, FakeVisionMetadata]) -> None:
        """Store fake metadata keyed by absolute file path.

        Parameters:
            metadata_by_path: Metadata payloads to return for each file.

        Returns:
            None.

        Raises:
            None.
        """

        self.metadata_by_path = metadata_by_path
        self.calls: list[Path] = []

    def analyze_image(self, image_path: Path) -> FakeVisionMetadata:
        """Return prepared metadata for the given file path.

        Parameters:
            image_path: File path requested by the workflow.

        Returns:
            FakeVisionMetadata: Prepared metadata result.

        Raises:
            KeyError: If the test did not prepare metadata for the path.
        """

        self.calls.append(image_path)
        return self.metadata_by_path[str(image_path)]


def test_run_processes_only_new_files() -> None:
    """Ensure the workflow enriches only files identified as new.

    Parameters:
        None.

    Returns:
        None.

    Raises:
        None.
    """

    existing_row = MetadataRow(
        filename="existing.png",
        filepath="/tmp/existing.png",
        description="existing",
        keywords=["existing"],
        processed_at="2026-03-17T00:00:00+00:00",
        last_modified="1.0",
    )
    scanned_files = [
        ImageFileRecord("existing.png", "/tmp/existing.png", 1.0),
        ImageFileRecord("new.png", "/tmp/new.png", 2.0),
    ]
    scanner = FakeScanner(scanned_files)
    repository = FakeRepository(existing_rows=[existing_row])
    startup_sync = FakeStartupSync(new_files=[scanned_files[1]])
    vision_client = FakeVisionClient(
        metadata_by_path={
            "/tmp/new.png": FakeVisionMetadata(
                description="fresh basil and tomato",
                keywords=("basil", "tomato"),
            )
        }
    )
    pipeline = MetadataEnrichmentPipeline(
        scanner=scanner,
        repository=repository,
        startup_sync=startup_sync,
        vision_client=vision_client,
        timestamp_factory=lambda: "2026-03-17T10:00:00+00:00",
    )

    result = pipeline.run(Path("/tmp/images"))

    assert result.scanned_count == 2
    assert result.new_file_count == 1
    assert len(result.processed_rows) == 1
    assert result.processed_rows[0].filename == "new.png"
    assert result.processed_rows[0].keywords == ["basil", "tomato"]
    assert result.processed_rows[0].processed_at == "2026-03-17T10:00:00+00:00"
    assert result.processed_rows[0].last_modified == "2.0"
    assert vision_client.calls == [Path("/tmp/new.png")]
    assert repository.appended_rows == result.processed_rows


def test_run_handles_no_new_files_without_calling_vision_client() -> None:
    """Ensure no enrichment occurs when startup sync finds no new files.

    Parameters:
        None.

    Returns:
        None.

    Raises:
        None.
    """

    scanned_files = [ImageFileRecord("existing.png", "/tmp/existing.png", 1.0)]
    scanner = FakeScanner(scanned_files)
    repository = FakeRepository()
    startup_sync = FakeStartupSync(new_files=[])
    vision_client = FakeVisionClient(metadata_by_path={})
    pipeline = MetadataEnrichmentPipeline(
        scanner=scanner,
        repository=repository,
        startup_sync=startup_sync,
        vision_client=vision_client,
        timestamp_factory=lambda: "2026-03-17T10:00:00+00:00",
    )

    result = pipeline.run(Path("/tmp/images"))

    assert result.scanned_count == 1
    assert result.new_file_count == 0
    assert result.processed_rows == []
    assert vision_client.calls == []
    assert repository.appended_rows == []

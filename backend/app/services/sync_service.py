"""Orchestrate image scanning, metadata enrichment, and embeddings refresh."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from app.models.api import SyncResponse
from app.repositories.embedding_store import EmbeddingStore
from app.repositories.metadata_store import MetadataStore
from app.search.embeddings import EmbeddingClient, build_embedding_records
from app.services.folder_scanner import create_pending_record, scan_image_folder
from app.services.metadata_extractor import MetadataExtractor


class SyncService:
    """Coordinate metadata sync between disk, CSV, and embeddings.

    Args:
        image_root: Root directory for source images.
        metadata_store: Canonical metadata repository.
        embedding_store: Derived embeddings repository.
        extractor: Metadata extraction service.
        embedder: Embedding generation service.
        vision_model: Vision model name for pending records.

    Returns:
        SyncService: Configured sync orchestrator.
    """

    def __init__(
        self,
        image_root: Path,
        metadata_store: MetadataStore,
        embedding_store: EmbeddingStore,
        extractor: MetadataExtractor,
        embedder: EmbeddingClient,
        vision_model: str,
    ) -> None:
        """Initialize the sync service."""

        self.image_root = image_root
        self.metadata_store = metadata_store
        self.embedding_store = embedding_store
        self.extractor = extractor
        self.embedder = embedder
        self.vision_model = vision_model

    def run(self) -> SyncResponse:
        """Run a full metadata and embedding sync.

        Returns:
            SyncResponse: Summary of the sync operation.
        """

        started_at = datetime.now(tz=UTC)
        existing_records = self.metadata_store.load_all()
        scan_result = scan_image_folder(self.image_root, existing_records)
        records_by_id = {record.image_id: record for record in existing_records}

        new_count = 0
        updated_count = 0
        failed_count = 0

        for image_path in scan_result.new_paths + scan_result.updated_paths:
            pending = create_pending_record(image_path, self.image_root, self.vision_model)
            try:
                extracted = self.extractor.extract(image_path)
                pending.description = extracted.description
                pending.tags = extracted.tags
                pending.search_text = " ".join([pending.filename, pending.description, *pending.tags])
                pending.status = "ready"
                pending.error_message = ""
                if pending.image_id in records_by_id:
                    updated_count += 1
                else:
                    new_count += 1
            except Exception as exc:  # pragma: no cover - defensive integration boundary
                pending.status = "error"
                pending.error_message = str(exc)
                failed_count += 1
            records_by_id[pending.image_id] = pending

        for stale_id in scan_result.stale_ids:
            if stale_id in records_by_id:
                stale_record = records_by_id[stale_id]
                stale_record.status = "stale"
                records_by_id[stale_id] = stale_record

        records = sorted(records_by_id.values(), key=lambda record: record.filename.lower())
        self.metadata_store.save_all(records)
        self.embedding_store.save_all(build_embedding_records(records, self.embedder))

        completed_at = datetime.now(tz=UTC)
        return SyncResponse(
            scannedCount=len(scan_result.scanned_paths),
            newCount=new_count,
            updatedCount=updated_count,
            failedCount=failed_count,
            startedAt=started_at,
            completedAt=completed_at,
        )

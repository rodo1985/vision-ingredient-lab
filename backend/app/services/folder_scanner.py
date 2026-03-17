"""Detect new, changed, and stale image files."""

from __future__ import annotations

import mimetypes
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from app.models.domain import ImageMetadataRecord

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


@dataclass(slots=True)
class ScanResult:
    """Describe the results of a folder scan.

    Args:
        scanned_paths: All discovered image paths.
        new_paths: Newly discovered image paths.
        updated_paths: Existing image paths that changed.
        stale_ids: Metadata ids for files no longer present.

    Returns:
        ScanResult: Scan summary object.
    """

    scanned_paths: list[Path]
    new_paths: list[Path]
    updated_paths: list[Path]
    stale_ids: list[str]


def build_image_id(path: Path) -> str:
    """Build a stable identifier from a file path stem.

    Args:
        path: Source image path.

    Returns:
        str: Stable image identifier.
    """

    return f"img_{path.stem.lower().replace(' ', '_')}"


def build_file_url(path: Path, image_root: Path) -> str:
    """Create a client-facing relative URL for an image.

    Args:
        path: Absolute source path.
        image_root: Root image directory.

    Returns:
        str: Relative URL string.
    """

    return f"/data/images/{path.relative_to(image_root).as_posix()}"


def scan_image_folder(image_root: Path, existing_records: list[ImageMetadataRecord]) -> ScanResult:
    """Scan for new, changed, and stale image files.

    Args:
        image_root: Directory containing source images.
        existing_records: Canonical metadata records already stored.

    Returns:
        ScanResult: Scan summary.
    """

    image_root.mkdir(parents=True, exist_ok=True)
    scanned_paths = sorted(
        [path for path in image_root.rglob("*") if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS]
    )
    existing_by_path = {record.filepath: record for record in existing_records}
    current_paths = {str(path.resolve()) for path in scanned_paths}

    new_paths: list[Path] = []
    updated_paths: list[Path] = []
    for path in scanned_paths:
        resolved = str(path.resolve())
        record = existing_by_path.get(resolved)
        modified_at = datetime.fromtimestamp(path.stat().st_mtime, tz=UTC)
        if record is None:
            new_paths.append(path)
            continue
        if modified_at != record.last_modified:
            updated_paths.append(path)

    stale_ids = [record.image_id for record in existing_records if record.filepath not in current_paths]
    return ScanResult(
        scanned_paths=scanned_paths,
        new_paths=new_paths,
        updated_paths=updated_paths,
        stale_ids=stale_ids,
    )


def create_pending_record(path: Path, image_root: Path, model_version: str) -> ImageMetadataRecord:
    """Create a pending metadata record before enrichment.

    Args:
        path: Source image path.
        image_root: Root image directory.
        model_version: Vision model name for traceability.

    Returns:
        ImageMetadataRecord: Pending record.
    """

    modified_at = datetime.fromtimestamp(path.stat().st_mtime, tz=UTC)
    mime_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return ImageMetadataRecord(
        image_id=build_image_id(path),
        filename=path.name,
        filepath=str(path.resolve()),
        file_url=build_file_url(path.resolve(), image_root.resolve()),
        mime_type=mime_type,
        description="",
        tags=[],
        search_text=path.stem,
        processed_at=datetime.now(tz=UTC),
        last_modified=modified_at,
        embedding_version="v1",
        model_version=model_version,
        status="processing",
        error_message="",
    )

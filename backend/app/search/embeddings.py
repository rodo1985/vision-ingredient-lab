"""Embedding helpers and interfaces for semantic search."""

from __future__ import annotations

import math
from datetime import UTC, datetime

from openai import OpenAI

from app.models.domain import EmbeddingRecord, ImageMetadataRecord


class EmbeddingClient:
    """Wrap embedding generation through the OpenAI SDK.

    Args:
        client: OpenAI client instance.
        model: Embedding model name.

    Returns:
        EmbeddingClient: Configured embedding client.
    """

    def __init__(self, client: OpenAI, model: str) -> None:
        """Initialize the embedding client.

        Args:
            client: OpenAI client instance.
            model: Embedding model name.

        Returns:
            None
        """

        self.client = client
        self.model = model

    def embed_text(self, text: str) -> list[float]:
        """Generate an embedding vector for text.

        Args:
            text: Source text to embed.

        Returns:
            list[float]: Embedding vector.
        """

        response = self.client.embeddings.create(model=self.model, input=text)
        return list(response.data[0].embedding)


def cosine_similarity(left: list[float], right: list[float]) -> float:
    """Compute cosine similarity between two vectors.

    Args:
        left: First vector.
        right: Second vector.

    Returns:
        float: Cosine similarity in the range [-1, 1].
    """

    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    dot_product = sum(a * b for a, b in zip(left, right, strict=False))
    return dot_product / (left_norm * right_norm)


def build_embedding_records(
    records: list[ImageMetadataRecord],
    embedder: EmbeddingClient,
    embedding_version: str = "v1",
) -> list[EmbeddingRecord]:
    """Generate embedding records for active metadata rows.

    Args:
        records: Metadata records to embed.
        embedder: Embedding client used for generation.
        embedding_version: Version label for the embedding schema.

    Returns:
        list[EmbeddingRecord]: Derived embedding records.
    """

    embeddings: list[EmbeddingRecord] = []
    for record in records:
        # Stale or failed rows should not influence retrieval results.
        if record.status != "ready":
            continue
        embeddings.append(
            EmbeddingRecord(
                image_id=record.image_id,
                vector=embedder.embed_text(record.search_text),
                embedding_version=embedding_version,
                updated_at=datetime.now(tz=UTC),
            )
        )
    return embeddings

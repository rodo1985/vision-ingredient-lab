"""Hybrid keyword and semantic search ranking."""

from __future__ import annotations

from app.models.domain import EmbeddingRecord, ImageMetadataRecord, SearchMatch
from app.search.embeddings import cosine_similarity


def normalize_query(query: str) -> list[str]:
    """Normalize a user query into lowercase tokens.

    Args:
        query: Raw search query.

    Returns:
        list[str]: Lowercase query tokens.
    """

    return [token.strip().lower() for token in query.split() if token.strip()]


def keyword_score(query_tokens: list[str], record: ImageMetadataRecord) -> tuple[float, list[str]]:
    """Score a metadata record by exact query overlap.

    Args:
        query_tokens: Normalized query tokens.
        record: Metadata record to evaluate.

    Returns:
        tuple[float, list[str]]: Keyword score and matched tags.
    """

    if not query_tokens:
        return 0.0, []

    matched_tags = sorted({tag for tag in record.tags if tag in query_tokens})
    description_tokens = set(record.description.lower().split())
    description_hits = sum(1 for token in query_tokens if token in description_tokens)
    tag_score = len(matched_tags) / max(len(query_tokens), 1)
    description_score = description_hits / max(len(query_tokens), 1)
    return min(1.0, (tag_score * 0.75) + (description_score * 0.25)), matched_tags


def rank_records(
    query: str,
    query_vector: list[float],
    records: list[ImageMetadataRecord],
    embedding_records: list[EmbeddingRecord],
    limit: int = 20,
) -> list[SearchMatch]:
    """Rank image metadata records using a hybrid score.

    Args:
        query: Raw search query.
        query_vector: Query embedding vector.
        records: Metadata records to rank.
        embedding_records: Stored image embeddings.
        limit: Maximum number of matches to return.

    Returns:
        list[SearchMatch]: Ranked search matches.
    """

    query_tokens = normalize_query(query)
    vectors_by_id = {record.image_id: record.vector for record in embedding_records}
    ranked: list[SearchMatch] = []

    for record in records:
        if record.status != "ready":
            continue
        exact_score, matched_tags = keyword_score(query_tokens, record)
        semantic_score = cosine_similarity(query_vector, vectors_by_id.get(record.image_id, []))
        combined_score = (exact_score * 0.65) + (semantic_score * 0.35)
        match_reasons: list[str] = []
        if matched_tags or exact_score > 0:
            match_reasons.append("keyword")
        if semantic_score > 0.2:
            match_reasons.append("semantic")
        if combined_score <= 0:
            continue
        ranked.append(
            SearchMatch(
                image=record,
                score=combined_score,
                match_reasons=match_reasons,
                matched_tags=matched_tags,
            )
        )

    ranked.sort(
        key=lambda match: (-match.score, -len(match.matched_tags), match.image.filename.lower())
    )
    return ranked[:limit]

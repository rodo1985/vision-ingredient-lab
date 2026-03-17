"""Keyword- and description-based metadata search helpers."""

from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple

from backend.app.models.metadata import MetadataRecord


def _normalize_terms(text: str | None) -> Tuple[str, ...]:
    """Normalize a string into lowercase tokens for scoring.

    Parameters:
        text: Raw text that should be tokenized.

    Returns:
        Tuple[str, ...]: Lowercase, deduplicated tokens in deterministic order.
    """

    if not text:
        return ()
    parts = (part.strip().lower() for part in text.replace(",", " ").split())
    tokens: List[str] = []
    seen = set()
    for part in parts:
        if not part or part in seen:
            continue
        seen.add(part)
        tokens.append(part)
    return tuple(tokens)


@dataclass(frozen=True)
class SearchMatch:
    """Structure that pairs a metadata record with its match score."""

    record: MetadataRecord
    score: int


def _score_record(record: MetadataRecord, query_tokens: Sequence[str]) -> int:
    """Compute a simple relevance score for a record against query terms."""

    if not query_tokens:
        return 0

    keyword_tokens = tuple(term.lower() for term in record.keywords)
    description_tokens = _normalize_terms(record.description)

    keyword_hits = sum(1 for token in query_tokens if token in keyword_tokens)
    description_hits = sum(1 for token in query_tokens if token in description_tokens)

    # Weight keyword matches higher so ingredient hits bubble to the top.
    return keyword_hits * 3 + description_hits


def search_metadata(
    records: Iterable[MetadataRecord],
    query: str | None,
    *,
    max_results: int | None = None,
) -> List[MetadataRecord]:
    """Search metadata records using keywords and descriptions.

    Parameters:
        records: Iterable metadata entries to filter.
        query: Search query text provided by the frontend.
        max_results: Optional limit on the number of returned records.

    Returns:
        List[MetadataRecord]: Matching records sorted by relevance then filepath.
    """

    query_tokens = _normalize_terms(query)
    matches: List[SearchMatch] = []

    for record in records:
        score = _score_record(record, query_tokens)
        matches.append(SearchMatch(record=record, score=score))

    # Deterministic order: sort by descending score then by filepath for stability.
    matches.sort(key=lambda match: (-match.score, match.record.filepath))

    filtered = [match.record for match in matches if match.score > 0 or not query_tokens]
    if max_results is not None:
        return filtered[:max_results]
    return filtered

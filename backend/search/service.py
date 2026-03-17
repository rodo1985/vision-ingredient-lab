"""Search service for ingredient metadata stored in CSV."""

from __future__ import annotations

from dataclasses import dataclass

from backend.metadata_repository import CsvMetadataRepository, MetadataRow


@dataclass(frozen=True, slots=True)
class SearchResult:
    """Wrap a metadata row with a deterministic relevance score.

    Parameters:
        row: Metadata row returned from the repository.
        score: Numerical score used for sorting matches.

    Returns:
        SearchResult: Scored search hit.

    Raises:
        None.
    """

    row: MetadataRow
    score: int


def _matches_keywords(row: MetadataRow, query: str) -> bool:
    """Return whether the query matches any keyword exactly.

    Parameters:
        row: Metadata row to inspect.
        query: Normalized user query.

    Returns:
        bool: `True` when at least one keyword matches exactly.

    Raises:
        None.
    """

    normalized_keywords = (keyword.lower() for keyword in row.keywords)
    return any(keyword == query for keyword in normalized_keywords)


def _matches_description(row: MetadataRow, query: str) -> bool:
    """Return whether the query appears anywhere in the description.

    Parameters:
        row: Metadata row to inspect.
        query: Normalized user query.

    Returns:
        bool: `True` when the description contains the query as a substring.

    Raises:
        None.
    """

    return query in row.description.lower()


def search_metadata(repo: CsvMetadataRepository, query: str) -> list[MetadataRow]:
    """Search metadata for rows that mention the provided query.

    Parameters:
        repo: CSV repository to read metadata from.
        query: User-supplied search term.

    Returns:
        List[MetadataRow]: Matching rows ordered by score and filepath.

    Raises:
        ValueError: When the query is empty or whitespace only.

    Example:
        >>> repo = CsvMetadataRepository("data/metadata.csv")
        >>> search_metadata(repo, "tomato")
        []
    """

    normalized_query = query.strip().lower()
    if not normalized_query:
        raise ValueError("Search query must not be empty.")

    rows: list[SearchResult] = []
    for metadata in repo.read_all():
        keyword_hit = _matches_keywords(metadata, normalized_query)
        description_hit = _matches_description(metadata, normalized_query)

        if not (keyword_hit or description_hit):
            continue

        score = int(keyword_hit) * 2 + int(description_hit)
        rows.append(SearchResult(row=metadata, score=score))

    rows.sort(key=lambda candidate: (-candidate.score, candidate.row.filepath))
    return [candidate.row for candidate in rows]

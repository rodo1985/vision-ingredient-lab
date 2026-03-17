import type { IngredientResult } from "../state/ingredientState";

import "./SearchResultsGrid.css";

export type SearchResultsGridProps = {
  results: IngredientResult[];
  selectedIds: string[];
  isLoading: boolean;
  errorMessage?: string | null;
  onSelect: (ingredient: IngredientResult) => void;
};

/**
 * Presentational grid showing ingredient search hits.
 *
 * The component delegates selection handling to the caller via `onSelect` and
 * keeps all UI-specific states (loading, error, empty, selection) local.
 */
export function SearchResultsGrid({
  results,
  selectedIds,
  isLoading,
  errorMessage,
  onSelect,
}: SearchResultsGridProps) {
  if (isLoading) {
    return (
      <div className="search-results__status" role="status">
        <span className="search-results__loading">Loading ingredients…</span>
      </div>
    );
  }

  if (errorMessage) {
    return (
      <div className="search-results__status search-results__error" role="alert">
        {errorMessage}
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <div className="search-results__status" role="status">
        No ingredients match that search yet. Try another term.
      </div>
    );
  }

  return (
    <div className="search-results__grid" role="list" aria-label="Ingredient results">
      {results.map((ingredient) => {
        const isSelected = selectedIds.includes(ingredient.id);
        return (
          <article className="search-results__card" key={ingredient.id} role="listitem">
            <header className="search-results__card-header">
              <h3>{ingredient.name}</h3>
            </header>
            <p className="search-results__description">{ingredient.description}</p>
            <div className="search-results__keywords" aria-label="keywords">
              {ingredient.keywords.map((keyword) => (
                <span className="search-results__keyword" key={keyword}>
                  {keyword}
                </span>
              ))}
            </div>
            <button
              type="button"
              className={`search-results__select ${isSelected ? "search-results__select--selected" : ""}`}
              onClick={() => onSelect(ingredient)}
              disabled={isSelected}
              aria-pressed={isSelected}
            >
              {isSelected ? "Selected" : "Add"}
            </button>
          </article>
        );
      })}
    </div>
  );
}

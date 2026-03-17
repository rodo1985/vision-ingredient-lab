import type { SearchStatus } from "../state/ingredientState";

import "./IngredientSearchPanel.css";

interface IngredientSearchPanelProps {
  query: string;
  onQueryChange: (query: string) => void;
  resultCount: number;
  searchStatus: SearchStatus;
  searchError: string | null;
}

/**
 * Render the ingredient search controls and current search feedback.
 *
 * Parameters:
 *   query: Active search query from shared state.
 *   onQueryChange: Callback used to update the shared query state.
 *   resultCount: Number of search results currently loaded.
 *   searchStatus: Current search lifecycle status.
 *   searchError: Optional error message from the latest search request.
 *
 * Returns:
 *   JSX.Element: Search controls panel for the ingredient lab workspace.
 */
export function IngredientSearchPanel({
  query,
  onQueryChange,
  resultCount,
  searchStatus,
  searchError,
}: IngredientSearchPanelProps) {
  return (
    <section className="search-panel" aria-label="Ingredient search">
      <div className="search-panel__header">
        <p className="search-panel__kicker">Search ingredients</p>
        <h2>Find the building blocks for your next creative dish.</h2>
        <p className="search-panel__copy">
          Search by ingredient name or describe what you want to explore. The backend
          will match against generated descriptions and keyword tags.
        </p>
      </div>

      <label className="search-panel__field" htmlFor="ingredient-query">
        <span className="search-panel__label">Ingredient query</span>
        <input
          id="ingredient-query"
          name="ingredient-query"
          type="search"
          value={query}
          placeholder="Try tomato, mozzarella, basil, dough..."
          onChange={(event) => onQueryChange(event.target.value)}
        />
      </label>

      <div className="search-panel__status" aria-live="polite">
        <p>
          <strong>{resultCount}</strong> result{resultCount === 1 ? "" : "s"} loaded
        </p>
        <p className="search-panel__status-pill">{formatSearchStatus(searchStatus)}</p>
      </div>

      {searchError ? <p className="search-panel__error">{searchError}</p> : null}
    </section>
  );
}

/**
 * Convert the search status enum into UI-friendly copy.
 *
 * Parameters:
 *   status: Current search lifecycle status.
 *
 * Returns:
 *   string: Human-readable label for the current search state.
 */
function formatSearchStatus(status: SearchStatus): string {
  switch (status) {
    case "loading":
      return "Searching";
    case "success":
      return "Ready";
    case "error":
      return "Needs attention";
    case "idle":
    default:
      return "Waiting";
  }
}

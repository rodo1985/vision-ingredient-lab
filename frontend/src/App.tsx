import { useEffect } from "react";

import { defaultApiClient, type MetadataRow } from "./lib/api/client";
import { LabShell } from "./components/LabShell";
import {
  IngredientProvider,
  useIngredientActions,
  useIngredientState,
} from "./state/ingredientState";

/**
 * Render the top-level frontend shell for Vision Ingredient Lab.
 *
 * Returns:
 *   JSX.Element: Root application shell for the React frontend.
 */
export function App() {
  return (
    <IngredientProvider>
      <AppContent />
    </IngredientProvider>
  );
}

/**
 * Connect the app shell to the shared ingredient state foundation.
 *
 * Returns:
 *   JSX.Element: Shell populated with current state snapshots.
 */
function AppContent() {
  const state = useIngredientState();
  const dispatch = useIngredientActions();

  useEffect(() => {
    let cancelled = false;
    const timeoutId = window.setTimeout(async () => {
      dispatch({ type: "setSearchStatus", payload: "loading" });
      dispatch({ type: "setSearchError", payload: null });

      try {
        const rows = state.query.trim()
          ? await defaultApiClient.searchMetadata(state.query)
          : await defaultApiClient.listMetadata();
        if (cancelled) {
          return;
        }

        dispatch({
          type: "setResults",
          payload: rows.map(mapMetadataRowToIngredientResult),
        });
        dispatch({ type: "setSearchStatus", payload: "success" });
      } catch (error) {
        if (cancelled) {
          return;
        }

        const message =
          error instanceof Error ? error.message : "Unable to load ingredient metadata.";
        dispatch({ type: "setResults", payload: [] });
        dispatch({ type: "setSearchStatus", payload: "error" });
        dispatch({ type: "setSearchError", payload: message });
      }
    }, 250);

    return () => {
      cancelled = true;
      window.clearTimeout(timeoutId);
    };
  }, [dispatch, state.query]);

  return (
    <LabShell
      query={state.query}
      onQueryChange={(query) => dispatch({ type: "setQuery", payload: query })}
      searchStatus={state.searchStatus}
      searchError={state.searchError}
      results={state.results}
      selectedIngredients={state.selectedIngredients}
      onSelectIngredient={(ingredient) => dispatch({ type: "addIngredient", payload: ingredient })}
      onRemoveIngredient={(ingredientId) =>
        dispatch({ type: "removeIngredient", payload: ingredientId })
      }
      onClearSelection={() => dispatch({ type: "clearSelection" })}
      selectedCount={state.selectedIngredients.length}
      resultCount={state.results.length}
      generationStatus={state.generationStatus}
    />
  );
}

/**
 * Convert backend metadata rows into UI-friendly ingredient search results.
 *
 * Parameters:
 *   row: Metadata row returned by the backend API.
 *
 * Returns:
 *   IngredientResult: Frontend search result with a stable identifier and display name.
 */
function mapMetadataRowToIngredientResult(row: MetadataRow) {
  return {
    id: row.filepath,
    name: formatIngredientName(row.filename),
    description: row.description,
    keywords: row.keywords,
  };
}

/**
 * Turn a local filename into a readable ingredient name for the UI.
 *
 * Parameters:
 *   filename: Raw file name stored in the metadata CSV.
 *
 * Returns:
 *   string: Human-friendly title derived from the filename.
 */
function formatIngredientName(filename: string): string {
  const withoutExtension = filename.replace(/\.[^.]+$/, "");
  return withoutExtension
    .split(/[-_\s]+/)
    .filter(Boolean)
    .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1))
    .join(" ");
}

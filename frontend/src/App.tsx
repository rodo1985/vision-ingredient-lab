import { IngredientProvider, useIngredientState } from "./state/ingredientState";
import { LabShell } from "./components/LabShell";

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

  return (
    <LabShell
      selectedCount={state.selectedIds.length}
      resultCount={state.results.length}
      generationStatus={state.generationStatus}
    />
  );
}

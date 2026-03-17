import type {
  GeneratedResult,
  GenerationStatus,
  IngredientResult,
  SearchStatus,
} from "../state/ingredientState";

import { GenerateImagePanel } from "./GenerateImagePanel";
import { GeneratedResultPanel } from "./GeneratedResultPanel";
import { IngredientSearchPanel } from "./IngredientSearchPanel";
import { SearchResultsGrid } from "./SearchResultsGrid";
import { SelectedIngredientsPanel } from "./SelectedIngredientsPanel";

type InsightCard = {
  label: string;
  value: string;
  detail: string;
};

const insightCards: InsightCard[] = [
  {
    label: "Dataset Pulse",
    value: "Local-first",
    detail: "Every run checks the ingredient folder for brand-new images."
  },
  {
    label: "Metadata Engine",
    value: "Vision tags",
    detail: "Descriptions and keywords are generated before the UI searches them."
  },
  {
    label: "Creative Output",
    value: "Prompt-driven",
    detail: "Selected ingredients become a single visual concept for image generation."
  }
];

const upcomingPanels = [
  {
    title: "Search Ingredients",
    copy: "This panel will host debounced ingredient search, result counts, and backend-powered filtering."
  },
  {
    title: "Selected Components",
    copy: "Chosen ingredients will accumulate here with room for removing, reordering, and generation validation."
  },
  {
    title: "Generated Result",
    copy: "The resulting creative image, prompt summary, and async states will appear in this focus area."
  }
];

type LabShellProps = {
  query: string;
  onQueryChange: (query: string) => void;
  searchStatus: SearchStatus;
  searchError: string | null;
  results: IngredientResult[];
  selectedIngredients: IngredientResult[];
  onSelectIngredient: (ingredient: IngredientResult) => void;
  onRemoveIngredient: (ingredientId: string) => void;
  onClearSelection: () => void;
  selectedCount: number;
  resultCount: number;
  generationStatus: GenerationStatus;
  generationError: string | null;
  generatedResult: GeneratedResult | null;
  onGenerateImage: () => void;
};

/**
 * Render the frontend app shell that future feature waves plug into.
 *
 * Parameters:
 *   selectedCount: Number of selected ingredients in shared state.
 *   resultCount: Number of current search results in shared state.
 *   generationStatus: Current generation lifecycle status.
 *
 * Returns:
 *   JSX.Element: Layout scaffold for the ingredient lab experience.
 */
export function LabShell({
  query,
  onQueryChange,
  searchStatus,
  searchError,
  results,
  selectedIngredients,
  onSelectIngredient,
  onRemoveIngredient,
  onClearSelection,
  selectedCount,
  resultCount,
  generationStatus,
  generationError,
  generatedResult,
  onGenerateImage,
}: LabShellProps) {
  const selectedIds = selectedIngredients.map((ingredient) => ingredient.id);

  return (
    <main className="app-shell">
      <section className="hero">
        <div className="hero__badge">Vision Ingredient Lab</div>
        <div className="hero__content">
          <div className="hero__copy">
            <p className="hero__eyebrow">React foundation</p>
            <h1>Turn a folder of ingredients into a searchable creative lab.</h1>
            <p className="hero__body">
              The frontend is ready for the next waves: API wiring, shared state,
              ingredient search, and generation flow. For now it gives us a strong
              structure, visual direction, and responsive base to build on.
            </p>
            <dl className="hero__snapshot" aria-label="Current frontend state snapshot">
              <div>
                <dt>Selected</dt>
                <dd>{selectedCount}</dd>
              </div>
              <div>
                <dt>Results</dt>
                <dd>{resultCount}</dd>
              </div>
              <div>
                <dt>Generation</dt>
                <dd>{generationStatus}</dd>
              </div>
            </dl>
          </div>

          <div className="hero__stats" aria-label="Frontend architecture summary">
            {insightCards.map((card) => (
              <article className="insight-card" key={card.label}>
                <p className="insight-card__label">{card.label}</p>
                <p className="insight-card__value">{card.value}</p>
                <p className="insight-card__detail">{card.detail}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="workspace" aria-label="Application workspace preview">
        <article className="workspace-panel workspace-panel--stacked">
          <div className="workspace-panel__glow" />
          <IngredientSearchPanel
            query={query}
            onQueryChange={onQueryChange}
            resultCount={resultCount}
            searchStatus={searchStatus}
            searchError={searchError}
          />
          <SearchResultsGrid
            results={results}
            selectedIds={selectedIds}
            isLoading={searchStatus === "loading"}
            errorMessage={searchStatus === "error" ? searchError : null}
            onSelect={onSelectIngredient}
          />
        </article>

        <article className="workspace-panel workspace-panel--stacked">
          <div className="workspace-panel__glow" />
          <SelectedIngredientsPanel
            selectedIngredients={selectedIngredients}
            onRemove={onRemoveIngredient}
            onClear={onClearSelection}
          />
        </article>

        <article className="workspace-panel workspace-panel--stacked" key={upcomingPanels[2].title}>
          <div className="workspace-panel__glow" />
          <p className="workspace-panel__kicker">Generated result</p>
          <h2>{upcomingPanels[2].title}</h2>
          <p className="workspace-panel__copy">{upcomingPanels[2].copy}</p>
          <GenerateImagePanel
            selectedIngredients={selectedIngredients}
            generationStatus={generationStatus}
            onGenerate={onGenerateImage}
          />
          <GeneratedResultPanel
            generationStatus={generationStatus}
            generationError={generationError}
            generatedResult={generatedResult}
          />
        </article>
      </section>
    </main>
  );
}

import type { GenerationStatus } from "../state/ingredientState";

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
  selectedCount: number;
  resultCount: number;
  generationStatus: GenerationStatus;
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
  selectedCount,
  resultCount,
  generationStatus,
}: LabShellProps) {
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
        {upcomingPanels.map((panel) => (
          <article className="workspace-panel" key={panel.title}>
            <div className="workspace-panel__glow" />
            <p className="workspace-panel__kicker">Planned surface</p>
            <h2>{panel.title}</h2>
            <p>{panel.copy}</p>
          </article>
        ))}
      </section>
    </main>
  );
}

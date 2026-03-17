import { IngredientResult, GenerationStatus } from "../state/ingredientState";
import "./GenerateImagePanel.css";

interface GenerateImagePanelProps {
  selectedIngredients: IngredientResult[];
  generationStatus: GenerationStatus;
  onGenerate: () => void;
}

const LABELS: Record<GenerationStatus, string> = {
  idle: "Generate image",
  loading: "Generating…",
  success: "Regenerate image",
  error: "Try again",
};

/** Present a button-driven panel that triggers image generation from the selection. */
export function GenerateImagePanel({
  selectedIngredients,
  generationStatus,
  onGenerate,
}: GenerateImagePanelProps) {
  const hasEnoughIngredients = selectedIngredients.length >= 2;
  const summary =
    selectedIngredients.length > 0
      ? selectedIngredients.map((ingredient) => ingredient.name).join(", ")
      : "No ingredients selected yet.";
  const disabled = !hasEnoughIngredients || generationStatus === "loading";
  const describedBy = hasEnoughIngredients
    ? "generate-panel-summary"
    : "generate-panel-summary generate-panel-validation";

  return (
    <section className="generate-panel">
      <div>
        <p className="generate-panel__label">Creative generation</p>
        <h2 className="generate-panel__title">Combine your selection</h2>
        <p className="generate-panel__helper">
          {hasEnoughIngredients
            ? "Preview what ingredients will shape the prompt below."
            : "Add at least two ingredients before generating an image."}
        </p>
      </div>

      <div className="generate-panel__summary" id="generate-panel-summary" aria-live="polite">
        <span className="generate-panel__summary-label">Ingredients:</span>
        {summary}
      </div>

      <button
        type="button"
        className="generate-panel__button"
        disabled={disabled}
        aria-describedby={describedBy}
        onClick={onGenerate}
      >
        {LABELS[generationStatus]}
      </button>

      {!hasEnoughIngredients && (
        <p className="generate-panel__validation" id="generate-panel-validation">
          You need at least two ingredients.
        </p>
      )}
    </section>
  );
}

import type { GeneratedResult, GenerationStatus } from "../state/ingredientState";

import "./GeneratedResultPanel.css";

export type GeneratedResultPanelProps = {
  generationStatus: GenerationStatus;
  generationError: string | null;
  generatedResult: GeneratedResult | null;
};

/**
 * Presents the generated image result area based on the current generation state.
 */
export function GeneratedResultPanel({
  generationStatus,
  generationError,
  generatedResult,
}: GeneratedResultPanelProps) {
  if (generationStatus === "loading") {
    return (
      <section className="generated-result" role="status" aria-live="polite" aria-busy="true">
        <p className="generated-result__status">Creating a new ingredient-inspired image…</p>
      </section>
    );
  }

  if (generationStatus === "error") {
    return (
      <section className="generated-result generated-result--error" role="alert" aria-live="assertive">
        <p>{generationError ?? "Something went wrong while generating the artwork."}</p>
      </section>
    );
  }

  if (generationStatus === "success" && generatedResult) {
    return (
      <section className="generated-result generated-result--success">
        <img
          className="generated-result__image"
          src={generatedResult.imageUrl}
          alt={`Generated artwork: ${generatedResult.prompt}`}
        />
        <div className="generated-result__meta">
          <p className="generated-result__prompt">Prompt: {generatedResult.prompt}</p>
          {generatedResult.metadata.description && (
            <p className="generated-result__description">{generatedResult.metadata.description}</p>
          )}
          {generatedResult.metadata.keywords?.length ? (
            <div className="generated-result__keywords" aria-label="keywords">
              {generatedResult.metadata.keywords.map((keyword) => (
                <span key={keyword} className="generated-result__keyword">
                  {keyword}
                </span>
              ))}
            </div>
          ) : null}
        </div>
      </section>
    );
  }

  return (
    <section className="generated-result" role="status" aria-live="polite">
      <p className="generated-result__status">
        Generated artwork will appear here once you select a few ingredients.
      </p>
    </section>
  );
}

import { IngredientResult } from "../state/ingredientState";
import "./SelectedIngredientsPanel.css";

interface SelectedIngredientsPanelProps {
  selectedIngredients: IngredientResult[];
  onRemove: (ingredientId: string) => void;
  onClear: () => void;
}

/** Present the currently selected ingredient components before generation. */
export function SelectedIngredientsPanel({
  selectedIngredients,
  onRemove,
  onClear,
}: SelectedIngredientsPanelProps) {
  const hasSelection = selectedIngredients.length > 0;

  return (
    <section className="selected-panel">
      <header className="selected-panel__header">
        <div>
          <p className="selected-panel__label">Selected Ingredients</p>
          <h2 className="selected-panel__title">Curate your component list</h2>
          <p className="selected-panel__helper">
            Add some ingredients to craft a richer generation prompt. You can remove or clear selections anytime.
          </p>
        </div>
        {hasSelection && (
          <button className="selected-panel__clear" type="button" onClick={onClear}>
            Clear all
          </button>
        )}
      </header>

      {hasSelection ? (
        <div className="selected-panel__grid">
          {selectedIngredients.map((ingredient) => (
            <article key={ingredient.id} className="selected-panel__card">
              <div>
                <h3 className="selected-panel__ingredient-name">{ingredient.name}</h3>
                <p className="selected-panel__ingredient-description">{ingredient.description}</p>
                <div className="selected-panel__keyword-row">
                  {ingredient.keywords.map((keyword) => (
                    <span key={keyword} className="selected-panel__keyword">
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>
              <button
                className="selected-panel__remove"
                type="button"
                aria-label={`Remove ${ingredient.name}`}
                onClick={() => onRemove(ingredient.id)}
              >
                Remove
              </button>
            </article>
          ))}
        </div>
      ) : (
        <p className="selected-panel__empty">
          No ingredients selected yet. Click any search result to add it to your generation queue.
        </p>
      )}
    </section>
  );
}

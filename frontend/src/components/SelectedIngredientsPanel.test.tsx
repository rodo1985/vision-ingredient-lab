import "@testing-library/jest-dom";
import { fireEvent, render, screen } from "@testing-library/react";
import { vi } from "vitest";

import { IngredientResult } from "../state/ingredientState";
import { SelectedIngredientsPanel } from "./SelectedIngredientsPanel";

const ingredientSample: IngredientResult = {
  id: "tomato",
  name: "Tomato",
  description: "Fresh red tomato",
  keywords: ["tomato", "produce"],
};

const anotherIngredient: IngredientResult = {
  id: "basil",
  name: "Basil",
  description: "Herbal green basil",
  keywords: ["herb"],
};

describe("SelectedIngredientsPanel", () => {
  it("shows empty state when nothing is selected", () => {
    render(<SelectedIngredientsPanel selectedIngredients={[]} onRemove={() => {}} onClear={() => {}} />);

    expect(screen.getByText(/selected ingredients/i)).toBeInTheDocument();
    expect(screen.getByText(/No ingredients selected yet/i)).toBeInTheDocument();
  });

  it("renders selected ingredients with remove buttons", () => {
    render(
      <SelectedIngredientsPanel
        selectedIngredients={[ingredientSample, anotherIngredient]}
        onRemove={() => {}}
        onClear={() => {}}
      />,
    );

    expect(screen.getByText("Tomato")).toBeInTheDocument();
    expect(screen.getByText("Basil")).toBeInTheDocument();
    expect(screen.getByText("Fresh red tomato")).toBeInTheDocument();
    expect(screen.getByText("Herbal green basil")).toBeInTheDocument();
    expect(screen.getAllByRole("button", { name: /remove/i })).toHaveLength(2);
  });

  it("fires onRemove when a card's remove button is clicked", () => {
    const removeSpy = vi.fn();
    render(
      <SelectedIngredientsPanel selectedIngredients={[ingredientSample]} onRemove={removeSpy} onClear={() => {}} />,
    );

    const removeButton = screen.getByRole("button", { name: /remove tomato/i });
    fireEvent.click(removeButton);

    expect(removeSpy).toHaveBeenCalledWith("tomato");
  });

  it("shows a clear button when there are selections and triggers onClear", () => {
    const clearSpy = vi.fn();
    render(
      <SelectedIngredientsPanel
        selectedIngredients={[ingredientSample]}
        onRemove={() => {}}
        onClear={clearSpy}
      />,
    );

    const clearButton = screen.getByRole("button", { name: /clear all/i });
    expect(clearButton).toBeInTheDocument();
    fireEvent.click(clearButton);
    expect(clearSpy).toHaveBeenCalled();
  });
});

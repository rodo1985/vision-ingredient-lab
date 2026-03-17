import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";

import { SearchResultsGrid } from "./SearchResultsGrid";
import type { IngredientResult } from "../state/ingredientState";

const ingredient: IngredientResult = {
  id: "tomato",
  name: "Tomato",
  description: "Ripe and juicy",
  keywords: ["tomato", "fresh"],
};

const buildProps = (overrides = {}) => ({
  results: [],
  selectedIds: [],
  isLoading: false,
  errorMessage: null,
  onSelect: vi.fn(),
  ...overrides,
});

describe("SearchResultsGrid", () => {
  it("renders loading state when isLoading is true", () => {
    render(<SearchResultsGrid {...buildProps({ isLoading: true })} />);

    expect(screen.getByRole("status")).toHaveTextContent("Loading ingredients…");
  });

  it("shows an error alert when errorMessage is provided", () => {
    const props = buildProps({ errorMessage: "Oops" });
    render(<SearchResultsGrid {...props} />);

    expect(screen.getByRole("alert")).toHaveTextContent("Oops");
  });

  it("shows the empty copy when there are no results", () => {
    render(<SearchResultsGrid {...buildProps()} />);

    expect(screen.getByRole("status")).toHaveTextContent(
      "No ingredients match that search yet. Try another term.",
    );
  });

  it("renders ingredient cards and wires the select handler", () => {
    const onSelect = vi.fn();
    render(
      <SearchResultsGrid
        {...buildProps({ results: [ingredient], onSelect })}
      />,
    );

    expect(screen.getByText("Tomato")).toBeInTheDocument();
    const button = screen.getByRole("button", { name: "Add" });
    fireEvent.click(button);
    expect(onSelect).toHaveBeenCalledWith(ingredient);
  });

  it("disables the button when the ingredient is already selected", () => {
    render(
      <SearchResultsGrid
        {...buildProps({ results: [ingredient], selectedIds: [ingredient.id] })}
      />,
    );

    const button = screen.getByRole("button", { name: "Selected" });
    expect(button).toBeDisabled();
  });
});

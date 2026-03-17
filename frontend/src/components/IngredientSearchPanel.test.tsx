import "@testing-library/jest-dom";
import { fireEvent, render, screen } from "@testing-library/react";
import { vi } from "vitest";

import { IngredientSearchPanel } from "./IngredientSearchPanel";

/**
 * Verify the ingredient search panel renders and reports query changes.
 */
describe("IngredientSearchPanel", () => {
  it("renders current result count and forwards query changes", () => {
    const handleQueryChange = vi.fn();

    render(
      <IngredientSearchPanel
        query="tomato"
        onQueryChange={handleQueryChange}
        resultCount={4}
        searchStatus="success"
        searchError={null}
      />,
    );

    expect(screen.getByLabelText(/ingredient search/i)).toHaveTextContent("4 results loaded");
    fireEvent.change(screen.getByRole("searchbox", { name: /ingredient query/i }), {
      target: { value: "basil" },
    });

    expect(handleQueryChange).toHaveBeenCalledWith("basil");
  });

  it("renders backend search errors when present", () => {
    render(
      <IngredientSearchPanel
        query=""
        onQueryChange={() => {}}
        resultCount={0}
        searchStatus="error"
        searchError="Backend unavailable"
      />,
    );

    expect(screen.getByText("Backend unavailable")).toBeInTheDocument();
    expect(screen.getByText(/needs attention/i)).toBeInTheDocument();
  });
});

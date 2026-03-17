import "@testing-library/jest-dom";
import { fireEvent, render, screen } from "@testing-library/react";
import { vi } from "vitest";

import { IngredientResult } from "../state/ingredientState";
import { GenerateImagePanel } from "./GenerateImagePanel";

const sampleIngredient: IngredientResult = {
  id: "tomato",
  name: "Tomato",
  description: "Fresh tomato",
  keywords: ["tomato"],
};

const anotherIngredient: IngredientResult = {
  id: "basil",
  name: "Basil",
  description: "Herb",
  keywords: ["basil"],
};

describe("GenerateImagePanel", () => {
  it("disables the button when fewer than two ingredients are selected", () => {
    render(
      <GenerateImagePanel
        selectedIngredients={[sampleIngredient]}
        generationStatus="idle"
        onGenerate={() => {}}
      />,
    );

    const button = screen.getByRole("button", { name: /generate image/i });
    expect(button).toBeDisabled();
    expect(screen.getByText(/need at least two ingredients/i)).toBeInTheDocument();
  });

  it("shows the selected ingredient summary and enables the button when ready", () => {
    render(
      <GenerateImagePanel
        selectedIngredients={[sampleIngredient, anotherIngredient]}
        generationStatus="idle"
        onGenerate={() => {}}
      />,
    );

    expect(screen.getByText(/Tomato, Basil/)).toBeInTheDocument();
    const button = screen.getByRole("button", { name: /generate image/i });
    expect(button).toBeEnabled();
  });

  it("disables the button while loading", () => {
    render(
      <GenerateImagePanel
        selectedIngredients={[sampleIngredient, anotherIngredient]}
        generationStatus="loading"
        onGenerate={() => {}}
      />,
    );

    expect(screen.getByRole("button", { name: /generating/i })).toBeDisabled();
  });

  it("calls onGenerate when clicked", () => {
    const generateSpy = vi.fn();

    render(
      <GenerateImagePanel
        selectedIngredients={[sampleIngredient, anotherIngredient]}
        generationStatus="idle"
        onGenerate={generateSpy}
      />,
    );

    fireEvent.click(screen.getByRole("button", { name: /generate image/i }));
    expect(generateSpy).toHaveBeenCalledTimes(1);
  });
});

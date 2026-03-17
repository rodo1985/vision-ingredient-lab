import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";

import { GeneratedResultPanel } from "./GeneratedResultPanel";
import type { GeneratedResult } from "../state/ingredientState";

const sampleResult: GeneratedResult = {
  prompt: "Create a basil-pesto swirl",
  imageUrl: "https://example.com/basil.png",
  metadata: {
    description: "A dreamy pesto swirl",
    keywords: ["pesto", "basil"],
  },
};

describe("GeneratedResultPanel", () => {
  it("shows idle copy when status is idle", () => {
    render(
      <GeneratedResultPanel generationStatus="idle" generationError={null} generatedResult={null} />,
    );

    expect(screen.getByRole("status")).toHaveTextContent(
      "Generated artwork will appear here once you select a few ingredients.",
    );
  });

  it("shows loading copy when status is loading", () => {
    render(
      <GeneratedResultPanel generationStatus="loading" generationError={null} generatedResult={null} />,
    );

    expect(screen.getByRole("status")).toHaveTextContent("Creating a new ingredient-inspired image…");
  });

  it("shows an error alert when status is error", () => {
    render(
      <GeneratedResultPanel
        generationStatus="error"
        generationError="Boom"
        generatedResult={null}
      />, 
    );

    expect(screen.getByRole("alert")).toHaveTextContent("Boom");
  });

  it("renders the generated result when status is success", () => {
    render(
      <GeneratedResultPanel
        generationStatus="success"
        generationError={null}
        generatedResult={sampleResult}
      />, 
    );

    expect(screen.getByRole("img")).toHaveAttribute("src", sampleResult.imageUrl);
    expect(screen.getByText(/Prompt:\s+Create a basil-pesto swirl/)).toBeInTheDocument();
    expect(screen.getByText("pesto")).toBeInTheDocument();
  });
});

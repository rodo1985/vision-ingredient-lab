import { describe, expect, it } from "vitest";

import {
  GeneratedResult,
  IngredientResult,
  IngredientState,
  ingredientReducer,
  initialIngredientState,
} from "./ingredientState";

const sampleResult: IngredientResult = {
  id: "tomato",
  name: "Tomato",
  description: "Fresh tomato",
  keywords: ["tomato"],
};

const generatedPayload: GeneratedResult = {
  prompt: "Prompt",
  imageUrl: "https://example.com/image.png",
  metadata: { description: "desc", keywords: ["tomato"] },
};

describe("ingredientReducer", () => {
  it("updates the query", () => {
    const next = ingredientReducer(initialIngredientState, {
      type: "setQuery",
      payload: "tomato",
    });
    expect(next.query).toBe("tomato");
  });

  it("sets results", () => {
    const next = ingredientReducer(initialIngredientState, {
      type: "setResults",
      payload: [sampleResult],
    });
    expect(next.results).toEqual([sampleResult]);
  });

  it("adds ingredients without duplicates", () => {
    const first = ingredientReducer(initialIngredientState, {
      type: "addIngredient",
      payload: sampleResult,
    });
    const second = ingredientReducer(first, {
      type: "addIngredient",
      payload: sampleResult,
    });
    expect(second.selectedIngredients).toEqual([sampleResult]);
  });

  it("removes ingredients", () => {
    const state: IngredientState = {
      ...initialIngredientState,
      selectedIngredients: [sampleResult],
    };
    const next = ingredientReducer(state, { type: "removeIngredient", payload: "tomato" });
    expect(next.selectedIngredients).toEqual([]);
  });

  it("clears selection", () => {
    const state: IngredientState = {
      ...initialIngredientState,
      selectedIngredients: [sampleResult],
    };
    const next = ingredientReducer(state, { type: "clearSelection" });
    expect(next.selectedIngredients).toEqual([]);
  });

  it("tracks search status", () => {
    const next = ingredientReducer(initialIngredientState, {
      type: "setSearchStatus",
      payload: "loading",
    });
    expect(next.searchStatus).toBe("loading");
  });

  it("stores search errors", () => {
    const next = ingredientReducer(initialIngredientState, {
      type: "setSearchError",
      payload: "Backend unavailable",
    });
    expect(next.searchError).toBe("Backend unavailable");
  });

  it("tracks generation status", () => {
    const next = ingredientReducer(initialIngredientState, {
      type: "setGenerationStatus",
      payload: "loading",
    });
    expect(next.generationStatus).toBe("loading");
  });

  it("stores generated result", () => {
    const next = ingredientReducer(initialIngredientState, {
      type: "setGeneratedResult",
      payload: generatedPayload,
    });
    expect(next.generatedResult).toEqual(generatedPayload);
  });

  it("resets generated result", () => {
    const state: IngredientState = { ...initialIngredientState, generatedResult: generatedPayload };
    const next = ingredientReducer(state, { type: "resetGeneratedResult" });
    expect(next.generatedResult).toBeNull();
  });
});

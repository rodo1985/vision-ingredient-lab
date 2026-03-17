import "@testing-library/jest-dom";
import { render, screen } from "@testing-library/react";
import { beforeEach, afterEach, vi } from "vitest";

import { App } from "../App";

/**
 * Verify the initial application shell renders the core frontend framing.
 */
describe("App", () => {
  beforeEach(() => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify([]), { status: 200 }),
    );
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("renders the hero heading and workspace panels", () => {
    render(<App />);

    expect(
      screen.getByRole("heading", {
        name: /turn a folder of ingredients into a searchable creative lab/i
      }),
    ).toBeInTheDocument();
    expect(screen.getByRole("region", { name: /ingredient search/i })).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: /curate your component list/i }),
    ).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /generated result/i })).toBeInTheDocument();
  });
});

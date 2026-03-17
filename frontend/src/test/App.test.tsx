import "@testing-library/jest-dom";
import { render, screen } from "@testing-library/react";

import { App } from "../App";

/**
 * Verify the initial application shell renders the core frontend framing.
 */
describe("App", () => {
  it("renders the hero heading and workspace panels", () => {
    render(<App />);

    expect(
      screen.getByRole("heading", {
        name: /turn a folder of ingredients into a searchable creative lab/i
      }),
    ).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /search ingredients/i })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /selected components/i })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /generated result/i })).toBeInTheDocument();
  });
});

import "@testing-library/jest-dom";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { App } from "../App";

const metadataRows = [
  {
    filename: "tomato.png",
    filepath: "/images/tomato.png",
    description: "Fresh tomato",
    keywords: ["tomato", "red"],
    processed_at: "2026-03-17T00:00:00Z",
    last_modified: "2026-03-17T00:00:00Z",
  },
  {
    filename: "basil.png",
    filepath: "/images/basil.png",
    description: "Fragrant basil leaves",
    keywords: ["basil", "herb"],
    processed_at: "2026-03-17T00:00:00Z",
    last_modified: "2026-03-17T00:00:00Z",
  },
];

/**
 * Verify the app can move from metadata loading to a successful generated result.
 */
describe("App integration", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("loads metadata, allows selection, and renders a generated result", async () => {
    const fetchMock = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(new Response(JSON.stringify(metadataRows), { status: 200 }))
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            prompt: "Create a tomato and basil poster",
            image_url: "https://example.com/poster.png",
            metadata: {
              description: "A vibrant tomato and basil composition",
              keywords: ["tomato", "basil"],
            },
          }),
          { status: 200 },
        ),
      );

    render(<App />);

    await waitFor(() => {
      expect(screen.getAllByRole("button", { name: "Add" })).toHaveLength(2);
    }, { timeout: 1500 });

    fireEvent.click(screen.getAllByRole("button", { name: "Add" })[0]);
    fireEvent.click(screen.getAllByRole("button", { name: "Add" })[0]);
    fireEvent.click(screen.getByRole("button", { name: /generate image/i }));

    await waitFor(() => {
      expect(screen.getByRole("img")).toHaveAttribute("src", "https://example.com/poster.png");
    });

    expect(fetchMock).toHaveBeenNthCalledWith(1, "/api/metadata/", { method: "GET" });
    expect(fetchMock).toHaveBeenNthCalledWith(2, "/api/generation", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ingredients: ["Tomato", "Basil"] }),
    });
    expect(screen.getByText(/vibrant tomato and basil composition/i)).toBeInTheDocument();
  });

  it("renders a generation error when the backend request fails", async () => {
    vi.spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(new Response(JSON.stringify(metadataRows), { status: 200 }))
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ detail: "Generation failed" }), { status: 500 }),
      );

    render(<App />);

    await waitFor(() => {
      expect(screen.getAllByRole("button", { name: "Add" })).toHaveLength(2);
    }, { timeout: 1500 });

    fireEvent.click(screen.getAllByRole("button", { name: "Add" })[0]);
    fireEvent.click(screen.getAllByRole("button", { name: "Add" })[0]);
    fireEvent.click(screen.getByRole("button", { name: /generate image/i }));

    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent(/failed to generate image/i);
    });
  });
});

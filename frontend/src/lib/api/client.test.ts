import { describe, expect, it, vi } from "vitest";

import { createApiClient, MetadataRow } from "./client";

describe("createApiClient", () => {
  const sampleMetadata: MetadataRow[] = [
    {
      filename: "tomato.png",
      filepath: "/images/tomato.png",
      description: "A ripe tomato",
      keywords: ["tomato", "red"],
      processed_at: "2026-03-17T00:00:00Z",
      last_modified: "2026-03-16T23:50:00Z",
    },
  ];

  it("fetches metadata listing over GET", async () => {
    const fetcher = vi.fn().mockResolvedValue(
      new Response(JSON.stringify(sampleMetadata), { status: 200 }),
    );
    const client = createApiClient({ baseUrl: "/api", fetcher });

    const rows = await client.listMetadata();

    expect(fetcher).toHaveBeenCalledWith("/api/images", { method: "GET" });
    expect(rows).toEqual(sampleMetadata);
  });

  it("searches metadata by forwarding the query parameter", async () => {
    const expected = sampleMetadata;
    const fetcher = vi.fn().mockResolvedValue(
      new Response(JSON.stringify(expected), { status: 200 }),
    );
    const client = createApiClient({ baseUrl: "/api", fetcher });

    const rows = await client.searchMetadata("tomato");

    expect(fetcher).toHaveBeenCalledWith("/api/search?query=tomato", { method: "GET" });
    expect(rows).toEqual(expected);
  });

  it("rejects empty search queries before making a request", async () => {
    const fetcher = vi.fn();
    const client = createApiClient({ baseUrl: "/api", fetcher });

    await expect(client.searchMetadata("   ")).rejects.toThrow("non-empty query");
    expect(fetcher).not.toHaveBeenCalled();
  });

  it("creates images by posting the payload and mapping the response", async () => {
    const fetcher = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          prompt: "Make a pizza",
          image_url: "https://example.com/pizza.png",
          model: "gpt-image-1",
        }),
        { status: 200 },
      ),
    );
    const client = createApiClient({ baseUrl: "/api", fetcher });

    const response = await client.generateImage({ ingredients: ["tomato", "basil"] });

    expect(fetcher).toHaveBeenCalledWith("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ selected_ingredients: ["tomato", "basil"] }),
    });
    expect(response.imageUrl).toBe("https://example.com/pizza.png");
    expect(response.metadata).toEqual({ description: undefined, keywords: undefined });
  });

  it("maps base64 generation payloads into a browser-safe data URL", async () => {
    const fetcher = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          prompt: "Paint basil leaves",
          image_base64: "ZmFrZS1kYXRh",
        }),
        { status: 200 },
      ),
    );
    const client = createApiClient({ baseUrl: "/api", fetcher });

    const response = await client.generateImage({ ingredients: ["basil", "tomato"] });

    expect(response.imageUrl).toBe("data:image/png;base64,ZmFrZS1kYXRh");
  });
});

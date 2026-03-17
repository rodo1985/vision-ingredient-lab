import { describe, expect, it, vi } from "vitest";

import { httpClient } from "../httpClient";

describe("httpClient", () => {
  it("prefixes backend-relative image URLs with the API base URL", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          items: [
            {
              id: "img_1",
              filename: "tomato.png",
              imageUrl: "/data/images/tomato.png",
              description: "Tomato",
              tags: ["tomato"],
              lastModified: "2026-03-17T00:00:00Z",
              status: "ready",
            },
          ],
          total: 1,
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          generationId: "gen_1",
          imageUrl: "/data/generated/gen_1.png",
          prompt: "selected ingredients only",
          ingredientIds: ["img_1"],
          createdAt: "2026-03-17T00:00:00Z",
        }),
      });

    vi.stubGlobal("fetch", fetchMock);

    const images = await httpClient.getImages();
    const generated = await httpClient.generate({ ingredientIds: ["img_1"] });

    expect(images.items[0]?.imageUrl).toBe("http://localhost:8000/data/images/tomato.png");
    expect(generated.imageUrl).toBe("http://localhost:8000/data/generated/gen_1.png");
  });
});

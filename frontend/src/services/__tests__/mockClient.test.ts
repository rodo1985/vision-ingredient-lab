import { describe, expect, it } from "vitest";

import { mockClient } from "../mockClient";

describe("mockClient", () => {
  it("returns contract-compatible image and search data", async () => {
    const images = await mockClient.getImages();
    const search = await mockClient.search("tomato");

    expect(images.total).toBeGreaterThan(0);
    expect(images.items[0]).toHaveProperty("id");
    expect(images.items[0]).toHaveProperty("imageUrl");
    expect(search.query).toBe("tomato");
    expect(Array.isArray(search.items)).toBe(true);
  });
});

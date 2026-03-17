import type { ApiClient } from "./client";
import type { GenerateRequest } from "../types/api";
import {
  mockConfig,
  mockGenerationResponse,
  mockImages,
  mockSearchResults,
  mockSyncResponse,
} from "../mocks/data";

function delay<T>(value: T, ms = 200): Promise<T> {
  return new Promise((resolve) => {
    setTimeout(() => resolve(value), ms);
  });
}

export const mockClient: ApiClient = {
  async getConfig() {
    return delay(mockConfig);
  },
  async getImages() {
    return delay(mockImages);
  },
  async search(query: string) {
    if (!query.trim()) {
      return delay({ query, items: mockImages.items.map((image) => ({ image, score: 0.5, matchReasons: ["semantic"], matchedTags: [] })) });
    }
    return delay({
      ...mockSearchResults,
      query,
      items: mockImages.items
        .filter((image) => image.tags.some((tag) => tag.includes(query.toLowerCase())))
        .map((image) => ({
          image,
          score: image.tags.includes(query.toLowerCase()) ? 0.95 : 0.55,
          matchReasons: image.tags.includes(query.toLowerCase()) ? ["keyword", "semantic"] : ["semantic"],
          matchedTags: image.tags.filter((tag) => tag.includes(query.toLowerCase())),
        })),
    });
  },
  async sync() {
    return delay(mockSyncResponse);
  },
  async generate(request: GenerateRequest) {
    return delay({
      ...mockGenerationResponse,
      ingredientIds: request.ingredientIds,
      prompt: request.creativeDirection
        ? `${mockGenerationResponse.prompt} Direction: ${request.creativeDirection}`
        : mockGenerationResponse.prompt,
    }, 500);
  },
};

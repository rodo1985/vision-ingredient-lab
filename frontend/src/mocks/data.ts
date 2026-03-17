import type { AppConfig, GenerateResponse, ImageListResponse, SearchResponse, SyncResponse } from "../types/api";

export const mockConfig: AppConfig = {
  mode: "mock",
  enableStartupSync: true,
  maxSearchResults: 20,
};

export const mockImages: ImageListResponse = {
  items: [
    {
      id: "img_tomato_01",
      filename: "tomato.jpg",
      imageUrl: "https://images.unsplash.com/photo-1546094096-0df4bcaaa337?auto=format&fit=crop&w=500&q=80",
      description: "A bright red tomato ingredient photo.",
      tags: ["tomato", "fresh", "red"],
      lastModified: "2026-03-16T18:30:00Z",
      status: "ready",
    },
    {
      id: "img_basil_01",
      filename: "basil.jpg",
      imageUrl: "https://images.unsplash.com/photo-1615485925600-97237c4fc1ec?auto=format&fit=crop&w=500&q=80",
      description: "Fresh basil leaves gathered in a bunch.",
      tags: ["basil", "green", "herb"],
      lastModified: "2026-03-16T18:35:00Z",
      status: "ready",
    },
    {
      id: "img_mozzarella_01",
      filename: "mozzarella.jpg",
      imageUrl: "https://images.unsplash.com/photo-1625943555419-56a2cb596640?auto=format&fit=crop&w=500&q=80",
      description: "Soft mozzarella cheese prepared for cooking.",
      tags: ["mozzarella", "cheese", "white"],
      lastModified: "2026-03-16T18:40:00Z",
      status: "ready",
    }
  ],
  total: 3,
};

export const mockSearchResults: SearchResponse = {
  query: "tomato",
  items: [
    {
      image: mockImages.items[0],
      score: 0.96,
      matchReasons: ["keyword", "semantic"],
      matchedTags: ["tomato"],
    },
  ],
};

export const mockSyncResponse: SyncResponse = {
  scannedCount: 3,
  newCount: 0,
  updatedCount: 0,
  failedCount: 0,
  startedAt: "2026-03-16T18:30:00Z",
  completedAt: "2026-03-16T18:30:01Z",
};

export const mockGenerationResponse: GenerateResponse = {
  generationId: "gen_20260316_183005",
  imageUrl: "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=800&q=80",
  prompt: "Create a food composition combining tomato, mozzarella, and basil in a rustic pizza-inspired plating.",
  ingredientIds: ["img_tomato_01", "img_basil_01", "img_mozzarella_01"],
  createdAt: "2026-03-16T18:30:05Z",
};

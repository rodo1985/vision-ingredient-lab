export type ImageStatus = "ready" | "processing" | "stale" | "error";

export interface ImageRecord {
  id: string;
  filename: string;
  imageUrl: string;
  description: string;
  tags: string[];
  lastModified: string;
  status: ImageStatus;
}

export interface SearchResult {
  image: ImageRecord;
  score: number;
  matchReasons: string[];
  matchedTags: string[];
}

export interface SearchResponse {
  query: string;
  items: SearchResult[];
}

export interface ImageListResponse {
  items: ImageRecord[];
  total: number;
}

export interface SyncResponse {
  scannedCount: number;
  newCount: number;
  updatedCount: number;
  failedCount: number;
  startedAt: string;
  completedAt: string;
}

export interface GenerateRequest {
  ingredientIds: string[];
  creativeDirection?: string;
}

export interface GenerateResponse {
  generationId: string;
  imageUrl: string;
  prompt: string;
  ingredientIds: string[];
  createdAt: string;
}

export interface AppConfig {
  mode: "mock" | "api";
  enableStartupSync: boolean;
  maxSearchResults: number;
}

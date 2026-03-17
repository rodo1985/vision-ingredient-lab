import type { ApiClient } from "./client";
import type {
  AppConfig,
  GenerateRequest,
  GenerateResponse,
  ImageRecord,
  ImageListResponse,
  SearchResponse,
  SearchResult,
  SyncResponse,
} from "../types/api";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

function resolveAssetUrl(assetUrl: string): string {
  if (/^https?:\/\//.test(assetUrl)) {
    return assetUrl;
  }
  if (assetUrl.startsWith("/")) {
    return `${API_BASE_URL}${assetUrl}`;
  }
  return assetUrl;
}

function normalizeImageRecord(image: ImageRecord): ImageRecord {
  return {
    ...image,
    imageUrl: resolveAssetUrl(image.imageUrl),
  };
}

function normalizeSearchResult(result: SearchResult): SearchResult {
  return {
    ...result,
    image: normalizeImageRecord(result.image),
  };
}

async function requestJson<T>(path: string, options?: RequestInit): Promise<T> {
  const hasBody = options?.body !== undefined;
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: hasBody
      ? {
          "Content-Type": "application/json",
          ...(options?.headers ?? {}),
        }
      : options?.headers,
    ...options,
  });
  if (!response.ok) {
    throw new Error(`Request failed for ${path}`);
  }
  return response.json() as Promise<T>;
}

export const httpClient: ApiClient = {
  getConfig(): Promise<AppConfig> {
    return requestJson<AppConfig>("/api/config");
  },
  async getImages(): Promise<ImageListResponse> {
    const response = await requestJson<ImageListResponse>("/api/images");
    return {
      ...response,
      items: response.items.map(normalizeImageRecord),
    };
  },
  async search(query: string): Promise<SearchResponse> {
    const response = await requestJson<SearchResponse>(`/api/search?q=${encodeURIComponent(query)}`);
    return {
      ...response,
      items: response.items.map(normalizeSearchResult),
    };
  },
  sync(): Promise<SyncResponse> {
    return requestJson<SyncResponse>("/api/startup/sync", { method: "POST" });
  },
  async generate(request: GenerateRequest): Promise<GenerateResponse> {
    const response = await requestJson<GenerateResponse>("/api/generate", {
      method: "POST",
      body: JSON.stringify(request),
    });
    return {
      ...response,
      imageUrl: resolveAssetUrl(response.imageUrl),
    };
  },
};

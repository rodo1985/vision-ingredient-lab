import type { ApiClient } from "./client";
import type {
  AppConfig,
  GenerateRequest,
  GenerateResponse,
  ImageListResponse,
  SearchResponse,
  SyncResponse,
} from "../types/api";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

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
  getImages(): Promise<ImageListResponse> {
    return requestJson<ImageListResponse>("/api/images");
  },
  search(query: string): Promise<SearchResponse> {
    return requestJson<SearchResponse>(`/api/search?q=${encodeURIComponent(query)}`);
  },
  sync(): Promise<SyncResponse> {
    return requestJson<SyncResponse>("/api/startup/sync", { method: "POST" });
  },
  generate(request: GenerateRequest): Promise<GenerateResponse> {
    return requestJson<GenerateResponse>("/api/generate", {
      method: "POST",
      body: JSON.stringify(request),
    });
  },
};

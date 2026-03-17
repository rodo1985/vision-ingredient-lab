import type {
  AppConfig,
  GenerateRequest,
  GenerateResponse,
  ImageListResponse,
  SearchResponse,
  SyncResponse,
} from "../types/api";

export interface ApiClient {
  getConfig(): Promise<AppConfig>;
  getImages(): Promise<ImageListResponse>;
  search(query: string): Promise<SearchResponse>;
  sync(): Promise<SyncResponse>;
  generate(request: GenerateRequest): Promise<GenerateResponse>;
}

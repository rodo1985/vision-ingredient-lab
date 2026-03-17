/**
 * Minimal typed client that wraps the Vision Ingredient Lab backend API.
 */

/** Fetch-like function signature used by the API client. */
export type ApiFetcher = (input: RequestInfo, init?: RequestInit) => Promise<Response>;

/**
 * Ingredient metadata row that mirrors the backend CSV structure.
 */
export interface MetadataRow {
  filename: string;
  filepath: string;
  description: string;
  keywords: string[];
  processed_at: string;
  last_modified: string;
}

/**
 * Payload sent to the generation endpoint describing which ingredients to combine.
 */
export interface GenerationRequest {
  ingredients: string[];
  size?: string;
}

/**
 * Response returned after a successful generation request.
 */
export interface GenerationResponse {
  prompt: string;
  imageUrl: string;
  metadata: {
    description?: string;
    keywords?: string[];
  };
}

/**
 * Public surface of the Vision Ingredient Lab API client.
 */
export interface ApiClient {
  listMetadata(): Promise<MetadataRow[]>;
  searchMetadata(query: string): Promise<MetadataRow[]>;
  generateImage(request: GenerationRequest): Promise<GenerationResponse>;
}

/**
 * Optional overrides that customize how the API client builds requests.
 */
export interface ApiClientOptions {
  baseUrl?: string;
  fetcher?: ApiFetcher;
}

const DEFAULT_BASE_URL = "/api";

/**
 * Normalize the provided base URL so that joining it with relative paths is deterministic.
 */
function normalizeBaseUrl(rawBaseUrl: string): string {
  const stripped = rawBaseUrl.replace(/\/+$|\.$/g, "");
  return stripped === "" ? "" : stripped;
}

/**
 * Join a base URL with an endpoint path while avoiding double slashes.
 */
function composeEndpoint(baseUrl: string, path: string): string {
  const normalizedBase = normalizeBaseUrl(baseUrl);
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return normalizedBase === "" ? normalizedPath : `${normalizedBase}${normalizedPath}`;
}

/**
 * Parse the response body as JSON or raise a contextual error for non-2xx results.
 */
async function parseResponse<T>(response: Response, context: string): Promise<T> {
  if (!response.ok) {
    const body = await response.text();
    const suffix = body ? `: ${body}` : "";
    throw new Error(`Failed to ${context} (${response.status} ${response.statusText})${suffix}`);
  }
  return response.json() as Promise<T>;
}

/** Default browser fetch implementation used when no override is supplied. */
function defaultFetcher(input: RequestInfo, init?: RequestInit): Promise<Response> {
  return fetch(input, init);
}

/**
 * Create an API client that talks to the Vision Ingredient Lab backend.
 *
 * @param options Optional overrides for base URL and fetch implementation.
 * @returns A client exposing metadata listing, search, and generation helpers.
 */
export function createApiClient(options?: ApiClientOptions): ApiClient {
  const baseUrl = options?.baseUrl ?? DEFAULT_BASE_URL;
  const fetcher = options?.fetcher ?? defaultFetcher;

  return {
    async listMetadata(): Promise<MetadataRow[]> {
      const endpoint = composeEndpoint(baseUrl, "/metadata/");
      const response = await fetcher(endpoint, { method: "GET" });
      return parseResponse<MetadataRow[]>(response, "list metadata");
    },

    async searchMetadata(query: string): Promise<MetadataRow[]> {
      if (!query.trim()) {
        throw new Error("searchMetadata requires a non-empty query");
      }
      const endpoint = composeEndpoint(baseUrl, "/metadata/search");
      const url = `${endpoint}?q=${encodeURIComponent(query)}`;
      const response = await fetcher(url, { method: "GET" });
      return parseResponse<MetadataRow[]>(response, "search metadata");
    },

    async generateImage(request: GenerationRequest): Promise<GenerationResponse> {
      const endpoint = composeEndpoint(baseUrl, "/generation");
      const response = await fetcher(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(request),
      });
      const body = await parseResponse<GenerationResponsePayload>(response, "generate image");
      return {
        prompt: body.prompt,
        imageUrl: body.image_url,
        metadata: {
          description: body.metadata?.description,
          keywords: body.metadata?.keywords,
        },
      };
    },
  };
}

/**
 * Convenience client wired with the default `/api` base path.
 */
export const defaultApiClient = createApiClient();

/**
 * Internal shape that models the backend generation response.
 */
interface GenerationResponsePayload {
  prompt: string;
  image_url: string;
  metadata?: {
    description?: string;
    keywords?: string[];
  };
}

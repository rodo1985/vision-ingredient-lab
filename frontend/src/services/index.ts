import type { ApiClient } from "./client";
import { httpClient } from "./httpClient";
import { mockClient } from "./mockClient";

export async function resolveApiClient(): Promise<ApiClient> {
  try {
    await httpClient.getConfig();
    return httpClient;
  } catch {
    return mockClient;
  }
}

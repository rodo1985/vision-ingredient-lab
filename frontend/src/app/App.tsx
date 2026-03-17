import { useEffect, useMemo, useState } from "react";

import { GeneratedResult } from "../components/GeneratedResult";
import { GeneratePanel } from "../components/GeneratePanel";
import { ImageGrid } from "../components/ImageGrid";
import { SearchBar } from "../components/SearchBar";
import { SelectedIngredients } from "../components/SelectedIngredients";
import { useDebouncedValue } from "../hooks/useDebouncedValue";
import type { ApiClient } from "../services/client";
import { mockClient } from "../services/mockClient";
import { resolveApiClient } from "../services";
import type { AppConfig, GenerateResponse, ImageRecord, SearchResult, SyncResponse } from "../types/api";

export function App() {
  const [client, setClient] = useState<ApiClient>(mockClient);
  const [config, setConfig] = useState<AppConfig | null>(null);
  const [syncStatus, setSyncStatus] = useState<SyncResponse | null>(null);
  const [query, setQuery] = useState("");
  const debouncedQuery = useDebouncedValue(query, 250);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [images, setImages] = useState<ImageRecord[]>([]);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [creativeDirection, setCreativeDirection] = useState("");
  const [generatedResult, setGeneratedResult] = useState<GenerateResponse | null>(null);
  const [generationError, setGenerationError] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);

  useEffect(() => {
    async function loadInitialData() {
      const resolvedClient = await resolveApiClient();
      setClient(resolvedClient);
      const [loadedConfig, loadedImages, loadedSync] = await Promise.all([
        resolvedClient.getConfig(),
        resolvedClient.getImages(),
        resolvedClient.sync(),
      ]);
      setConfig(loadedConfig);
      setImages(loadedImages.items);
      setSyncStatus(loadedSync);
      setResults(
        loadedImages.items.map((image) => ({
          image,
          score: 0.5,
          matchReasons: ["semantic"],
          matchedTags: [],
        })),
      );
    }

    void loadInitialData();
  }, []);

  useEffect(() => {
    async function runSearch() {
      if (!config) {
        return;
      }
      const response = await client.search(debouncedQuery);
      setResults(response.items);
    }

    void runSearch();
  }, [client, config, debouncedQuery]);

  const selectedItems = useMemo(
    () => images.filter((image) => selectedIds.includes(image.id)),
    [images, selectedIds],
  );

  function toggleSelection(imageId: string) {
    setSelectedIds((current) =>
      current.includes(imageId) ? current.filter((id) => id !== imageId) : [...current, imageId],
    );
  }

  async function handleGenerate() {
    try {
      setIsGenerating(true);
      setGenerationError(null);
      const response = await client.generate({
        ingredientIds: selectedIds,
        creativeDirection: creativeDirection || undefined,
      });
      setGeneratedResult(response);
    } catch (error) {
      setGenerationError(error instanceof Error ? error.message : "Generation failed.");
    } finally {
      setIsGenerating(false);
    }
  }

  return (
    <main className="appShell">
      <header className="hero">
        <p className="eyebrow">Vision Ingredient Lab</p>
        <h1>Ingredient search, selection, and creative generation.</h1>
        <p className="heroCopy">
          Build the frontend independently in mock mode, then switch to the backend contract without
          changing the UI flow.
        </p>
      </header>

      <section className="statusBanner">
        <strong>Mode:</strong> {config?.mode ?? "loading"} | <strong>Last sync:</strong>{" "}
        {syncStatus?.completedAt ?? "loading"}
      </section>

      <SearchBar value={query} onChange={setQuery} />
      <ImageGrid items={results} selectedIds={selectedIds} onToggle={toggleSelection} />
      <SelectedIngredients items={selectedItems} onRemove={toggleSelection} />
      <GeneratePanel
        creativeDirection={creativeDirection}
        disabled={selectedIds.length === 0}
        loading={isGenerating}
        onChange={setCreativeDirection}
        onGenerate={() => void handleGenerate()}
      />
      <GeneratedResult error={generationError} result={generatedResult} />
    </main>
  );
}

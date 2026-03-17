import type { GenerateResponse } from "../types/api";

interface GeneratedResultProps {
  result: GenerateResponse | null;
  error: string | null;
}

export function GeneratedResult({ result, error }: GeneratedResultProps) {
  return (
    <section className="panel">
      <h2 className="panelTitle">Generated output</h2>
      {error ? <p className="errorText">{error}</p> : null}
      {result ? (
        <div className="generatedResult">
          <img alt={result.generationId} className="generatedImage" src={result.imageUrl} />
          <p>{result.prompt}</p>
        </div>
      ) : (
        <p>No generation yet.</p>
      )}
    </section>
  );
}

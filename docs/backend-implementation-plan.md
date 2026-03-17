# Vision Ingredient Lab Backend Implementation Plan

## Document Purpose
This plan defines the backend implementation order, task dependencies, and parallelization strategy for **Vision Ingredient Lab**.

It is designed to let multiple engineers work simultaneously while preserving a safe dependency order.

## Project Context
Vision Ingredient Lab backend responsibilities:

- Scan a local folder for ingredient images.
- Detect newly added images on startup.
- Generate image descriptions and ingredient keywords with OpenAI vision models.
- Persist metadata in CSV.
- Expose search/filter APIs for the frontend.
- Accept selected ingredients and generate a creative image using an OpenAI image model.

## Epic and Jira Mapping
- Epic: **AIIP-31** (`vision-ingredient-lab`)

Tasks created under the Epic:

- **AIIP-32**: `[Backend] Project bootstrap with uv + config foundation`
- **AIIP-33**: `[Backend] Image dataset scanner service`
- **AIIP-34**: `[Backend] CSV metadata repository (read/write/append/update)`
- **AIIP-35**: `[Backend] Startup sync: detect and process only new images`
- **AIIP-36**: `[Backend] OpenAI vision client for description + keyword extraction`
- **AIIP-37**: `[Backend] Metadata enrichment pipeline for new images`
- **AIIP-38**: `[Backend] REST API: metadata and search endpoints`
- **AIIP-39**: `[Backend] Search service over ingredient metadata`
- **AIIP-40**: `[Backend] REST API: ingredient selection and image generation endpoint`
- **AIIP-41**: `[Backend] Prompt builder for ingredient composition`
- **AIIP-42**: `[Backend] Automated tests for ingestion, metadata, search, and generation flow`
- **AIIP-43**: `[Backend] README and backend documentation updates`

## Recommended Backend Structure
Suggested Python backend structure:

```text
backend/
  app/
    api/
      routes_search.py
      routes_generation.py
    core/
      config.py
      logging.py
    services/
      scanner.py
      metadata_repository.py
      vision_client.py
      prompt_builder.py
      enrichment_pipeline.py
      search_service.py
      generation_service.py
    models/
      metadata.py
    main.py
  tests/
    test_scanner.py
    test_metadata_repository.py
    test_startup_sync.py
    test_vision_client.py
    test_search_service.py
    test_prompt_builder.py
docs/
```

## Execution Waves (Order + Parallelization)

### Wave 1: Foundation and independent modules (parallel)
Run these in parallel.

- **AIIP-32**: project skeleton, uv setup, config, logging.
- **AIIP-33**: image scanner.
- **AIIP-34**: CSV metadata repository.
- **AIIP-36**: OpenAI vision client.
- **AIIP-41**: prompt builder.

Why parallel is safe:
- No hard runtime dependencies between these tasks.
- They define reusable building blocks for later integration tasks.

### Wave 2: Core feature assembly (partly parallel)
Start as soon as dependent Wave 1 tasks are complete.

- **AIIP-35** depends on **AIIP-33 + AIIP-34**.
- **AIIP-39** depends on **AIIP-34**.
- **AIIP-40** depends on **AIIP-41** and API app skeleton from **AIIP-32**.

Why parallel is safe:
- Startup sync, search service, and generation endpoint target different modules with minimal overlap.

### Wave 3: Integrated backend APIs (parallel after prerequisites)

- **AIIP-37** depends on **AIIP-35 + AIIP-36 + AIIP-34**.
- **AIIP-38** depends on **AIIP-39** and API skeleton from **AIIP-32**.

Why parallel is safe:
- Enrichment pipeline and search API touch different functional lanes.

### Wave 4: Hardening and documentation

- **AIIP-42** (tests): begin alongside each task and finalize after Wave 3.
- **AIIP-43** (README/docs): draft early, finalize once APIs and behavior are stable.

## Dependency Matrix

| Task | Depends On | Parallel Lane |
|---|---|---|
| AIIP-32 | None | Platform |
| AIIP-33 | AIIP-32 | Ingestion |
| AIIP-34 | AIIP-32 | Storage |
| AIIP-36 | AIIP-32 | AI Integration |
| AIIP-41 | AIIP-32 | Generation |
| AIIP-35 | AIIP-33, AIIP-34 | Ingestion |
| AIIP-39 | AIIP-34 | Search |
| AIIP-40 | AIIP-41, AIIP-32 | Generation/API |
| AIIP-37 | AIIP-35, AIIP-36, AIIP-34 | Orchestration |
| AIIP-38 | AIIP-39, AIIP-32 | API/Search |
| AIIP-42 | AIIP-32..AIIP-41 | QA |
| AIIP-43 | AIIP-32..AIIP-42 | Docs |

## Suggested Team Parallelization
If 4 engineers are available:

- Engineer A: Platform + API skeleton (AIIP-32), then AIIP-38.
- Engineer B: Ingestion/Storage (AIIP-33, AIIP-34, AIIP-35, AIIP-37).
- Engineer C: AI and generation flow (AIIP-36, AIIP-41, AIIP-40).
- Engineer D: Search + tests + docs (AIIP-39, AIIP-42, AIIP-43).

## API Scope (Backend)
Primary backend endpoints:

- `GET /health`
- `GET /api/images`
- `GET /api/search?query=<term>`
- `POST /api/generate`

## Data Contract (CSV)
CSV columns:

- `filename`
- `filepath`
- `description`
- `keywords`
- `processed_at`
- `last_modified`

Implementation note:
- `keywords` should be stored as a deterministic serialized value (for example, comma-separated or JSON string) to simplify parse and search behavior.

## Configuration Plan
Environment variables expected:

- `OPENAI_API_KEY`
- `OPENAI_VISION_MODEL` (optional override)
- `OPENAI_IMAGE_MODEL` (optional override)
- `IMAGE_DATASET_DIR`
- `METADATA_CSV_PATH`

## Testing Strategy
Minimum coverage expectations:

- Scanner handles empty folders and mixed file types.
- CSV repository supports read/write/append without duplicate records.
- Startup sync identifies only new/unprocessed files.
- Vision client parses structured response and handles failures.
- Search service returns relevant matches for ingredient terms.
- Generation endpoint validates input and returns deterministic response schema.

## Definition of Done
A task is done when:

- Implementation matches ticket scope.
- Functions/classes include docstrings and clear type hints.
- Non-obvious logic has inline comments explaining "why".
- Tests are added/updated and pass locally.
- Docs are updated where behavior or setup changed.

## Local Commands (`uv` workflow)

```bash
uv venv
uv sync
uv run pytest
uv run ruff check .
uv run uvicorn backend.app.main:app --reload
```

## Risks and Mitigation

- Risk: CSV schema drift across contributors.
  - Mitigation: central metadata repository with schema validation.
- Risk: repeated image processing across restarts.
  - Mitigation: startup diff logic keyed by file path + modification timestamp.
- Risk: unstable model outputs.
  - Mitigation: strict parsing, retries, and fallback error handling.
- Risk: temporary duplication between the primary backend app and the preserved legacy slice.
  - Mitigation: keep their tests separate until the consolidation work is explicitly scheduled.

## Next Implementation Step
Start with **AIIP-32** and create a baseline backend app skeleton plus uv setup. This unlocks all parallel lanes safely.

# Backend Implementation Definition

## Goal

Build a Python backend with FastAPI and `uv` that can ingest local ingredient images, enrich them with OpenAI-generated metadata, persist canonical CSV records, derive a local embeddings sidecar for semantic search, and synchronously generate a new creative image from selected ingredients.

## Runtime and Tooling

- Python 3.11+
- Dependency management: `uv`
- Web framework: FastAPI
- Test framework: `pytest`
- HTTP client for OpenAI: official `openai` Python SDK

## Primary Modules

### API layer

- `app/main.py`: FastAPI app creation and router registration
- `app/api/routes.py`: public HTTP endpoints

### Core configuration

- `app/core/config.py`: environment-based settings for data paths, feature flags, and OpenAI model names

### Models

- `app/models/api.py`: request and response schemas shared across routes
- `app/models/domain.py`: internal record models for metadata and search

### Repositories

- `app/repositories/metadata_store.py`: CSV persistence for canonical metadata rows
- `app/repositories/embedding_store.py`: JSONL persistence for derived embedding rows

### Services

- `app/services/folder_scanner.py`: detect new, changed, and stale image files
- `app/services/metadata_extractor.py`: analyze images with OpenAI Responses and normalize tags
- `app/services/generation.py`: create image prompts and call OpenAI Images
- `app/services/sync_service.py`: orchestrate scanning, metadata writes, and embedding refresh

### Search

- `app/search/embeddings.py`: embedding client interface and cosine similarity utilities
- `app/search/hybrid_search.py`: combine exact-match and semantic scores into ranked results

## Canonical Data

### CSV source of truth

Store image metadata in `backend/data/metadata/image_metadata.csv` with these columns:

- `image_id`
- `filename`
- `filepath`
- `file_url`
- `mime_type`
- `description`
- `tags`
- `search_text`
- `processed_at`
- `last_modified`
- `embedding_version`
- `model_version`
- `status`
- `error_message`

Notes:

- `tags` uses a `|` delimiter in CSV.
- `search_text` is derived from filename, description, and tags for embedding generation.
- deleted files are marked `stale` instead of removed in v1.

### Embedding sidecar

Store derived vectors in `backend/data/metadata/image_metadata.embeddings.jsonl`.

Each line should contain:

- `image_id`
- `vector`
- `embedding_version`
- `updated_at`

## OpenAI Integration

Use current official APIs:

- image analysis: Responses API with image input
- semantic embeddings: Embeddings API with `text-embedding-3-small`
- image generation: Images API using the GPT image line configured in settings

Implementation expectations:

- wrap OpenAI SDK calls behind service classes so tests can mock them cleanly
- request structured JSON for metadata extraction
- keep prompts deterministic and ingredient-focused
- expose model names through configuration, not hard-coded route logic

## Endpoints

Defined in [api-contract.md](/Users/REDONSX1/Documents/training/Codex/code/vision-ingredient-lab/docs/implementation/api-contract.md):

- `GET /health`
- `POST /api/startup/sync`
- `GET /api/images`
- `GET /api/images/{image_id}`
- `GET /api/search`
- `POST /api/generate`
- `GET /api/config`

## Search Design

Hybrid ranking logic:

1. Normalize the query.
2. Score exact matches against tags and description tokens.
3. Generate a query embedding with `text-embedding-3-small`.
4. Compute cosine similarity against active image vectors.
5. Combine scores using a weighted sum.
6. Return deterministic ordering using score, exact-match strength, then filename.

Suggested default weighting:

- keyword score: `0.65`
- semantic score: `0.35`

Return match reasons so the frontend can explain why a result appeared.

## Tests

Required unit coverage:

- folder scanner new, unchanged, modified, and stale detection
- metadata CSV round-trip
- metadata extraction response parsing
- embedding index writes only active rows
- hybrid ranking behavior
- prompt building for generation
- route payload and validation behavior

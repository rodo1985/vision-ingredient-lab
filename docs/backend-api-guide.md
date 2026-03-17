# Backend API Guide

## Overview
The primary Vision Ingredient Lab backend exposes a FastAPI surface for metadata inspection, keyword search, and creative image generation. This guide covers the repo-root `uv` workflow, the current API contract, and the main backend modules that power it.

## Setup
1. Ensure [`uv`](https://docs.astral.sh/uv/) is installed.
2. From the repository root, create the Python environment: `uv venv`.
3. Sync runtime and development dependencies: `uv sync`.

## Running the API
- Start the primary API locally: `uv run uvicorn backend.app.main:app --reload`.
- The server listens on `http://127.0.0.1:8000` by default.
- A health check is available at `GET /health`.

## Required Environment Variables
- `OPENAI_API_KEY`: OpenAI API key for startup enrichment and generation requests.
- `OPENAI_VISION_MODEL`: Optional vision model override (default: `gpt-4.1-mini`).
- `OPENAI_IMAGE_MODEL`: Optional image generation model override (default: `gpt-image-1`).
- `IMAGE_DATASET_DIR`: Path to the ingredient image folder.
- `METADATA_CSV_PATH`: Path to the metadata CSV file.
- `APP_ENV`: Optional environment label used in logging.

## Endpoint Reference
- `GET /health`: Returns `{"status": "ok"}` to indicate the API is running.
- `GET /api/images`: Lists all metadata rows stored in the CSV repository.
- `GET /api/search?query=<term>`: Searches metadata entries with case-insensitive keyword and description matching.
- `POST /api/generate`: Accepts JSON like `{ "selected_ingredients": ["tomato", "basil"] }` and returns the generated prompt plus either `image_url` or `image_base64`.

Example generation request:

```json
{
  "selected_ingredients": ["tomato", "basil"],
  "base_style": "editorial food photography",
  "creativity": 0.7
}
```

## Developer Notes
- The primary API wiring lives in `backend/app/main.py`; route modules live under `backend/app/api/`.
- Metadata routes use `backend/app/services/metadata_repository.py` and `backend/app/services/search_service.py`.
- Generation relies on `backend/app/services/generation_service.py` and the dependency providers in `backend/app/api/dependencies.py`.
- The repository still contains a preserved legacy backend stack under `backend/api` and related modules. Keep that slice covered by its own legacy tests until consolidation work is scheduled.
- Useful targeted checks:
  - `uv run pytest backend/tests/test_main.py backend/tests/test_search_api.py backend/tests/test_generation_api.py`
  - `uv run pytest backend/tests/test_legacy_generation_api.py backend/tests/test_legacy_search_service.py`

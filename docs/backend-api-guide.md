# Backend API Guide

## Overview
The Vision Ingredient Lab backend exposes a FastAPI-based surface for metadata inspection and creative generation. This guide covers how to configure the environment, run the API server, and exercise the available endpoints.

## Setup
1. Ensure [`uv`](https://docs.astral.sh/uv/) is installed.
2. Create the Python environment: `uv venv`.
3. Sync dependencies (production + dev): `uv sync --dev`.

## Running the API
- Start the API locally: `uv run python -m backend.app.api_main`.
- The server listens on `http://127.0.0.1:8000` by default.
- A health check is available at `GET /health`.

## Required Environment Variables
- `OPENAI_API_KEY`: (required) OpenAI API key for vision and generation clients.
- `VISION_IMAGES_DIR`: Path to ingredient image folder (default: `data/images`).
- `VISION_METADATA_CSV`: Path to metadata CSV (default: `data/metadata.csv`).
- `OPENAI_VISION_MODEL`: Vision model name (default: `gpt-4.1-mini`).
- `OPENAI_IMAGE_MODEL`: Image generation model name (default: `gpt-image-1`).
- `OPENAI_MAX_RETRIES`: Retry count for OpenAI clients (default: `2`).

## Endpoint Reference
- `GET /health`: Returns `{"status": "ok"}` to indicate the API is running.
- `GET /api/metadata/`: Lists all metadata rows stored in the CSV (`filename`, `filepath`, `description`, `keywords`, `processed_at`, `last_modified`).
- `GET /api/metadata/search?q=<term>`: Searches metadata entries with case-insensitive keyword or description matching; returns results sorted by keyword relevance then filepath.
- `POST /api/generation`: Accepts JSON `{ "ingredients": ["tomato", "basil"], "size": "512x512" }`; responds with the generated `prompt`, `image_url`, and attached metadata.

## Developer Notes
- The API wiring lives in `backend/api/app.py`; new routers can be mounted in the `create_app` factory.
- Metadata routes use the CSV repository (`backend/metadata_repository.py`) and the search helper (`backend/search/service.py`).
- Generation relies on `backend/clients/image_generation_client.py`, which is easy to mock via the `ImageService` protocol for testing.
- Run targeted tests with `uv run pytest backend/tests/test_metadata_api.py` and `uv run pytest backend/tests/test_generation_api.py`.

# vision-ingredient-lab

Vision Ingredient Lab is a small full-stack prototype for exploring ingredient images with AI.
The backend scans a local image folder, enriches new files with AI-generated metadata, stores
that metadata in CSV, and exposes API endpoints the frontend can use for search and generation.

## What this repo is

This repository is the foundation for an image-driven ingredient exploration workflow.
It is intended to stay simple and contributor-friendly while we build the backend and frontend in
small, parallelizable slices.

## Key features / scope

- Scan a local dataset of ingredient images.
- Detect newly added images without reprocessing the entire dataset.
- Generate descriptions and keywords for images using OpenAI models.
- Persist metadata in a lightweight CSV store.
- Provide API endpoints for search and creative image generation.
- Support a separate React frontend.
- Not in scope yet: production deployment, authentication, and large-scale indexing.

## Setup

### Prerequisites

- Python `3.11+`
- `uv` installed locally

### Environment setup

```bash
uv venv
uv sync
```

## How to run

### Start the backend API

```bash
uv run uvicorn backend.app.main:app --reload
```

### Run tests

```bash
uv run pytest
```

### Run lint checks

```bash
uv run ruff check .
```

## Configuration

The backend reads configuration from environment variables and optionally a local `.env` file.

- `OPENAI_API_KEY`: OpenAI API key for model-backed features.
- `OPENAI_VISION_MODEL`: Optional override for the image understanding model.
- `OPENAI_IMAGE_MODEL`: Optional override for the image generation model.
- `IMAGE_DATASET_DIR`: Local folder containing ingredient images.
- `METADATA_CSV_PATH`: CSV file used for metadata persistence.

## Project structure

```text
backend/
  app/
    api/
    core/
    models/
    services/
  tests/
docs/
```

## Development notes

- On startup, the backend attempts to scan `IMAGE_DATASET_DIR` and enrich only images that are not yet present in `METADATA_CSV_PATH`.
- Startup enrichment is skipped when the dataset directory does not exist or `OPENAI_API_KEY` is not configured.
- Metadata search currently works in the service layer and is ready to be connected to API endpoints next.

## Planning

- Backend implementation plan: [docs/backend-implementation-plan.md](docs/backend-implementation-plan.md)

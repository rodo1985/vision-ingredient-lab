# vision-ingredient-lab

Vision Ingredient Lab is a toy full-stack application for exploring ingredient imagery with AI. The backend scans a local image library, generates descriptions and keywords for new files, and stores metadata in CSV. The frontend will let users search ingredients, select components, and generate a new creative image that combines them.

## What this repo is
- A Python backend for local image ingestion, metadata enrichment, and future search/generation APIs.
- A React frontend for ingredient search, selection, and generated result display.
- A lightweight playground for testing an image-to-metadata-to-generation workflow with OpenAI models.

## Key features / scope
- Scans a local ingredient image folder.
- Detects only new or unprocessed files during startup synchronization.
- Tracks processed files in a CSV metadata store.
- Enriches new files with generated descriptions and keywords.
- Searches persisted metadata by keyword or description text.
- Exposes FastAPI endpoints for metadata search and image generation.
- Builds creative prompts from selected ingredients.
- Uses OpenAI models for vision tagging and image generation.
- Keeps backend and frontend work separated by area.
- Does not yet include production deployment, authentication, or a persistent database.

## Setup
### Python backend with `uv`
1. Install `uv`: [https://docs.astral.sh/uv/](https://docs.astral.sh/uv/)
2. Create the virtual environment:
   `uv venv`
3. Sync dependencies, including dev dependencies:
   `uv sync --dev`

### Frontend
The frontend project structure exists conceptually, but the first frontend implementation task is still responsible for restoring or creating the package manifest and scripts in this worktree.

## How to run
### Backend
- Validate backend configuration:
  `uv run python -m backend.app.main`
- Run the FastAPI backend locally:
  `uv run python -m backend.app.api_main`
- Run backend tests:
  `uv run pytest`
- Run a focused backend test module:
  `uv run pytest backend/tests/test_startup_sync.py`
- Run the generation API test suite:
  `uv run pytest backend/tests/test_generation_api.py`

### Frontend
- Frontend run/build/test commands will be added as part of the frontend bootstrap task once the React manifest is present in the repo.

## Configuration
Set these environment variables before running backend commands:

- `OPENAI_API_KEY`: Required API key for OpenAI requests.
- `VISION_IMAGES_DIR`: Optional path to the local image dataset. Default: `data/images`
- `VISION_METADATA_CSV`: Optional path to the metadata CSV file. Default: `data/metadata.csv`
- `OPENAI_VISION_MODEL`: Optional vision model name. Default: `gpt-4.1-mini`
- `OPENAI_IMAGE_MODEL`: Optional image generation model name. Default: `gpt-image-1`
- `OPENAI_MAX_RETRIES`: Optional retry count for OpenAI calls. Default: `2`

## Project structure
- `backend/app`: Backend startup, config, and prompt-building modules.
- `backend/clients`: External service adapters such as the OpenAI vision client.
- `backend/ingestion`: Local dataset scanning helpers.
- `backend/metadata_repository.py`: CSV persistence logic for image metadata.
- `backend/api`: FastAPI application factory and routes.
- `backend/search`: Metadata search services.
- `backend/services`: Startup synchronization services.
- `backend/workflows`: Multi-step orchestration such as metadata enrichment.
- `backend/tests`: Backend tests.
- `docs`: Implementation plans and project notes.

## API surface
- `GET /health`: Basic health check endpoint.
- `GET /api/metadata/`: List persisted metadata rows.
- `GET /api/metadata/search?q=tomato`: Search metadata by keyword or description.
- `POST /api/generation`: Generate an image from selected ingredients.

## Contributing / Development notes
- Prefer small, well-named modules and explicit control flow.
- Keep README and docs aligned with implementation changes.
- Add or update tests for every behavior change.

# Vision Ingredient Lab

Vision Ingredient Lab is a toy full-stack application for exploring ingredient images with AI. The primary backend scans a local image folder, enriches new files with OpenAI-generated metadata, stores that metadata in CSV, and exposes search plus creative generation endpoints. The React frontend lets contributors search ingredient records, build a selection, and request a generated composition from the backend.

This review branch also preserves an older backend slice that was merged in parallel. The documented runtime below uses the newer `backend/app` stack; the legacy modules remain in the tree so their behavior can still be reviewed and tested before consolidation.

## What this repo is

- A Python backend for local image ingestion, metadata enrichment, CSV persistence, and API-driven search/generation flows.
- A React frontend for ingredient search, selection, and creative image generation.
- A contributor-friendly playground for validating backend contracts and frontend UX in the same repository.

## Key features / scope

### What it does

- Scan a local dataset of ingredient images.
- Detect newly added images without reprocessing the entire dataset.
- Generate descriptions and keywords for images with OpenAI models.
- Persist image metadata in CSV.
- Expose REST endpoints for metadata listing, search, and image generation.
- Run a React frontend against the backend API or local mock-friendly test doubles.
- Preserve both the primary backend stack and a legacy backend slice during merge review.

### What it does not do yet

- Provide production deployment or infrastructure automation.
- Include authentication or user accounts.
- Use a production database or hosted vector store.
- Consolidate the legacy backend slice into the primary `backend/app` runtime.

## Setup

### Prerequisites

- Python `3.11+`
- Node.js `20+`
- [`uv`](https://docs.astral.sh/uv/)

### Python environment with `uv`

Run these commands from the repository root:

```bash
uv venv
uv sync
```

### Frontend dependencies

```bash
cd frontend
npm install
```

### Optional local `.env`

Create a repository-root `.env` file when you want real OpenAI-backed behavior:

```env
OPENAI_API_KEY=your_api_key
OPENAI_VISION_MODEL=gpt-4.1-mini
OPENAI_IMAGE_MODEL=gpt-image-1
IMAGE_DATASET_DIR=backend/data/images
METADATA_CSV_PATH=backend/data/metadata/ingredients.csv
```

Notes:

- `OPENAI_API_KEY` is required for startup enrichment and generation requests.
- Startup enrichment is skipped when the dataset directory does not exist.
- `METADATA_CSV_PATH` defaults to `data/metadata/ingredients.csv` inside the current working directory if you do not override it.

## How to run

### Backend

Start the primary FastAPI backend from the repository root:

```bash
uv run uvicorn backend.app.main:app --reload
```

Useful backend checks:

```bash
uv run pytest
uv run ruff check .
uv run python -c "from backend.app.main import app; print(app.title)"
```

### Frontend

```bash
cd frontend
npm run dev
```

Additional frontend commands:

```bash
cd frontend
npm test
npm run build
```

## Configuration

The primary backend reads configuration from environment variables and an optional repository-root `.env` file.

- `OPENAI_API_KEY`: OpenAI API key for metadata enrichment and generation.
- `OPENAI_VISION_MODEL`: Optional override for the image understanding model.
- `OPENAI_IMAGE_MODEL`: Optional override for the image generation model.
- `IMAGE_DATASET_DIR`: Local folder containing ingredient images.
- `METADATA_CSV_PATH`: CSV file used for metadata persistence.
- `APP_ENV`: Optional environment label used in startup logging.

## Project structure

- `backend/app`: Primary backend application package, API routes, settings, models, and services.
- `backend/tests`: Backend tests for both the primary app and the preserved legacy slice.
- `frontend/src`: React components, state, and API client code.
- `docs`: Supporting implementation and API notes.
- `backend/api`, `backend/clients`, `backend/ingestion`, `backend/search`, `backend/workflows`: Legacy modules preserved during merge review so behavior remains inspectable and testable.

## API surface

Primary backend endpoints:

- `GET /health`: Basic service health check.
- `GET /api/images`: List stored metadata rows.
- `GET /api/search?query=<term>`: Search metadata by keyword and description terms.
- `POST /api/generate`: Generate an image from selected ingredients.

See [docs/backend-api-guide.md](/Users/REDONSX1/Documents/training/Codex/code/vision-ingredient-lab-merge-review-20260317-115025/docs/backend-api-guide.md) for request examples and testing notes.

## Contributing / Development notes

- The root `pyproject.toml` is the canonical `uv` manifest for this review branch.
- Keep README and docs aligned with whichever backend contract you change.
- When touching the preserved legacy modules, keep their separate tests passing until the backend stacks are intentionally consolidated.
- Add or update tests for every behavior change, including contract changes in the frontend API client.

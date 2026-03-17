# Vision Ingredient Lab

Vision Ingredient Lab is a toy full-stack application for exploring a local folder of ingredient images with AI. The backend scans local images, generates descriptions and ingredient tags with OpenAI models, stores canonical metadata in CSV, derives a local embeddings sidecar for semantic search, and generates a new creative image from selected ingredients. The frontend is a separate React app that can run in mock mode or against the backend API.

This repository is now scaffolded for parallel implementation and deployment. The frontend and backend are intentionally separated so they can evolve in different worktrees while sharing one documented HTTP contract.

## Key Features / Scope

### What it does

- Scan a local folder of ingredient images
- Detect newly added and modified images
- Generate image descriptions and normalized ingredient tags with OpenAI
- Store canonical metadata in CSV format
- Build a local embeddings sidecar for semantic search
- Search by both exact keywords and semantic similarity
- Select ingredients in a React UI
- Generate a new creative image from selected ingredients

### What it does not do in v1

- Use a production database or hosted vector store
- Support user accounts or authentication
- Implement asynchronous background job orchestration
- Provide cloud deployment infrastructure out of the box

## Setup

### Prerequisites

- Python 3.11 or newer
- Node.js 20 or newer
- `uv`

Install `uv`:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Quick Start

### Fastest path: run the frontend by itself in mock mode

If you just want to see the UI running without configuring OpenAI yet:

```bash
cd frontend
npm install
npm run dev
```

Then open the local Vite URL shown in the terminal, usually `http://localhost:5173`.

### Full local setup: backend + frontend

If you want the frontend to talk to the backend API:

1. Set up the backend environment.
2. Add your backend `.env`.
3. Start the backend.
4. Start the frontend.

### Backend setup with uv

```bash
cd backend
uv venv
source .venv/bin/activate
uv sync --group dev
```

Create a local `.env` file in `backend/` when you are ready to use real OpenAI calls.

Example: [backend/.env](/Users/REDONSX1/Documents/training/Codex/code/vision-ingredient-lab/backend/.env)

The recommended setup is to copy the template:

```bash
cd backend
cp .env.example .env
```

```env
OPENAI_API_KEY=your_key_here
VISION_MODEL=gpt-4.1-mini
EMBEDDING_MODEL=text-embedding-3-small
IMAGE_GENERATION_MODEL=gpt-image-1.5
ENABLE_STARTUP_SYNC=false
```

Notes:

- `OPENAI_API_KEY` is required for real image analysis, embeddings, and image generation.
- Omit `OPENAI_BASE_URL` unless you intentionally use a custom-compatible endpoint.
- Keep `ENABLE_STARTUP_SYNC=false` at first so sync only runs when you explicitly trigger it.
- Do not commit the real `.env` file.

### Frontend setup

```bash
cd frontend
npm install
```

No frontend environment file is required for the current scaffold.

The frontend will try the backend first at `http://localhost:8000`.
If the backend is unavailable, it will automatically fall back to mock data.

## How To Run

### Backend

Run the API locally:

```bash
cd backend
uv run uvicorn app.main:app --reload
```

The backend will start on `http://localhost:8000`.

Useful endpoints once it is running:

- `GET http://localhost:8000/health`
- `GET http://localhost:8000/api/config`
- `POST http://localhost:8000/api/startup/sync`

Run tests:

```bash
cd backend
uv run pytest
```

Run linting:

```bash
cd backend
uv run ruff check .
```

### Frontend

Run the frontend in mock mode:

```bash
cd frontend
npm run dev
```

Build the frontend:

```bash
cd frontend
npm run build
```

Run frontend tests:

```bash
cd frontend
npm test
```

## First Real Run

After both apps are configured, this is the recommended first real run flow:

### 1. Add source images

Place a few ingredient images in:

- [backend/data/images](/Users/REDONSX1/Documents/training/Codex/code/vision-ingredient-lab/backend/data/images)

Examples:

- `tomato.jpg`
- `basil.jpg`
- `mozzarella.jpg`

### 2. Start the backend

```bash
cd backend
source .venv/bin/activate
uv run uvicorn app.main:app --reload
```

### 3. Trigger a sync

In a second terminal:

```bash
curl -X POST http://localhost:8000/api/startup/sync
```

This will:

- scan `backend/data/images/`
- generate metadata for new or changed images
- write canonical CSV data
- write the local embeddings sidecar

Expected output files after a successful sync:

- [backend/data/metadata/image_metadata.csv](/Users/REDONSX1/Documents/training/Codex/code/vision-ingredient-lab/backend/data/metadata/image_metadata.csv)
- [backend/data/metadata/image_metadata.embeddings.jsonl](/Users/REDONSX1/Documents/training/Codex/code/vision-ingredient-lab/backend/data/metadata/image_metadata.embeddings.jsonl)

### 4. Start the frontend in API mode

```bash
cd frontend
npm run dev
```

If the backend is already running on `http://localhost:8000`, the frontend will use it automatically.
If the backend is not running, the frontend will use mock data automatically.

### 5. Use the app

Recommended first checks:

1. Search for `tomato`.
2. Select one or more ingredients.
3. Add optional creative direction.
4. Generate an image.

Generated outputs will be written under:

- [backend/data/generated](/Users/REDONSX1/Documents/training/Codex/code/vision-ingredient-lab/backend/data/generated)

## Frontend Runtime Behavior

### When the backend is running

- the frontend connects to `http://localhost:8000`
- real API data is used

### When the backend is not running

- the frontend falls back to built-in mock data
- no frontend env file is needed

## Configuration

### Backend environment

- `OPENAI_API_KEY`: API key for OpenAI requests
- `OPENAI_BASE_URL`: optional custom API base URL (defaults to `https://api.openai.com/v1` when unset)
- `VISION_MODEL`: model used for image analysis
- `EMBEDDING_MODEL`: model used for semantic search embeddings
- `IMAGE_GENERATION_MODEL`: model used for image generation
- `ENABLE_STARTUP_SYNC`: whether the backend runs sync on startup

### Data directories

- `backend/data/images/`: source ingredient images
- `backend/data/metadata/image_metadata.csv`: canonical metadata store
- `backend/data/metadata/image_metadata.embeddings.jsonl`: local embeddings sidecar
- `backend/data/generated/`: generated output images

## Troubleshooting

### Frontend starts but shows only mock data

Check that the backend is running on `http://localhost:8000`, then restart `npm run dev`.

### Backend starts but sync fails

Check:

- `backend/.env` exists
- `OPENAI_API_KEY` is valid
- `backend/data/images/` contains supported image files such as `.jpg`, `.jpeg`, `.png`, or `.webp`

### No metadata files appear after sync

Make sure you called:

```bash
curl -X POST http://localhost:8000/api/startup/sync
```

and that the backend terminal did not log an OpenAI or file path error.

### Tests and verification

Backend:

```bash
cd backend
uv run pytest
uv run ruff check .
```

Frontend:

```bash
cd frontend
npm test
npm run build
```

## Project Structure

```text
vision-ingredient-lab/
├── docs/
│   └── implementation/
│       ├── api-contract.md
│       ├── backend-definition.md
│       └── frontend-definition.md
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   ├── features/
│   │   ├── hooks/
│   │   ├── mocks/
│   │   ├── services/
│   │   └── types/
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── search/
│   │   └── services/
│   ├── data/
│   │   ├── generated/
│   │   ├── images/
│   │   └── metadata/
│   ├── tests/
│   └── pyproject.toml
├── AGENTS.md
└── README.md
```

## API Contract

The shared frontend/backend contract lives in:

- [docs/implementation/api-contract.md](/Users/REDONSX1/Documents/training/Codex/code/vision-ingredient-lab/docs/implementation/api-contract.md)

The implementation handoff docs live in:

- [docs/implementation/frontend-definition.md](/Users/REDONSX1/Documents/training/Codex/code/vision-ingredient-lab/docs/implementation/frontend-definition.md)
- [docs/implementation/backend-definition.md](/Users/REDONSX1/Documents/training/Codex/code/vision-ingredient-lab/docs/implementation/backend-definition.md)

## Contributing / Development Notes

- Keep the frontend and backend deployable on their own.
- Treat the API contract as the shared integration source of truth.
- Keep CSV as the canonical metadata store in v1.
- Keep embeddings as a derived local sidecar, not the source of truth.
- Add or update tests for backend behavior changes.
- Update the README and implementation docs whenever setup, behavior, or contract details change.

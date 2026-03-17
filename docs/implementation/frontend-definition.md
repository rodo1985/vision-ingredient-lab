# Frontend Implementation Definition

## Goal

Build a React + TypeScript + Vite single-page application that can run independently in mock mode or connect to the backend through the shared HTTP contract without changing component logic.

## Runtime and Tooling

- React 18
- TypeScript
- Vite
- Vitest + Testing Library for UI and service tests

## App Structure

- `src/app/`: app shell and layout
- `src/components/`: reusable presentational UI
- `src/features/search/`: search input and results grid
- `src/features/selection/`: selected ingredient list
- `src/features/generation/`: generate action and generated result view
- `src/services/`: typed API and mock service adapters
- `src/mocks/`: fixture data and mock API implementation
- `src/types/`: frontend copies of the shared API contract

## Runtime Modes

### Mock mode

Use fixture-backed services with artificial latency so the frontend team can build and test without the backend being available.

### API mode

Use HTTP calls to the backend contract from [api-contract.md](/Users/REDONSX1/Documents/training/Codex/code/vision-ingredient-lab/docs/implementation/api-contract.md).

Selection between modes should happen through a single environment variable.

## Main Screen

The v1 UI should remain a single focused workflow:

1. Sync status banner
2. Search bar
3. Search result grid
4. Selected ingredients panel
5. Generate panel
6. Generated image result panel

## Data Flow

1. On app boot, load config and initial image data.
2. Search queries debounce and call the search service.
3. Clicking a result toggles ingredient selection.
4. Generate submits selected ingredient ids plus optional creative direction.
5. The UI renders loading, success, and error states for generation.

## Frontend Boundaries

- Treat backend ranking as authoritative.
- Do not infer filesystem locations beyond the `imageUrl` field.
- Keep all request and response types aligned with the shared contract.
- Mock payloads must be shape-compatible with the real backend responses.

## Testing

Required frontend tests:

- app boots in mock mode
- search debounce triggers service queries
- selection updates correctly on toggle
- generate action blocks duplicate submits while loading
- success state renders returned generation data
- error state is recoverable

# Frontend Guide

## Purpose
The React frontend in Vision Ingredient Lab gives users a local, visual workflow for:
- searching AI-generated ingredient metadata
- selecting ingredient building blocks
- sending the selected ingredients to the backend generation endpoint
- reviewing the generated creative image and prompt metadata

## Setup
1. Install dependencies:
   `cd frontend && npm install`
2. Start the dev server:
   `cd frontend && npm run dev`

## Test and build commands
- Run the frontend test suite:
  `cd frontend && npm test`
- Build the production bundle:
  `cd frontend && npm run build`

## Configuration
- `VITE_BACKEND_BASE_URL`: Optional override for the backend base path. Defaults to `/api`.

## Component map
- `src/App.tsx`: Connects backend API calls to the shared reducer/context state.
- `src/components/IngredientSearchPanel.tsx`: Query input, search feedback, and search helper text.
- `src/components/SearchResultsGrid.tsx`: Search result cards, loading state, empty state, and add actions.
- `src/components/SelectedIngredientsPanel.tsx`: Selected ingredient review with remove and clear actions.
- `src/components/GenerateImagePanel.tsx`: Generation CTA, validation, and selected ingredient summary.
- `src/components/GeneratedResultPanel.tsx`: Idle, loading, error, and success display for generated artwork.
- `src/state/ingredientState.tsx`: Shared reducer/context state for search, selection, and generation.

## Frontend flow
1. App boot triggers a metadata fetch from the backend.
2. Typing in the search field updates shared query state.
3. Search requests are debounced before calling the metadata search endpoint.
4. Selected ingredients are stored as full result objects so the selection survives query changes.
5. Generating an image sends the selected ingredient names to the backend.
6. The UI renders loading, error, or success states based on the generation response.

## Testing notes
- `src/test/App.test.tsx` covers the top-level shell rendering.
- `src/test/App.integration.test.tsx` covers the main search -> select -> generate flow with mocked backend responses.
- Component tests cover empty, loading, error, and success states where appropriate.

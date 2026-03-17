# API Contract

This document defines the shared HTTP contract for the independently deployable frontend and backend applications.

## Base URL

- Local development: `http://localhost:8000`
- All API responses are JSON unless otherwise stated.

## Models

### ImageRecord

```json
{
  "id": "img_tomato_01",
  "filename": "tomato.jpg",
  "imageUrl": "/data/images/tomato.jpg",
  "description": "A close-up ingredient photo of a ripe red tomato.",
  "tags": ["tomato", "red", "fresh"],
  "lastModified": "2026-03-16T18:30:00Z",
  "status": "ready"
}
```

Fields:

- `id`: string
- `filename`: string
- `imageUrl`: string
- `description`: string
- `tags`: string[]
- `lastModified`: ISO 8601 string
- `status`: `"ready" | "processing" | "stale" | "error"`

### SearchResult

```json
{
  "image": {
    "id": "img_tomato_01",
    "filename": "tomato.jpg",
    "imageUrl": "/data/images/tomato.jpg",
    "description": "A close-up ingredient photo of a ripe red tomato.",
    "tags": ["tomato", "red", "fresh"],
    "lastModified": "2026-03-16T18:30:00Z",
    "status": "ready"
  },
  "score": 0.93,
  "matchReasons": ["keyword", "semantic"],
  "matchedTags": ["tomato"]
}
```

Fields:

- `image`: `ImageRecord`
- `score`: number
- `matchReasons`: string[]
- `matchedTags`: string[]

### SyncResponse

```json
{
  "scannedCount": 12,
  "newCount": 2,
  "updatedCount": 1,
  "failedCount": 0,
  "startedAt": "2026-03-16T18:30:00Z",
  "completedAt": "2026-03-16T18:30:05Z"
}
```

### GenerateRequest

```json
{
  "ingredientIds": ["img_tomato_01", "img_basil_01"],
  "creativeDirection": "Plate the ingredients like a rustic pizza concept."
}
```

Fields:

- `ingredientIds`: string[]
- `creativeDirection`: string | omitted

### GenerateResponse

```json
{
  "generationId": "gen_20260316_183005",
  "imageUrl": "/data/generated/gen_20260316_183005.png",
  "prompt": "Create a food composition combining tomato and basil in a rustic pizza-inspired plating.",
  "ingredientIds": ["img_tomato_01", "img_basil_01"],
  "createdAt": "2026-03-16T18:30:05Z"
}
```

## Endpoints

### `GET /health`

Response:

```json
{
  "status": "ok",
  "indexFresh": true
}
```

### `POST /api/startup/sync`

Runs a scan and metadata/index sync.

Response: `SyncResponse`

### `GET /api/images?limit=50&offset=0`

Response:

```json
{
  "items": ["<ImageRecord>"],
  "total": 1
}
```

### `GET /api/images/{image_id}`

Response: `ImageRecord`

### `GET /api/search?q=tomato&limit=20`

Response:

```json
{
  "query": "tomato",
  "items": ["<SearchResult>"]
}
```

### `POST /api/generate`

Request: `GenerateRequest`

Response: `GenerateResponse`

### `GET /api/config`

Response:

```json
{
  "mode": "mock",
  "enableStartupSync": true,
  "maxSearchResults": 20
}
```

## Error Shape

```json
{
  "error": {
    "code": "not_found",
    "message": "Image not found.",
    "details": {
      "imageId": "img_missing"
    }
  }
}
```

Fields:

- `error.code`: string
- `error.message`: string
- `error.details`: object | omitted

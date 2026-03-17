# Vision Ingredient Lab Backend Implementation Plan

## Document Metadata
- Project: Vision Ingredient Lab (Backend)
- Jira Epic: `AIIP-31`
- Plan version: 1.0
- Created: March 17, 2026

## Objective
Build the Python backend that scans local ingredient images, enriches new files with OpenAI-generated metadata, stores that metadata in CSV, and supports later search and generation APIs.

## Wave 1
- `AIIP-32`: Project bootstrap with `uv` + config foundation
- `AIIP-33`: Image dataset scanner service
- `AIIP-34`: CSV metadata repository
- `AIIP-36`: OpenAI vision client
- `AIIP-41`: Prompt builder for ingredient composition

## Wave 2
- `AIIP-35`: Startup sync service for detecting unprocessed images
- `AIIP-37`: Metadata enrichment workflow for newly discovered files
- `AIIP-39`: Search service over persisted metadata

## Wave 3
- `AIIP-38`: Metadata/search API endpoints
- `AIIP-40`: Image generation API endpoint

## Parallel lanes
- Core/bootstrap: `AIIP-32`, `AIIP-41`
- Ingestion: `AIIP-33`
- Storage: `AIIP-34`
- AI integration: `AIIP-36`

## Integration note
Wave 1 establishes the package structure and isolated building blocks. Wave 2 wires those pieces together into startup synchronization, metadata enrichment, and search-ready querying. Wave 3 adds the FastAPI endpoints for metadata browsing and creative generation, giving clients a clear surface for the queued workflows.

## Current API endpoints
- `GET /health`
- `GET /api/metadata/`
- `GET /api/metadata/search?q=<term>`
- `POST /api/generation`

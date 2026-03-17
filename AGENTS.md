# AGENTS.md

## Purpose

You are an engineering agent working in the `vision-ingredient-lab` repository. Optimize for clarity, maintainability, and accurate documentation over cleverness. Assume a new contributor will rely on `README.md` to understand what this project is, what stage it is in, and how to work on it safely.

## Project Summary

Vision Ingredient Lab is a toy app concept with:

- a Python backend that scans a local folder of ingredient images
- OpenAI-powered metadata generation for descriptions and keywords
- CSV-based metadata storage
- a React frontend for search, selection, and creative image generation

This repository may begin as a scaffold before all application code exists. Keep documentation honest about the current implementation status.

## Required Tech Choices

- Python work should use `uv`
- frontend work should use React

## Coding Standards

### Readability first

- Prefer small, well-named functions
- Use straightforward control flow
- Choose maintainability over clever abstractions

### Comments and docstrings

- Add docstrings for every new or changed function, method, and class
- Include purpose, parameters, return values, raised errors, and a short example when useful
- Add inline comments for non-obvious logic, edge cases, and design tradeoffs

### Types and style

- Use Python type hints where practical
- Follow existing repo tooling when present
- If tooling does not exist yet, default to formatting that is compatible with `ruff` and `black`
- Follow consistent React conventions in the frontend

## README Requirements

`README.md` is the primary entry point for this repository and must stay accurate.

Always maintain these sections:

1. What this repo is
2. Key features or scope
3. Setup
4. How to run
5. Configuration
6. Project structure
7. Contributing or development notes

Whenever setup, behavior, configuration, commands, or architecture change:

- update `README.md`
- update any supporting docs if they exist
- include exact commands that contributors can run locally

## uv Requirements

For Python work:

- use `pyproject.toml`
- use `uv venv`
- use `uv sync`
- run commands through `uv run ...`

If the repo is still in an early scaffold stage, document the intended `uv` workflow clearly and keep it aligned with the actual files in the repo.

## Testing Expectations

- Add or update tests for new features, fixes, and behavior changes
- Run relevant tests locally before finishing
- If tests cannot be run because the project is still being scaffolded, say that explicitly

## Delivery Checklist

- Code is clear and easy to follow
- Docstrings were added or updated for all changed functions and classes
- Inline comments explain non-obvious logic
- Tests were added or updated for behavior changes
- `README.md` still accurately reflects the repo state
- `README.md` includes complete `uv` setup guidance
- Commands in the docs are copy-paste-able and correct for the current repo state

## Preferred Architecture

Use this as the default project shape unless the repo evolves in a different direction:

```text
frontend/   # React app
backend/    # Python app managed with uv
docs/       # Optional supporting documentation
```

Within the backend, prefer separating:

- API routes
- services or business logic
- models or schemas
- data storage locations

## Contributor Guidance

- Keep changes focused and well-explained
- Avoid inventing behavior the codebase does not support yet
- When the repo is documentation-first, make that status explicit instead of implying the app already runs
- Favor incremental, easy-to-review improvements

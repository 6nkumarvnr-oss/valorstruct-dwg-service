# Contributing Guide

Thank you for contributing to this repository.

## Development setup
1. Create a virtual environment.
2. Install dependencies from `requirements.txt`.
3. Run the API using `uvicorn tet_engine.app.main:app --reload --port 8001`.

## Pull Request process
- Create a feature branch from `main`.
- Keep PRs focused and small.
- Update docs for behavior changes.
- Add or update tests when modifying logic.
- Ensure CI passes.

## Commit conventions
Use concise, imperative commit messages, for example:
- `Add publish report download endpoint`
- `Fix chunk retrieval ranking bug`

## Code style
- Prefer explicit typing.
- Keep API models in `models.py`.
- Keep business logic in `services.py` or dedicated modules.

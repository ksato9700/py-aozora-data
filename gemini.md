# Gemini Rules

- **Always use `uv` commands**: Use `uv sync`, `uv run`, `uv add`, etc. for all Python dependency management and execution tasks. Do not use direct `pip`, `python`, `pytest` or `ruff` commands unless necessary (e.g. inside a specific `uv run` context).
- **Always run `uv run ruff format` before committing changes.
- **Check for PII before commit**: Before committing changes, scan for and warn about any personal information (names, emails, addresses, keys, etc.) other than valid project metadata like authors in `pyproject.toml`.

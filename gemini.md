# Gemini Rules

- **Always use `uv` commands**: Use `uv sync`, `uv run`, `uv add`, etc. for all Python dependency management and execution tasks. Do not use direct `pip` or `python` commands unless necessary (e.g. inside a specific `uv run` context).

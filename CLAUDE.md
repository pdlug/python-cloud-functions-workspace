- Prefer functional, modular code over procedural or class-heavy styles.
- Enforce descriptive variable names and structure.
- Eagerly refactor to smaller functions, classes, externalized configuration to
  improve readability and reduce duplication
- Use strict typing with mypy
- Use uv as the package manager
  - Always run python with `uv run python`

This is a monorepo using uv workspaces. Libraries go in `libs` and services that
use libraries and are deployable go in `services`.

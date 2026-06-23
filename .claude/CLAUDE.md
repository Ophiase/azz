# Project Memory

## Context

Azz is a CLI tool for Azure DevOps work item management, built on top of
the Azure CLI. It is a personal tool made public — keep changes focused
and avoid scope creep.

Stack: Python 3.14, uv, just, Ruff, Ty.

## Tooling

- **uv** manages packages and the virtual environment.
  Never use `pip install` or create a venv manually.
- **just** is the task runner. Run `just -l` to discover commands.
  Key recipes:
  - `just precommit` — lint + type-check (run before every commit,
    never invoke `ruff` or `ty` directly)
  - `just install` / `just install-dev` — install the tool
  - `just run <args>` — run the CLI locally

## Code Practices

See [PYTHON.md](./PYTHON.md) for the full Python guidelines.
Quick summary:

- Type annotations everywhere.
- No abbreviations, no single-letter names.
- Short functions, short files, single concern per unit.
- `pydantic.BaseModel` for public-facing data, `dataclass` for internal.
- `StrEnum`/`IntEnum` for enums.
- Prefer immutable types: accept `Sequence`, return `tuple`.
- Comments only when the *why* is non-obvious.

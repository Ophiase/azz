# Project Memory

## LIST LABELS

When presenting a list of items the developer may want to respond to
individually (review findings, options, TODOs, checklist items), prefix each
item with a short label so it can be referenced with a single word:

- Use `[A]`, `[B]`, `[C]` … for flat lists.
- Use `[A1]`, `[A2]`, `[B1]` … for grouped lists.
- In review reports use `[B1]`, `[B2]` for blockers, `[W1]`, `[W2]` for
  warnings, `[D1]` for defers.

This lets the developer say "fix B2 and W1" without copy-pasting.

## LANGUAGE — ENGLISH ONLY

All code, comments, docstrings, names, commit messages, markdown files and
documentation must be in English. No exceptions. French anywhere is a
blocker.

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
  - `just checks` — `rumdl` + lint + type-check in one allowlisted command,
    with a real exit code. Run it before every commit and always prefer it
    over hand-piping `just precommit` through `grep`/`tail`.
  - `just precommit` — lint + type-check only
    (never invoke `ruff` or `ty` directly)
  - `just install` / `just install-dev` — install the tool
  - `just run <args>` — run the CLI locally

### Agent justfile

Recipes meant for agent use live in [agent.just](../agent.just), available
from the project root as `just agent::<command>`.

- List everything including the module: `just --list --list-submodules`
- `just agent::checks` — the underlying recipe behind `just checks`
- When you find yourself repeating the same Bash invocation across sessions,
  add it to `agent.just` and document it here. No `settings.json` entry is
  needed — `just *` is already allowed.
- Always tell the developer which command you are about to run before
  running it.

## Bash commands

- **Never chain with `;`.** This is the number one cause of permission
  prompts. Claude Code splits a command on `|` and `&&` and matches each
  part against the allowlist, but a `;` list is matched as one opaque
  string that no rule can ever allow — so even an all-read-only chain like
  `head -5 CHANGELOG.md; echo "==="; git log -3` interrupts the developer.
  - One command per Bash call, or `&&` when a step must gate the next.
  - Pipes and `2>&1` are fine and never prompt on their own:
    `just precommit 2>&1 | tail -20` is allowed.
  - `echo "=== label ==="; cmd` is the most frequent offender — put the
    label in the tool call description, not in the command.
  - `cmd | tail -5; echo "exit=$?"` also reports the **wrong** exit code
    (that is `tail`'s status, not `cmd`'s). Use `just checks` for a
    markdown + precommit summary with a real exit code.
- **No `$(...)` or backticks** in a command meant to run unattended: a
  substitution can expand to anything, so the whole command falls back to
  asking. Use the tool's own filters instead of interpolating a file list —
  `rg -n 'name = "pydantic"' -g uv.lock .`, not
  `rg -n 'name = "pydantic"' $(find . -name uv.lock)`.
- Read third-party library sources through the in-repo venv
  (`.venv/lib/python3.14/site-packages/...`), never through
  `~/.cache/uv/...`. Both are the same file, but paths outside the
  workspace require approval whatever command reads them.
- Each Bash call starts at the project root — `cd` never persists across
  calls.
- For **search commands**, prefer path arguments over `cd dir && command`
  chains. A `cd`-prefixed command won't match `grep *`, `rg *` or `find *`
  allow rules, causing unnecessary permission prompts.
  - `rg pattern src/azz/plan/` not `cd src/azz/plan && rg pattern .`
  - `find src/azz -name 'plan*'` not `cd src/azz && find . -name 'plan*'`
- Always use relative paths from the project root for search commands.
- Prefer purpose-built read-only tools over generic interpreters
  (`python3 -c`, `node -e`, …) for one-off inspection or validation.
  Interpreters grant arbitrary code execution, so they always prompt for
  approval — correctly so, never ask to blanket-allow them. The
  alternatives below are read-only and mostly already allowed:
  - JSON: `jq` — `jq . file.json` to pretty-print, `jq empty file.json` to
    validate, `jq '.some.key' file.json` to query
  - Hex/binary inspection: `xxd`, `hexdump`, `od`, `file`
  - Checksums: `sha256sum`, `md5sum`
  - Text search: `rg`/`grep`, never a `python3 -c` regex loop
  - Diffing: `diff`, `git diff`

## Code Practices

See [PYTHON.md](./PYTHON.md) for the full Python guidelines.
Quick summary:

- Type annotations everywhere.
- No abbreviations, no single-letter names.
- Short functions, short files, single concern per unit.
- `pydantic.BaseModel` for public-facing data, `dataclass` for internal.
- `StrEnum`/`IntEnum` for enums.
- Prefer immutable types: accept `Sequence`, return `tuple`.
- `Protocol` over `Callable`.
- Comments only when the *why* is non-obvious — but a docstring is required
  when the signature alone cannot convey the purpose.

Read [PLAN.md](./PLAN.md) **before** touching the plan engine
(`src/azz/plan/`, `src/azz/cache/`, `azz plan *`) — and keep it updated in
the same change when you alter the model.

## Changelog and VERSION

[CHANGELOG.md](../CHANGELOG.md) is read at sight, not archaeologically.
Be **extremely** careful not to bloat it: only significant, user-visible
changes, and be very brief.

Version numbers are `vMAJOR.MINOR.PATCH` (e.g. `v0.2.1`).

- **MINOR** (`v0.1` → `v0.2`): opened by the **developer only**, never by
  Claude. Each minor version has its own `## v0.1` section.
- **PATCH** (`v0.1.0` → `v0.1.1`): Claude can and should open a new patch
  entry when the change is a distinct concern from the current latest one.
  Add it as a bullet in the existing `## vMAJOR.MINOR` section, with a date:
  `- **v0.1.1 — 2026-07-31**`
- Never bump twice ahead of the remote head.

The root [VERSION](../VERSION) file is the source of truth for the git tag
and must stay in sync with `pyproject.toml` and the latest CHANGELOG entry.
`just version` shows all three — use it to check they agree.

## Git

- You are **not** supposed to commit by yourself. There is a `/commit`
  command for that. Ask, or wait to be asked.
- Never rewrite history: no `--amend`, no rebase, no force-push.

## Remarks

- Markdown: linted with `rumdl`
  - always specify the language on fenced code blocks (e.g. ` ```python `,
    ` ```bash `)
  - be careful about line length (break them)
  - after editing any `.md` file, run `just checks` (or `just rumdl` alone)
    and `just rumdl-fmt` to auto-fix formatting

# AGENTS.md

Instructions for any coding agent working in this repository. Claude Code
reads this file through `.claude/CLAUDE.md`; other agents (Codex, Cursor,
Copilot, Gemini CLI) read it directly.

## Language — English only

All code, comments, docstrings, identifiers, commit messages, markdown files
and documentation **must be in English**. No exceptions. French anywhere is
an automatic blocker.

## List labels

When presenting a list of items the developer may want to answer individually
(review findings, options, TODOs, checklist items), prefix each item with a
short label so it can be referenced with a single word:

- `[A]`, `[B]`, `[C]` ... for flat lists
- `[A1]`, `[A2]`, `[B1]` ... for grouped lists
- In review reports: `[B1]`, `[B2]` for blockers, `[W1]`, `[W2]` for warnings,
  `[D1]` for defers

This lets the developer say "fix B2 and W1" without copy-pasting.

## What this project is

Azz is a CLI tool for Azure DevOps work item management, built on top of the
Azure CLI. It is a personal tool made public — keep changes focused and avoid
scope creep.

Stack: Python 3.14, uv, just, Ruff, Ty.

- [README.md](README.md) — commands and project structure
- [docs/](docs/) — user-facing documentation
- [docs/decisions/](docs/decisions/) — accepted architecture decisions

## Reference material

Topic guides live in `.claude/rules/`. Claude Code loads them automatically
(`python.md` every session, the others when you touch a matching file); every
other agent must open them by path. Read the relevant one **before** you
start:

- `.claude/rules/python.md` — how Python code here is expected to look
- `.claude/rules/plan.md` — **before** touching the plan engine
  (`src/azz/plan/`, `src/azz/cache/`, `azz plan *`)

Keep the matching guide updated in the same change as the code it describes.

## Toolchain

- **just** — task runner. Run `just -l` to discover commands; check the
  `justfile` before inventing an invocation.
  - `just checks` — `rumdl` + lint + type-check + tests in one allowlisted
    command, with a real exit code. Run it before every commit and always
    prefer it over hand-piping `just precommit` through `grep`/`tail`.
  - `just precommit` — lint + type-check only (never invoke `ruff` or `ty`
    directly)
  - `just install` / `just install-dev` — install the tool
  - `just run <args>` — run the CLI locally
- **uv** — packages and virtualenv. Never `pip install`, never create a venv
  by hand; `uv run` is how Python runs locally.
- **Markdown** — linted with `rumdl`. Always set a language on fenced code
  blocks, keep lines short, and after editing any `.md` run `just rumdl` to
  check and `just rumdl-fmt` to fix. In Claude Code a hook enforces this on
  every markdown file you touch (see [.claude/CLAUDE.md](.claude/CLAUDE.md));
  other agents must run it themselves.

Read third-party library sources through the in-repo venv
(`.venv/lib/python3.14/site-packages/...`), never through a global cache such
as `~/.cache/uv/`.

## Shell discipline

- One command per call, or `&&` when a step must gate the next. **Never chain
  with `;`** — see [.claude/CLAUDE.md](.claude/CLAUDE.md) for why this
  matters to Claude Code specifically.
- Put labels in the tool-call description, not in an `echo` before the
  command.
- `cmd | tail -5` reports `tail`'s exit code, not `cmd`'s. For a markdown +
  precommit summary with a real exit code, run `just checks`.
- Avoid `$(...)` and backticks in unattended commands; use the search tool's
  own filters instead of interpolating a file list.
- Prefer purpose-built read-only tools over generic interpreters (`python3 -c`,
  `node -e`, ...) for inspection: `jq` for JSON, `rg`/`grep` for text, `xxd`
  or `file` for binaries, `sha256sum` for checksums, `diff`/`git diff` for
  comparisons.
- Every call starts at the project root; a `cd` does not persist across calls.
  Use relative paths from the root, and pass paths as arguments rather than
  `cd dir && command`.

## Agent utilities

Read-only helpers built for agents live in [agent.just](agent.just) and are
available from the project root as `just agent::<command>`:

- `just --list --list-submodules` — full recipe tree, agent module included
- `just agent::checks` — the recipe behind `just checks`
- `just agent::version` — VERSION, `pyproject.toml` and the latest CHANGELOG
  entry side by side

Tell the developer which command you are about to run before running it. When
you find yourself repeating a Bash invocation across sessions, add it to
`agent.just` and document it there.

## Changelog and version

[CHANGELOG.md](CHANGELOG.md) is read at a glance, not archaeologically. Be
**extremely** careful not to bloat it: only significant, user-visible
changes, and be very brief.

Versions are `vMAJOR.MINOR.PATCH` (e.g. `v0.2.1`). An agent may open a
**patch** entry, never a **minor** section, and never two patch bumps ahead of
the remote head. The root [VERSION](VERSION) file is the source of truth for
the git tag and must stay in sync with `pyproject.toml` and the newest
CHANGELOG entry — `just version` shows all three.

Never touch `CHANGELOG.md` or `VERSION` outside the procedure in
`.claude/skills/log-changes/SKILL.md` (in Claude Code: `/log-changes`) — it
owns the numbering, the dated-bullet format and the VERSION sync.

## Committing

Agents do not commit, amend, rewrite or push on their own. The developer asks
for a commit explicitly (in Claude Code, `/commit`). Never rewrite history:
no `--amend`, no rebase, no force-push.

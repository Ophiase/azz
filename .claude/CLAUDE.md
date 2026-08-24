# Claude Code — project instructions

@../AGENTS.md

The shared, tool-neutral rules are in the imported `AGENTS.md` above. This
file adds what only applies to Claude Code.

## How the rules load

The map of `.claude/rules/` is in `AGENTS.md` above. What is Claude-specific:
`rules/python.md` has no `paths:` frontmatter, so it loads every session;
`rules/plan.md` is path-scoped and arrives when you read a file under
`src/azz/plan/` or `src/azz/cache/`. That trigger is a file *read* — if you
are about to add a `azz plan` subcommand or a new cache backend from scratch,
open the rule yourself instead of assuming it fired.

## Why shell discipline matters here

Claude Code splits a command on `|` and `&&` and matches each part against the
permission allowlist, but a `;` list is matched as one opaque string that no
rule can ever allow. So a chain like
`head -5 CHANGELOG.md; echo "==="; git log -3` interrupts the developer even
though every part is read-only. Pipes and `2>&1` never prompt on their own:
`just precommit 2>&1 | tail -20` is fine.

A `$(...)` substitution can expand to anything, so the whole command falls
back to asking — use the tool's own filters instead of interpolating a file
list (`rg -n 'name = "pydantic"' -g uv.lock .`, not `rg ... $(find ...)`).
Paths outside the workspace prompt whatever command reads them, which is why
third-party sources are read through the in-repo venv.

For search commands prefer path arguments over `cd dir && command`: a
`cd`-prefixed command does not match the `grep *`, `rg *` or `find *` allow
rules. Generic interpreters (`python3 -c`, `node -e`) always prompt, correctly
so — never ask to blanket-allow them.

The permission model in `.claude/settings.json` is a broad `allow` list with a
short `deny` list (history rewrites, `azz delete`, `.env`) and an `ask` list
(commit, push, `gh`, `az`, `azz plan push`, `azz edit`) as the boundary.
`just *` already covers every recipe, so a new `agent.just` recipe needs no
settings entry.

## Skills

Project workflows live in `.claude/skills/<name>/SKILL.md` and are invoked as
`/<name>`; the `/` menu lists them with their descriptions.

- `/claude` — re-read the instruction files and report what is stale
- `/commands` — list what this project offers
- `/commit` — commit the current work (never pushes)
- `/log-changes` — CHANGELOG entry plus the VERSION sync

Skills with side effects (`/commit`, `/log-changes`) set
`disable-model-invocation: true`, so they run only when the developer types
them.

Instruction files are read at session start: a mid-session edit to
`AGENTS.md`, `.claude/CLAUDE.md` or a rule is not picked up on its own.
`/claude` re-reads them and reports what is stale; changes to
`settings.json` or to a skill's frontmatter need a restart.

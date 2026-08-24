---
name: commands
description: "List what this project offers an agent: the skills, the just recipes and the guideline documents, one screen, labelled."
allowed-tools: Bash(just --list*) Read Glob
---

# List the project commands

Report what is available in this project, grouped, with one line each.

1. `ls .claude/skills/` — read each `SKILL.md` frontmatter `description` for
   its purpose. These are the slash commands.
2. `just --list --list-submodules` — the task runner, including the
   `agent::` module.
3. Point at the guideline documents: [AGENTS.md](../../../AGENTS.md),
   [CLAUDE.md](../../CLAUDE.md), [rules/](../../rules/), and
   [docs/decisions/](../../../docs/decisions/).

Keep the answer to a screen. Label the entries per the list-labels rule so
the developer can pick one by letter.

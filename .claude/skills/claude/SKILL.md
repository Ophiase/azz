---
name: claude
description: "Force a re-read of the project instructions after editing .claude/ — reads AGENTS.md, CLAUDE.md and the active rules, then reports what is loaded."
disable-model-invocation: true
allowed-tools: Read Glob
---

# Reload the project instructions

Use this after editing anything under `.claude/` (or `AGENTS.md`) to confirm
what this session is actually working from. Instruction files are read at
session start, so a mid-session edit is **not** picked up on its own.

## Step 1 — Read, in full, in this order

- `AGENTS.md` — the shared, tool-neutral core
- `.claude/CLAUDE.md` — the Claude Code layer (it imports the file above)
- `.claude/rules/python.md` — always loaded, this is a Python project
- `README.md` — skim for the project structure

Then read `.claude/rules/plan.md` if the task touches the plan engine.

## Step 2 — Report

Print, in this order:

1. Which of the files above you had **already** loaded before this command,
   and which ones you had not. If an edit is not reflected in what you just
   read, say so — the developer needs to know the session is stale.
2. The rules you are most likely to violate on the current task, in one
   sentence each, so the developer can see the instructions were processed.

## Step 3 — When a restart is required

Some things cannot be reloaded by reading files. Tell the developer to restart
the session (or run `/context` to check what is loaded) when the edit touched:

- `.claude/settings.json` — permissions
- the frontmatter of a skill, or the `paths:` of a rule

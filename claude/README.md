# azz — Claude integration

Two files to add to your project to give Claude access to `azz` commands:

1. **A docs file** — tells Claude what commands exist and how to use them
2. **A settings file** — controls what Claude can run silently vs. what
   requires your approval

## Profiles

| Profile | Commands | Use case |
|---|---|---|
| `read-only` | list, show, timebox, list_timebox, branch, plan status | Claude can look things up, you stay in control of all writes |
| `standard` | + create, state, close, resolve, attach, set_timebox | Claude can manage tasks; destructive ops (delete, edit) still blocked |

Both profiles let Claude run `azz plan status` and write intent files in
`.azz/tasks/` — planning is local and risk-free. `azz plan resolve` is the
only plan command that touches the remote and is never allow-listed.

## Setup

```bash
# Choose one profile — read-only example:
cat path/to/azz/claude/docs-read-only.md >> CLAUDE.md
cp path/to/azz/claude/settings-read-only.json .claude/settings.json

# Or standard:
cat path/to/azz/claude/docs-standard.md >> CLAUDE.md
cp path/to/azz/claude/settings-standard.json .claude/settings.json
```

If you already have a `.claude/settings.json`, merge the `permissions`
block manually instead of overwriting.

## What the settings file controls

- Commands listed under `allow` run silently without a confirmation prompt.
- Commands **not** listed require your approval each time — Claude will show
  you what it wants to run.
- `delete`, `edit`, and `plan resolve` are never in the allow list by design;
  they will always require explicit approval.

## Prerequisites

- `azz` installed and on PATH
- Environment variables configured (see `.env.example` in the azz repo)

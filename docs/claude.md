# azz — Claude integration

Give Claude access to `azz` in one command, from inside the project you
want it to work on:

```bash
azz claude install            # planning profile (default)
azz claude install standard
azz claude list               # show what each profile grants
```

This writes two things:

1. **Docs** appended to `CLAUDE.md` — tells Claude what commands exist and
   how to use them
2. **Permissions** merged into `.claude/settings.json` — controls what Claude
   can run silently, what prompts you, and what is refused outright

Use `--target <dir>` to install somewhere other than the current directory.

## Profiles

| Profile | Claude can | Claude cannot |
|---|---|---|
| `planning` | read the remote, author intent files in `.azz/tasks/` | change Azure DevOps at all — every write command is denied |
| `standard` | the above, plus `create`, `state`, `close`, `attach`, `set_timebox` behind a prompt | `edit`, `delete`, `plan push` |

`planning` is the default, and it is not as restrictive as it sounds. Claude
can plan a whole batch of work as local Markdown files; you review them like
a git diff and apply them yourself with `azz plan push`. The agent gets full
planning autonomy, and no path to your board.

`plan push` is never allow-listed in either profile. It confirms each change
on a TTY, so an agent cannot usefully run it anyway — and the only way to
make it agent-runnable would be `--yes`, which removes exactly the review
step the plan engine exists to provide.

## Re-running it

The command is idempotent and safe to re-run:

- The docs go between `<!-- azz:begin -->` and `<!-- azz:end -->` markers.
  Re-installing replaces that block and leaves the rest of your `CLAUDE.md`
  untouched.
- In `settings.json`, only rules starting with `Bash(azz` are replaced.
  Your other permissions, `env`, hooks and everything else are preserved.

Because old `azz` rules are dropped before the new ones are written,
switching profiles never leaves stale entries behind.

## Prerequisites

- `azz` installed and on PATH
- Environment variables configured (see `.env.example` in the azz repo)

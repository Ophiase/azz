# azz — Claude integration

Give Claude access to `azz` in one command, from inside the project you
want it to work on:

```bash
azz claude install            # planning profile (default)
azz claude install standard
azz claude list               # show what each profile grants
```

This writes three things:

1. **A skill** at `.claude/skills/azz/SKILL.md` — what the commands are, the
   intent-file format, and the hand-off ritual. Claude Code lists skills with
   their descriptions, so it is reached for when you say "plan a task" and
   costs nothing the rest of the time.
2. **A note in `AGENTS.md`**, between `<!-- azz:begin -->` markers — the
   tool-neutral convention, for Codex, Cursor, Gemini and anything else that
   does not read skills.
3. **Permissions** merged into `.claude/settings.json` — what the agent may
   run silently, what prompts you, and what is refused outright.

Use `--target <dir>` to install somewhere other than the current directory.

## Shared, or personal

The default installs into the repository, which is right when the whole team
uses azz. It is wrong on a repository that merely happens to be where you
work: your colleagues get an `AGENTS.md` note and a `settings.json` entry for
a tool they do not use.

```bash
azz claude install --scope user
```

| | `--scope project` (default) | `--scope user` |
|---|---|---|
| skill | `.claude/skills/azz/SKILL.md` | same path |
| permissions | `.claude/settings.json` | `.claude/settings.local.json` |
| `AGENTS.md` note | yes | no |
| hidden with `.git/info/exclude` | no | yes |
| goes in the repo | yes, commit it | no |

The skill stays inside the project in both cases: it is only useful where
`.azz/` is, and a skill in your home directory would follow you into personal
projects that have nothing to do with Azure DevOps.

What changes is whether the files are committed. A personal install adds them
to `.git/info/exclude`, which is per-clone and never committed — so
`git status` stays clean for your colleagues without touching the shared
`.gitignore`.

If a path is already tracked by git, no ignore rule can hide it. `azz` says so
rather than pretending the install was private.

## Why a skill rather than CLAUDE.md

Earlier versions appended about a hundred lines to `CLAUDE.md`. That content
is then loaded into *every* conversation in the repository, including the ones
that never mention a work item. A skill is loaded on demand. Re-installing
removes the old `CLAUDE.md` block, so you never carry both.

## The hand-off

The skill requires the agent to end any reply that touched `.azz/tasks/` with
the list of files it changed and the two commands to run:

```text
Plan changed — 2 files in .azz/tasks:
  ~ 7651-langfuse-trace.md     title, description
  + buffer-late-events.md      new task, will be created

Review:  azz plan status
Apply:   azz plan push
```

It is also told never to claim it created or pushed a work item — nothing
reaches Azure DevOps until you run `azz plan push`.

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

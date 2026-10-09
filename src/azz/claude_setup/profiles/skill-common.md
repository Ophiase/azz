## Start here

```text
azz plan status     # what is tracked locally, and what diverges
```

If azz fails with `Environment variable cannot be empty`, its settings
(`AZURE_DEVOPS_ORG`, `AZURE_DEVOPS_PROJECT`, `AZURE_DEVOPS_MANAGEMENT_PROJECT`,
`AZURE_DEVOPS_REPO`) most likely live in a direnv `.envrc` at the project root,
which a non-interactive agent shell does not load. Run every command through
it from that root — `direnv exec . azz plan status` — and never copy the
values into another file or ask the developer to change their shell setup.

If it says there is no `.azz` directory, ask the developer to run
`azz plan init`. To bring in work items that already exist on the board:

```text
azz plan fetch      # record the remote in .azz/cache (needs the network)
azz plan pull       # write that into .azz/tasks (offline, fast-forward only)
```

`fetch` never touches `.azz/tasks`; `pull` does. `status` and `pull` are
offline. Use `azz plan fetch <ID>` to pull one specific item the developer
names.

## Intent files

One Markdown file per work item in `.azz/tasks/`. Writing them is local and
risk-free — do it freely.

```markdown
---
item_id: 1234
title: Implement login page
state: Active
type: Task
parent: 100
iteration: Sprint 42
---

The body is the work item description. Write the plan here.
```

- **No `item_id` means "create this on the next push."** Omit it for a new
  task; azz writes the real id back into the file after it is created.
- A field absent from the frontmatter is never compared and never written. A
  file with only `title` will only ever change the title.
- `state`: New, Active, Resolved, Closed. `type`: Task, Bug, User Story,
  Feature, Epic.
- Deleting a file never deletes the work item.
- Edit an existing item only through a file `azz plan pull` wrote. A file
  `status` reports as `NO BASE` has no merge base and is never pushed; taking
  the remote with `azz plan pull --force` is the developer's call, not yours.
- `push` sends only the fields the file changed since it was pulled. A field
  that moved on the remote alone is left alone — `azz plan pull` brings it in.
- A new work item cannot yet name a *new* parent — `parent` only accepts a
  real remote id. Say so rather than inventing a placeholder.

## Writing a good task

- Title: imperative, no ticket prefix, no trailing period.
- Body: what and why, and the shape of the work. A few lines, not an essay —
  it is read at a glance in a board UI.
- Prefer several small tasks over one vague one, but do not invent scope the
  developer did not ask for.

## Always finish with the hand-off

The developer cannot see your file edits scroll by. Whenever you create or
edit anything in `.azz/tasks/`, **end your reply with this block**:

```text
Plan changed — 2 files in .azz/tasks:
  ~ 4103-buffer-late-events.md title, description
  + buffer-late-events.md      new task, will be created

Review:  azz plan status
Apply:   azz plan push
```

Rules for that block:

- List every file you touched, `~` for edited and `+` for new.
- Give the two commands verbatim, so they can be copied.
- **Never claim you created, updated or pushed a work item.** Nothing reaches
  Azure DevOps until the developer runs `azz plan push` themselves.

## Starting work on a task

The branch for a work item is named by azz, never invented:

```bash
azz branch 4103                     # first line: dev/tb-12-4103-buffer-late-events-in-the
git switch -c dev/tb-12-4103-buffer-late-events-in-the
```

Keep that name: `azz pr create` reads the work item id from it and links the
pull request to the item. A task that exists only in `.azz/tasks` has no id
yet — the developer pushes it first.

## Opening a pull request — `/azz pr`

When the developer asks for a pull request (or types `/azz pr`), run every
step from the directory of the branch — a worktree included:

1. `azz pr create --dry-run` shows the repository, the target branch, the
   linked work item and the reviewer that azz inferred.
2. Read what the branch adds: `git log <remote>/<target>..HEAD` and
   `git diff <remote>/<target>...HEAD`.
3. Write a title (imperative, at most 72 characters, no period) and a
   Markdown description: `## What` (the problem, then 2–4 bullets) and
   `## How` (the choices a reviewer needs). If the project has its own PR
   description guide, follow it instead. Never sign it as an agent.
4. Open it — this pushes the branch and prompts the developer:

```bash
azz pr create --title "Buffer late events in the window operator" --description-file - <<'MARKDOWN'
## What
...
MARKDOWN
```

Running it again updates the open pull request instead of opening another.
In a worktree whose `.envrc` direnv has not approved, run azz from the
worktree with the main checkout's settings:
`direnv exec <main checkout> azz pr create ...`.

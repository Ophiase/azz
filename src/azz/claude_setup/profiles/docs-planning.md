# azz — Azure DevOps task CLI (planning)

`azz` is a CLI for Azure DevOps work items and timeboxes.

In this profile you can read the remote and plan work locally, but you cannot
change Azure DevOps. Every write command is denied at the harness level.

That is not a limitation on what you can accomplish — it is the workflow. To
propose changes, write intent files in `.azz/tasks/` and show the user
`azz plan status`. They review the files like a git diff and run
`azz plan push` themselves. You plan; they apply.

Use the read commands freely to look up context before writing code.

## List work items

```text
azz list [OPTIONS]
azz l    [OPTIONS]   # alias
```

Options:

- `-a` / `--all` — include Closed items (default: open only)
- `-A` / `--others` — show other people's tasks instead of mine
- `-r` / `--resolved` — show only Resolved items
- `-c` / `--current-timebox` — restrict to the current sprint/timebox
- `-s` / `--sorted-by-update` — sort by most recently changed
  (ascending; last = most recent)
- `-l N` / `--limit N` — keep only the last N items after sorting
- `-d` / `--date` — show the last-changed date in the list

Output: one line per item — ID, state (color-coded), title, project.

## Show a work item

```text
azz show <ID>
```

Output: full details in markdown — title, state, description, parent,
iteration path.

## Timebox (current sprint)

```text
azz timebox
```

Output: name, start date, end date, and path of the current timebox (sprint).

## List all timeboxes

```text
azz list_timebox
```

Output: all available timeboxes (past and future).

## Branch name

```text
azz branch <ID>
```

Output: a normalized git branch name derived from the work item title, also
copied to clipboard. Read-only — does not create a branch.

## Plan engine (local files only — never writes to the remote)

```text
azz plan init                    # create the gitignored .azz/ directory
azz plan fetch [<ID> ...]        # mirror remote items into .azz/tasks/*.md
azz plan status                  # drift between .azz/tasks and the remote
azz plan prune --dry-run         # list the local files safe to delete
```

`fetch` options: `-l N` / `--limit N` (default 20, most recently changed;
`-l 0` means no limit), `-a` / `--all` to include Closed items,
`-c` / `--current-timebox`. `-f` / `--force` overwrites locally edited
files — ask the user first.

`azz plan fetch -a -l 0` archives every work item `azz list -a` reports,
Closed ones included. That is the backup command; it can write a lot of
files, so only run it when the user asks for a full archive.

`status` prints one line per file — `[NEW]`, `[DRIFT]`, `[NOOP]`, or
`[GONE]`. A `⚠ remote changed since the last fetch` line means someone edited
the item on Azure DevOps since it was fetched; suggest `azz plan fetch` to
take the remote version.

All of these are read-only with respect to Azure DevOps.

### Prune closed, in-sync files

```text
azz plan prune --dry-run   # pre-approved: lists candidates, deletes nothing
azz plan prune             # deletes — needs the user's approval every time
azz plan prune --yes       # same, without the per-run confirmation
```

Deletes local files only, and only when the item is Closed on the remote
*and* the file has no drift (`[NOOP]`). Files with drift, files without an
`item_id`, and `[GONE]` files are always kept. Deleting a file never deletes
the work item — re-fetch to get it back.

Only `--dry-run` is pre-approved. Run it, show the user the list, and let
them decide.

### Intent files

One Markdown file per work item in `.azz/tasks/`. Writing them is a local,
zero-risk operation — do it freely.

```markdown
---
item_id: 1234
title: Implement login page
state: Active
type: Task
parent: 100
iteration: Sprint 42
remote_changed_date: "2026-07-29T10:12:33+00:00"
---

Free-form description. The body is the work item description.
```

Rules:

- Every field is optional except `title` (required to create).
- **No `item_id` means "create this on the next push."** Omit it for new
  tasks; it is written back into the file after creation.
- A field absent from the frontmatter is never compared and never written.
  A file containing only `title` will only ever touch the title.
- `remote_changed_date` is managed by `azz`. Never write or edit it by hand.
- Only keep locally the items being worked on. Deleting a file never deletes
  the work item — `azz plan prune` does exactly that, in bulk and safely.

### Workflow

1. Write or edit files in `.azz/tasks/`.
2. Run `azz plan status` and show the user the drift.
3. Ask them to review the files.
4. They run `azz plan push`. You never do.

---

`azz create`, `azz edit`, `azz delete`, `azz state`, `azz close`,
`azz resolve`, `azz attach`, `azz set_timebox`, and `azz plan push` are
denied in this profile. Do not attempt them — propose an intent file
instead.

# azz — Azure DevOps task CLI (read-only)

`azz` is a CLI for querying Azure DevOps work items and timeboxes. The commands
below are read-only — they produce output but change nothing in Azure DevOps.

Use them freely to look up context before suggesting changes or writing code.

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
```

`fetch` options: `-l N` / `--limit N` (default 20, most recently changed),
`-a` / `--all` to include Closed items, `-c` / `--current-timebox`.
`-f` / `--force` overwrites locally edited files — ask the user first.

`status` prints one line per file — `[NEW]`, `[DRIFT]`, `[NOOP]`, or
`[GONE]`. All three commands are read-only with respect to Azure DevOps;
writing the `.azz/tasks/*.md` files themselves is safe and purely local.

---

Do not use `azz create`, `azz edit`, `azz delete`, `azz state`, `azz close`,
`azz resolve`, `azz attach`, `azz set_timebox`, or `azz plan resolve`
without explicit user instruction.

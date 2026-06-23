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

---

Do not use `azz create`, `azz edit`, `azz delete`, `azz state`, `azz close`,
`azz resolve`, `azz attach`, or `azz set_timebox` without explicit user instruction.

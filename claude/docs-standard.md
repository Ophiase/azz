# azz — Azure DevOps task CLI (standard)

`azz` is a CLI for managing Azure DevOps work items and timeboxes.

Always confirm with the user before running any write command. State the
exact command you intend to run and wait for approval before executing it.
Never chain multiple write commands without re-confirming after each one.

## Read-only commands

### List work items

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

### Show a work item

```text
azz show <ID>
```

Full details: title, state, description, parent, iteration path.

### Timebox (current sprint)

```text
azz timebox
```

### List all timeboxes

```text
azz list_timebox
```

### Branch name

```text
azz branch <ID>
```

Normalized git branch name from the work item title, copied to clipboard.

---

## Write commands — confirm before running

### Create a work item

```text
azz create "<title>" [OPTIONS]
azz c      "<title>" [OPTIONS]   # alias
```

Options:

- `-s` / `--state <state>` — initial state (Active, New, Resolved, Closed)
- `-p` / `--parent <ID>` — parent work item ID
- `-t` / `--type <type>` — work item type
  (Task, Bug, User Story, Feature, Epic; default: Task)
- `-P` / `--project <name>` — target project (defaults to the configured project)
- `-d` / `--description "<text>"` — description as a string

Do not use `--editor` / `-e` (opens an interactive editor, not suited
for agent use).

### Update state

```text
azz state "<state>" <ID> [<ID> ...]
```

Valid states: `Active`, `New`, `Resolved`, `Closed`.

### Close a work item

```text
azz close <ID> [<ID> ...]
```

Sets state to Closed. Equivalent to `azz state Closed <ID>`.

### Resolve a work item

```text
azz resolve <ID> [<ID> ...]
```

Sets state to Resolved. Equivalent to `azz state Resolved <ID>`.

### Attach a child to a parent

```text
azz attach <parent-ID> <child-ID> [<child-ID> ...]
```

Links one or more work items as children of the parent.

### Assign to current timebox

```text
azz set_timebox <ID> [<ID> ...]
```

Moves the work item(s) into the current sprint. There is no option to target a
specific timebox — it always uses the current one.

---

## Commands that require explicit user permission (not in allow list)

- `azz edit` — opens an editor to modify title/description; too interactive
- `azz delete` — permanent, irreversible

Never run these without a direct, explicit instruction from the user.

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

## Plan engine — batch planning with review

Prefer this over one-off `azz create` calls when planning more than one
task. You write local files, the user reviews them like a git diff, and a
single command pushes them to the remote.

### Set up and pull existing items

```text
azz plan init                    # create the gitignored .azz/ directory
azz plan fetch [OPTIONS]         # mirror remote items into .azz/tasks/*.md
azz plan fetch <ID> [<ID> ...]   # only these items
```

Fetch options: `-l N` / `--limit N` (default 20, most recently changed),
`-a` / `--all` to include Closed items, `-c` / `--current-timebox`,
`-f` / `--force`.

Re-running `fetch` refreshes files whose remote moved since the last fetch
and keeps files that were edited locally. `--force` overwrites local edits —
ask the user before using it.

Only keep locally the items being worked on. Deleting a file never deletes
the work item.

### Intent files

One Markdown file per work item in `.azz/tasks/`:

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
- **No `item_id` means "create this on the next resolve."** Omit it for new
  tasks; it is written back into the file after creation.
- A field absent from the frontmatter is never compared and never written.
  A file containing only `title` will only ever touch the title.
- `remote_changed_date` is managed by `azz`. Never write or edit it by hand.
- Writing these files is a local, zero-risk operation — do it freely.

### Check drift (read-only, safe to run anytime)

```text
azz plan status
```

Reports one line per file:

- `[NEW]` — no `item_id`, will be created
- `[DRIFT]` — differs from the remote, with a per-field breakdown
- `[NOOP]` — in sync
- `[GONE]` — the `item_id` does not exist on the remote; resolve skips it

A `⚠ remote changed since the last fetch` line means someone edited the item
on Azure DevOps after it was fetched. Tell the user, and suggest
`azz plan fetch` to take the remote version before pushing local edits over it.

### Apply to the remote — confirm before running

```text
azz plan resolve [OPTIONS]
```

Options:

- `--dry-run` — same output as `status`, changes nothing
- `-y` / `--yes` — skip the per-change confirmation

Creations run before updates. Each change is confirmed individually. On
error, the run reports it and continues to the next file — there is no
rollback, so a partial apply is normal and visible in `azz plan status`.

Changing `type` on an existing item is not supported and is skipped with a
notice; delete and recreate instead.

### Recommended workflow

1. Write or edit files in `.azz/tasks/`.
2. Run `azz plan status` and show the user the drift.
3. Ask the user to review the files.
4. Let the user run `azz plan resolve` — do not run it yourself unless
   explicitly told to.

---

## Commands that require explicit user permission (not in allow list)

- `azz edit` — opens an editor to modify title/description; too interactive
- `azz delete` — permanent, irreversible
- `azz plan resolve` — the only plan command that writes to the remote

Never run these without a direct, explicit instruction from the user.

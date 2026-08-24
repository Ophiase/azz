## Start here

```text
azz plan status     # what is tracked locally, and what diverges
```

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
  ~ 7651-langfuse-trace.md     title, description
  + buffer-late-events.md      new task, will be created

Review:  azz plan status
Apply:   azz plan push
```

Rules for that block:

- List every file you touched, `~` for edited and `+` for new.
- Give the two commands verbatim, so they can be copied.
- **Never claim you created, updated or pushed a work item.** Nothing reaches
  Azure DevOps until the developer runs `azz plan push` themselves.

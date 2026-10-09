# Changelog

## Todo

- proper shortcuts
- pr management
- `local_id` so a new work item can parent another new one — decided in
  `docs/decisions/2026-07-31-local-ids.md`, not implemented
- TUI local-edit mode: edit `.azz/tasks` instead of the remote
  (phase 6 of `docs/decisions/2026-07-31-plan-cache.md`)
- an interactive panel to reconcile a divergent item
- descriptions are Markdown on our side: `create -f`, `edit` (and the editor)
  send the text raw into `System.Description`, an HTML field, so ADO shows one
  unformatted block unless we write HTML by hand; convert on write (or set the
  field's Markdown format) and keep `show` rendering it back
- `list` prints the new item's type as `Default` right after `create`, while
  `show` says `Task`

## v0.1

- **v0.1.3**
  - `Ctrl+P` lists every key binding, including the twelve the footer hides
  - the README opens on interactive mode rather than the plan engine
  - `azz --help` describes every command, and shows aliases as `list | l`
    instead of an undocumented entry each
  - interactive: a `P` priority column, and palette commands to raise,
    lower and filter by priority
  - interactive: `/` searches only the rows on screen
  - interactive: critical rows tinted red, rows below High faded
  - interactive: `TB`, `P` and `ID` columns moved to the right of the name
  - interactive: `E` tree view, nesting items under their parent, and
    showing a parent filtered out (e.g. another timebox) dimmed
  - interactive: *Split by priority* palette command, bands keep the sort
  - interactive: tree and priority split on by default; `Space` folds a
    subtree, *Fold all* / *Unfold all* in the palette
  - interactive: Resolved and Closed rows fade out, and Closed groups
    with nothing open sink into a last band
  - `azz plan push|status <file>...` act on the named files only
  - `priority: 1..4` in intent files, compared, pulled and pushed
  - `standard` profile: the agent may push its own files, behind a prompt

- **v0.1.2**
  - plan engine — write work items as Markdown in `.azz/tasks`, review, then
    apply: `azz plan init | fetch | pull | status | push | prune`
  - `.azz/cache` records the remote each file was synced from, so
    `azz plan status` is offline and tells a remote edit from a local one
  - `azz interactive` shows a plan gutter: `●` in sync, `◆` local changes,
    `▼` remote moved, `✗` both changed; `P` refreshes, `?` explains
  - demo mode — `azz --demo`, a fictional board needing no credentials
  - `azz claude install` sets up Claude Code with a skill and permissions,
    and by default adds nothing to the repository

- **v0.1.1**
  - interactive:
    - create item
      - more work item types
      - working timebox
      - description field
    - show item content
    - fix branch crash
  - timebox management
  - task dependencies
  - fix work_item/user_story/task management
  - state update shortcuts
  - claude integration: read-only and standard permission profiles

- **v0.1.0**
  - initial public release

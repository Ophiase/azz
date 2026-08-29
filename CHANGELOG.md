# Changelog

## Todo

- proper shortcuts
- pr management
- `local_id` so a new work item can parent another new one — decided in
  `docs/decisions/2026-07-31-local-ids.md`, not implemented
- TUI local-edit mode: edit `.azz/tasks` instead of the remote
  (phase 6 of `docs/decisions/2026-07-31-plan-cache.md`)
- an interactive panel to reconcile a divergent item
- widen `register(app, engine: Engine)` to `WorkItemBackend` and drop the
  `cast` in `app.py`

## v0.1

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

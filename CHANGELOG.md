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

- **v0.1.1 — 2026-07-31**
    - `azz plan fetch` now records the remote in `.azz/cache` and leaves
      `.azz/tasks` alone; `azz plan pull` writes the working tree
    - `azz plan status` is offline and three-way — it tells a remote edit
      apart from a local one instead of guessing
    - `azz interactive` shows a plan gutter: `●` in sync, `◆` local changes,
      `▼` remote moved, `✗` both changed; `P` refreshes, `?` explains
    - demo mode — `azz --demo` or `AZZ_DEMO=1`, a fictional board needing no
      Azure DevOps credentials
    - `azz claude install` installs a Claude Code skill and an `AGENTS.md`
      note instead of a `CLAUDE.md` block, and retires the old block on
      re-install; the skill makes the agent report which intent files it
      changed and the command to apply them
    - `azz plan pull` is now in the installed permissions and docs
    - retire the `remote_changed_date` frontmatter key
    - fix `StateFilter`, which silently matched nothing for a single state

- **v0.1.0**
    - plan engine:
        - local intent files in `.azz/tasks/*.md`
        - `azz plan init` — create the gitignored `.azz/` directory
        - `azz plan fetch` — mirror remote items into local Markdown files
        - `azz plan status` — read-only drift against the remote
        - `azz plan push` — apply with per-change confirmation
        - `azz plan prune` — delete the local files of Closed, in-sync items
          (`--dry-run`, `--yes`; never touches the remote)
        - `azz plan fetch --limit 0` — no cap, so `-a -l 0` archives everything
        - `item_id` write-back after creation
        - `remote_changed_date` metadata to separate remote edits from local ones
    - claude integration:
        - `azz claude install [planning|standard]` — docs + permissions in one step
        - `azz claude list` — describe the profiles
        - profiles ship inside the package; `read-only` renamed to `planning`
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

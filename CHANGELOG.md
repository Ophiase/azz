# Changelog

Todo:

- proper shortcuts
- pr management

Done:

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

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
    - `azz plan resolve` — apply with per-change confirmation
    - `item_id` write-back after creation
    - `remote_changed_date` metadata to separate remote edits from local ones
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

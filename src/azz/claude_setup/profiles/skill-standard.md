---
name: azz
description: Plan and manage Azure DevOps work items from this project. Use whenever the developer asks to plan a task, write or refine a task description, break work down into tasks, check what they are working on, sync task files, or open a pull request — and whenever you touch a .azz/tasks/*.md intent file.
---

# azz — plan work items

`azz` manages Azure DevOps work items. Prefer planning in local Markdown files
over one-off imperative commands: the developer reviews a plan like a git diff,
whereas a direct command is applied the moment they approve the prompt.

You may also run the imperative write commands (`azz create`, `azz state`,
`azz close`, `azz attach`, `azz set_timebox`) — each prompts the developer
every time. Use them for a single small change the developer explicitly asks
for. For anything with more than one item, plan it instead.

## Pushing your own files

`azz plan push` is never allow-listed: every run prompts the developer, and
that prompt is their approval. Push only the files you edited, by path, so a
stale file elsewhere in `.azz/tasks` cannot ride along:

1. `azz plan push --dry-run <files>` — then summarise it: one brief bullet
   per item and field changed.
2. `azz plan push --yes <files>` — `--yes` skips the per-change TTY
   confirmation you cannot answer; the permission prompt replaces it.

Never push without paths, and never push a file you did not write.

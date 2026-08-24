---
name: azz
description: Plan and manage Azure DevOps work items from this project. Use whenever the developer asks to plan a task, write or refine a task description, break work down into tasks, check what they are working on, or sync task files — and whenever you touch a .azz/tasks/*.md intent file.
---

# azz — plan work items

`azz` manages Azure DevOps work items. Prefer planning in local Markdown files
over one-off imperative commands: the developer reviews a plan like a git diff,
whereas a direct command is applied the moment they approve the prompt.

You may also run the imperative write commands (`azz create`, `azz state`,
`azz close`, `azz attach`, `azz set_timebox`) — each prompts the developer
every time. Use them for a single small change the developer explicitly asks
for. For anything with more than one item, plan it instead.

`azz plan push` is never allow-listed. Only the developer runs it.

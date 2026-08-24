---
name: azz
description: Plan and manage Azure DevOps work items from this project. Use whenever the developer asks to plan a task, write or refine a task description, break work down into tasks, check what they are working on, or sync task files — and whenever you touch a .azz/tasks/*.md intent file.
---

# azz — plan work items

`azz` manages Azure DevOps work items. You plan in local Markdown files; the
developer applies the plan.

**In this project you cannot change Azure DevOps at all.** Every write command
is denied at the harness level. That is the workflow, not an obstacle: you
write intent files, the developer reviews them like a git diff and runs
`azz plan push` themselves.

Read-only commands you may run freely: `azz list`, `azz show <ID>`,
`azz timebox`, `azz plan status`, `azz plan fetch`, `azz plan pull`.

## Task management — azz

Work items live in Azure DevOps and are planned locally as Markdown intent
files in `.azz/tasks/` (gitignored). `azz plan status` shows what is tracked
and what diverges; `azz plan fetch` then `azz plan pull` bring items in.

Edit `.azz/tasks/*.md` freely — it is local and reversible. Never run
`azz plan push`: only the developer applies a plan to the board. After
editing intent files, list what changed and tell the developer to run
`azz plan status` then `azz plan push`.

Claude Code users get this as the `azz` skill, with the file format and the
full workflow. Others: run `azz plan status --help` and `azz --help`.

# Azz - Azure Devops CLI helper

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-green.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.14+](https://img.shields.io/badge/Python-3.14%2B-yellow.svg)](https://www.python.org/)
[![UV](https://img.shields.io/badge/uv-available-brightgreen.svg)](https://astral.sh/uv)
[![Justfile](https://img.shields.io/badge/just-available-brightgreen.svg)](https://just.systems/man/en/)
[![Docker](https://img.shields.io/badge/Docker-available-blue.svg)](https://www.docker.com/)

A simple CLI tool to help with Azure DevOps work item management,
built on top of the Azure CLI.

I only built this tool for myself,
but I thought it could be useful for others as well,
so I decided to make it public.
Feel free to clone it to adapt it to your needs.

## Installation

Requirements:

- [azure cli](https://learn.microsoft.com/en-us/cli/azure/get-started-with-azure-cli?view=azure-cli-latest)
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- An Azure DevOps organization and project
  - the tool is based on the Epic-Feature-Task work item hierarchy

Recommended:

- unix-like environment
  The tool was only tested on Linux
- [direnv](https://github.com/direnv/direnv)
  For loading environment variables from .envrc files.
  It permits you to have different configurations for different projects.

Installation:

```bash
# From pypi
uvx add azz # Not published yet, but will be available soon

# From source 
git clone
cd Azz

uv tool install . # classic install
just install # classic install using justfile
uv tool install --editable . # dev install
just install-dev # dev install using justfile
```

Then to verify the installation

```bash
azz --version
```

## Usage

In your project repository,
configure a `.envrc` file like `.envrc.example`.

### Plan engine

Declarative work item management: express the desired state in local files,
diff it against Azure DevOps, apply it with confirmation.

```bash
azz plan init                # create the gitignored .azz/ directory
azz plan fetch               # mirror your 20 most recent items into .azz/tasks
azz plan fetch 7651 7695     # or just these ones
azz plan fetch -a -l 0       # everything, Closed included — a full local archive
```

One Markdown file per work item under `.azz/tasks/`:

```markdown
---
item_id: 1234
title: Implement login page
state: Active
type: Task
parent: 100
iteration: Sprint 42
remote_changed_date: "2026-07-29T10:12:33+00:00"
---

The body of the file is the work item description.
```

Omit `item_id` to mark the file as a new task — it is written back into the
file once the item is created. Fields absent from the frontmatter are never
compared and never written, so a file containing only `title` will only ever
touch the title. `remote_changed_date` is tool-managed; it records when the
remote last changed so `azz` can tell a remote edit apart from a local one.

Only the items you are working on are kept locally. Fetch as many as you
want, delete the files you no longer need — a missing file never means
"delete the work item".

```bash
azz plan status           # read-only diff against the remote
azz plan push             # apply, confirming each change
azz plan push --dry-run   # same output as status
azz plan push --yes       # apply without per-change confirmation
```

Re-running `azz plan fetch` refreshes files whose remote moved since the last
fetch, and keeps files you have edited locally — pass `--force` to overwrite
those too.

Fetch options: `-l/--limit N` (default 20, `0` for no limit), `-a/--all` to
include Closed items, `-c/--current-timebox`, `-f/--force`. `-a -l 0` pulls
the same set as `azz list -a` — every work item assigned to you in the
configured projects, whatever its state.

Once the archive is on disk, prune it back to the work in flight:

```bash
azz plan prune --dry-run   # list what would go
azz plan prune             # delete, after one confirmation
azz plan prune --yes       # delete without confirming
```

`prune` removes a file only when the work item is Closed on the remote *and*
the file is in sync with it. Local drift, files with no `item_id`, and files
whose item is gone from the remote are always kept.

`.azz/` is gitignored by default. A missing file never means "delete" —
`prune` only ever touches local files, and deletion on Azure DevOps stays
explicit via `azz delete`.

See [the design decision](docs/decisions/2026-07-24-plan-engine.md) for the
rationale.

### Claude integration

From the project you want Claude to work on:

```bash
azz claude install            # planning profile (default)
azz claude install standard
azz claude list               # what each profile grants
```

This appends the command docs to `CLAUDE.md` and merges the matching
permissions into `.claude/settings.json`, preserving anything already there.
The `planning` profile lets Claude author intent files but denies every
command that writes to Azure DevOps — you apply its plans with
`azz plan push`.

See [docs/claude.md](docs/claude.md) for details.

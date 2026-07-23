# Plan Engine — Local Intent Files + Remote Sync

**Date:** 2026-07-24
**Status:** Decided (revised — see end)

---

## Context

`azz` currently wraps Azure DevOps imperatively: every command hits the
remote immediately. There is no way for an agent (Claude) to author a
batch of changes, let the human review them, and then apply them in one
controlled step.

The immediate need is: Claude plans work items locally, the human reviews,
then a single command syncs to Azure DevOps.

The broader vision: this tool will eventually support multiple backends
(GitHub Projects, Jira, Linear, …). But that is a future concern.
The objective right now is a working implementation on Azure DevOps.

---

## Problem Statement

Two distinct problems are bundled together here:

1. **Safety for agentic use.** Claude should be able to write local files
   freely and the human should control when remote state changes.
2. **Declarative task management.** Treating work items like code: express
   desired state in files, diff against reality, apply with confirmation.

Both problems share the same solution shape.

---

## Non-Goals (for this decision)

- Multi-backend support — not now, not designed for proactively.
- Team collaboration on `.azz/` files — opt-in, not enforced.
- A local state cache (`.azz-state.json` / tfstate equivalent) — deferred;
  AzDO item fetches are cheap enough to always go to the remote.
- Conflict resolution — if the remote changed since you authored the intent
  file, `resolve` shows the conflict and stops. Manual resolution.
- Deletion via plan files — `azz delete` stays explicit. A missing file
  does not mean "delete".

---

## Design Decisions

### 1. Module boundary

The plan engine lives at `src/azz/plan/`. It imports `WorkItem` from
`src/azz/core/` directly — no abstraction layer, no generic types.

The goal is clean code organization, not backend portability.
If a second backend is added later, the extraction of a shared interface
is a refactor done at that point, on a well-structured module.
Doing it now would be speculative.

```text
src/azz/
  plan/
    __init__.py
    models.py       ← LocalItem, Changeset, Change, ChangeType
    parser.py       ← .md frontmatter → LocalItem
    diff.py         ← (LocalItem[], Engine) → Changeset
    writer.py       ← writes item_id back into .md after creation
    renderer.py     ← formats status / resolve output for the terminal
  core/             ← Azure DevOps backend (unchanged)
    engine.py
  cli/
    plan.py         ← `azz plan status` and `azz plan resolve` commands
```

### 2. Dependency on Engine

`src/azz/plan/diff.py` imports `Engine` and `WorkItem` directly.
No callable injection, no Protocol, no adapter layer.

```python
# src/azz/plan/diff.py

from azz.core.engine import Engine
from azz.plan.models import LocalItem, Changeset

def compute_changeset(
    local_items: Sequence[LocalItem],
    engine: Engine,
) -> Changeset: ...
```

When a second backend is needed, the right move at that time is to
extract a `PlanBackend` Protocol from `Engine`'s surface and make
`compute_changeset` depend on it. That refactor is straightforward on
a module this size. There is no point doing it before there are two
backends to unify.

### 3. Intent file format

```markdown
---
item_id: 1234
title: Implement login page
state: Active
type: Task
parent: 100
iteration: Sprint 42
---

Free-form description. The body of the file is the work item description.
Frontmatter fields take precedence over the body for structured fields.
```

Rules:

- `item_id` absent → `ChangeType.CREATE` on resolve.
- `item_id` present → `ChangeType.UPDATE` if any field differs,
  `ChangeType.NOOP` if in sync.
- Fields absent from frontmatter are **not compared and not updated**.
  A minimal file with only `title` will only ever touch the title.
- After `resolve` creates an item, the `item_id` is written back into
  the file. The file becomes the source of truth for subsequent diffs.

### 4. `.azz/` directory layout

```text
.azz/
  tasks/
    <slug>.md    ← one file per work item intent
```

The directory is gitignored by default. Teams that want to version
planned (uncreated) items can un-ignore it selectively. The filename
`<slug>.md` has no machine meaning — it is a human label only.

### 5. `azz plan status` — read-only diff

Outputs a structured view of drift:

```text
[NEW]    .azz/tasks/new-api.md             → will create Task under #100
[DRIFT]  .azz/tasks/login.md (#1234)
           state:     Active (local) ≠ Resolved (remote)
[NOOP]   .azz/tasks/fix-crash.md (#5678)  ✓ in sync
[GONE]   .azz/tasks/old-feature.md (#999) → item not found on remote
```

`GONE` means the remote item was deleted or the ID is wrong. Resolve
will skip this file — the human must handle it manually.

### 6. `azz plan resolve` — apply with confirmation

- Iterates changes in order: creates first, updates second.
- Confirms per file (default) or with `--yes` for all.
- On create: writes `item_id` back into the `.md` file immediately.
- On any error: reports and continues to the next item (no rollback —
  partial apply is visible and recoverable).
- `--dry-run` is an alias for `status` with resolve-style output.

### 7. Permissions model for Claude

Claude is allowed to read and write `.azz/tasks/*.md` files freely.
`azz plan status` is read-only and can be in the `allow` list.
`azz plan resolve` requires explicit confirmation — it stays out of
`allow`, so every invocation triggers a user prompt.

This gives Claude full planning autonomy while keeping the human in the
loop for all remote state changes.

---

## Rejected Alternatives

**Single `azz plan` command for both status and resolve.**
Rejected: separating them makes it natural to run status in CI or from
Claude without risk. Two commands, unambiguous intent.

**YAML files instead of Markdown.**
Rejected: Claude writes better prose descriptions in Markdown. The
frontmatter/body split lets the description be a first-class field
without forcing it into a YAML string literal.

**Storing a local state cache (like `terraform.tfstate`).**
Rejected for now: adds write-on-every-operation complexity. AzDO API
calls for individual items are fast. Revisit if `status` becomes slow
across large `.azz/` directories.

**Deletion via plan files (missing file = delete).**
Rejected: too much blast radius. A misplaced gitignore or an accidental
`rm` becomes a production incident. Deletion stays an explicit imperative
command (`azz delete`).

**Proactive backend abstraction (callable injection, `RemoteItem` type).**
Rejected: YAGNI. The plan module is a clean, bounded unit that can be
refactored when a second backend actually exists. Building the abstraction
now adds complexity with no present benefit and risks getting the interface
wrong because we have only one data point.

---

## Verdict

Ship `src/azz/plan/` as a well-organized module that imports `Engine`
directly. No abstraction layer, no generic types. Make it work on Azure
DevOps first. Extract a `PlanBackend` Protocol if and when a second
backend is added.

The two CLI commands are `azz plan status` (safe, allow-listed) and
`azz plan resolve` (gated, confirmation-required).
No local state cache. No deletion via plan files.

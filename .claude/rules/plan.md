---
paths:
  - "src/azz/plan/**"
  - "src/azz/cache/**"
  - "tests/**/*plan*.py"
---

# Plan Engine

Read this before touching `src/azz/plan/`, `src/azz/cache/`, or any
`azz plan *` command. Keep it updated in the same change when you alter the
model.

The *why* lives in the decision records — read them before proposing a
design change, not before a small fix:

- [2026-07-24-plan-engine.md](../../docs/decisions/2026-07-24-plan-engine.md)
  — the shipped two-part design and its rejected alternatives.
- [2026-07-31-plan-cache.md](../../docs/decisions/2026-07-31-plan-cache.md)
  — **Accepted and shipped** through phase 5. Adds `.azz/cache/` as a merge
  base and makes `status` offline. Supersedes the earlier record's rejection
  of a cache. Its addendum explains why the cache is also a second backend.
- [2026-07-31-local-ids.md](../../docs/decisions/2026-07-31-local-ids.md)
  — **Accepted, not implemented.** `local_id` so a new item can parent
  another new one. Read it before touching `parent` or the create ordering.

## Module map

```text
src/azz/plan/
  discovery.py    find_plan_root (walks up like git), tasks/cache paths
  initializer.py  creates .azz/ + .azz/.gitignore containing `*`
  frontmatter.py  text → (metadata, body)
  parser.py       .md → LocalItem, rejects unknown keys
  serializer.py   WorkItem → .md text
  writer.py       upserts single keys back into an existing .md
  slug.py         WorkItem → filename (human label, no machine meaning)
  diff.py         (LocalItem[], Engine) → Changeset
  resolver.py     RemoteResolver — all tracked ids in one query
  batch_reader.py BatchWorkItemReader — the optional batching capability
  comparison.py   field-by-field diffing, HTML/Markdown normalization
  snapshots.py    Snapshots — the two cache generations for one plan root
  snapshot_diff.py remote_advanced — has the remote moved past a snapshot
  fetch_clock.py  FetchClock — stamps and reads .azz/cache/fetched-at
  applier.py      pushes one Change to the remote
  fetcher.py      records one remote item in .azz/cache (never .azz/tasks)
  puller.py       fast-forwards .azz/cache into .azz/tasks
  inspector.py    the offline three-way comparison behind `status`
  pruner.py       deletes local files of Closed, in-sync items
  renderer.py     all terminal output
  sync_renderer.py output for status and pull
  tracking.py     TrackingStatus glyphs, consumed by the TUI
  models/         one class per file
src/azz/cache/
  store.py        CacheStore — per-id JSON files, one store per generation
  payload.py      ItemPayload — raw az JSON ↔ WorkItem
  backend.py      CacheBackend — WorkItemBackend over a CacheStore
  assignee_filter.py  AssigneeFilter — no assignee means the owner's
src/azz/backend/
  protocol.py     WorkItemBackend — the 12-method surface every caller uses
src/azz/demo/     the fictional board; a CacheBackend over a fixture
src/azz/tui/
  plan_state.py   PlanState — the plan's view of the on-screen items
  plan_legend.py  the `?` legend, built from TrackingStatus
```

`BatchWorkItemReader` is deliberately *not* part of `WorkItemBackend`: it is
checked at runtime, so a backend without the capability still works and just
costs one call per id. Keep optional capabilities as separate
`runtime_checkable` protocols rather than widening the main surface.

`Engine` satisfies `WorkItemBackend` structurally, and so would a
cache-backed source. New code that reads work items should depend on the
protocol, not on `Engine` — that is what makes offline and demo modes
possible without callers knowing the difference. Existing code still imports
`Engine` directly; migrate opportunistically, not in bulk.

## The cache has two generations

Both are `CacheStore` instances over different directories, from
`plan/discovery.py`:

- `.azz/cache/items/` — the **merge base**: the remote state each intent file
  was last synced from. Only `pull` and `push` advance it, because only those
  leave the working tree agreeing with the remote.
- `.azz/cache/fetched/items/` — the **newest remote state** `fetch` saw, which
  may be ahead of the working tree.

Keeping them apart is the point: a `fetch` must never destroy the only record
of what a file was synced from. Do not collapse them, and do not advance the
merge base from `fetch` except for files it actually brought level with the
remote.

`.azz/cache/fetched-at` stamps the last fetch, so a command can report how
stale the cache is.

## Invariants

- **A `None` field on `LocalItem` means absent from the frontmatter.** It is
  never compared and never pushed. A file with only `title` can only ever
  change the title. Do not introduce defaults that break this.
- **A missing file never means delete.** Deletion is explicit
  (`azz delete`, or `azz plan prune` for local files only).
- **`prune` never touches the remote.** Local files only, and only Closed
  items that are in sync.
- **`push` has no rollback.** Errors are reported per change and the loop
  continues — a partial apply must stay visible and recoverable.
- **`item_id` matches files to remote items, not the filename.** A file keeps
  its name after the remote title changes.
- **Write-back includes the title**, because
  `create_work_item_helper` may prepend a `[project]` marker. Without it
  every freshly created item reports `DRIFT` on the next `status`.
- **`type` is compared but never pushed** on an existing item. Azure DevOps
  treats it as a different operation and `Engine` does not expose it.
- **`remote_changed_date` is retired.** The merge base replaced it. The
  parser still accepts and ignores the key so old files parse; do not
  reintroduce a tool-managed timestamp in a human-readable file.
- **`fetch` never writes `.azz/tasks/`.** It records the remote in the cache;
  `pull` writes the working tree. Collapsing them removes the merge base.
- **Descriptions are lossy.** Remote is HTML, local is Markdown. Comparison
  normalizes both (`normalize_markdown`) to survive the round-trip. Any
  change here risks either phantom drift or silently unpushed edits.

## Current state of the cache migration

Against the phasing proposed in the 2026-07-31 record. Check this table
against `git log` before trusting it — the engine is under active work.

| Phase | State |
|---|---|
| 1. Batch remote lookups in `compute_changeset` | **done** — `RemoteResolver` resolves all tracked ids in one query |
| 2. `.azz/cache/` populated by `fetch` | **done** — both generations written; nothing read them at the time |
| 3. Three-way offline `status`, `azz plan pull` | **done** — `status` makes no remote call; `pull` fast-forwards and refuses conflicts |
| 4. Drop `remote_changed_date` | **done** — still tolerated in `KNOWN_FIELDS` so old files parse |
| 5. TUI glyph column | **done** — `PlanState` wraps `tracking.py`, `P` refreshes, `?` shows the legend |
| 6. TUI local-edit mode | not started |

Phase 6 is the only one left. Demo mode was added outside this phasing: it is
a `CacheBackend` over a bundled fixture, selected in `AzzApp` before
`EngineConfig.from_env()` runs, so it needs no credentials.

Two properties the landed work relies on, worth preserving:

- **Plan state never breaks the TUI.** Any failure loading it degrades to an
  empty mapping, and unparseable intent files are skipped rather than raised.
  A broken `.azz/` must not stop remote items from rendering.
- **Glyphs, colours and wording come from `TrackingStatus`**, so the TUI
  cannot drift from the plan engine. Add a state there, not in the TUI.

## Permission model

The safety argument of the whole engine: Claude authors local files freely,
the human controls remote writes.

- `azz plan init` / `fetch` / `pull` / `status` / `prune --dry-run` are safe
  and allow-listed. `status` and `pull` are offline; only `fetch` needs the
  network, and none of them write to Azure DevOps.
- `azz plan push` must **never** be allow-listed — every invocation prompts.
- Reading and writing `.azz/tasks/*.md` needs no confirmation.

The shipped profiles are in `src/azz/claude_setup/profiles/`. Changing a
command's blast radius means updating them in the same change.

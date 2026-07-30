# Plan Engine

Read this before touching `src/azz/plan/`, `src/azz/cache/`, or any
`azz plan *` command. Keep it updated in the same change when you alter the
model.

The *why* lives in the decision records — read them before proposing a
design change, not before a small fix:

- [2026-07-24-plan-engine.md](../docs/decisions/2026-07-24-plan-engine.md)
  — the shipped two-part design and its rejected alternatives.
- [2026-07-31-plan-cache.md](../docs/decisions/2026-07-31-plan-cache.md)
  — **Proposed**, not shipped. Adds `.azz/cache/` as a merge base and makes
  `status` offline. Supersedes the earlier record's rejection of a cache.

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
  comparison.py   field-by-field diffing, HTML/Markdown normalization
  freshness.py    remote_changed_date heuristic
  applier.py      pushes one Change to the remote
  fetcher.py      writes one remote item into .azz/tasks/
  pruner.py       deletes local files of Closed, in-sync items
  renderer.py     all terminal output
  tracking.py     TrackingStatus glyphs — cache-based, not yet wired
  models/         one class per file
src/azz/cache/
  store.py        CacheStore — per-id JSON files under .azz/cache/
  payload.py      ItemPayload — raw az JSON ↔ WorkItem
src/azz/backend/
  protocol.py     WorkItemBackend — the 12-method surface every caller uses
```

`Engine` satisfies `WorkItemBackend` structurally, and so would a
cache-backed source. New code that reads work items should depend on the
protocol, not on `Engine` — that is what makes offline and demo modes
possible without callers knowing the difference. Existing code still imports
`Engine` directly; migrate opportunistically, not in bulk.

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
- **`remote_changed_date` is tool-managed.** Written on fetch and after
  push, never compared as a field.
- **Descriptions are lossy.** Remote is HTML, local is Markdown. Comparison
  normalizes both (`normalize_markdown`) to survive the round-trip. Any
  change here risks either phantom drift or silently unpushed edits.

## Current state of the cache migration

`src/azz/cache/` and `plan/tracking.py` exist and are correct, but they are
**scaffolding — nothing writes the cache and nothing calls
`tracking_statuses` yet**. Do not treat this as a bug to fix opportunistically.

Where the code stands against the proposed phasing:

| Phase | State |
|---|---|
| 1. Batch remote lookups in `compute_changeset` | not done — `diff.py` still calls `Engine.get_workitem` once per file |
| 2. `.azz/cache/` populated by `fetch` | store written, **not populated** |
| 3. Three-way offline `status`, `azz plan pull` | not started |
| 4. Drop `remote_changed_date` | not started — `freshness.py` is still live |
| 5. TUI glyph column | `TrackingStatus` ready, not wired |
| 6. TUI local-edit mode | not started |

Phase 1 is independent and safe. Phase 3 changes what `azz plan fetch`
means and needs its own review before implementation — do not start it
without being asked.

## Permission model

The safety argument of the whole engine: Claude authors local files freely,
the human controls remote writes.

- `azz plan init` / `fetch` / `status` / `prune --dry-run` are safe and
  allow-listed.
- `azz plan push` must **never** be allow-listed — every invocation prompts.
- Reading and writing `.azz/tasks/*.md` needs no confirmation.

The shipped profiles are in `src/azz/claude_setup/profiles/`. Changing a
command's blast radius means updating them in the same change.

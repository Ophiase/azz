# Plan Cache — a local copy of the remote, like git

**Date:** 2026-07-31
**Status:** Proposed
**Supersedes part of:**
[2026-07-24-plan-engine.md](./2026-07-24-plan-engine.md) — specifically its
rejection of a local state cache, and the `remote_changed_date` workaround
added in that document's addendum.

---

## Context

The plan engine shipped with two moving parts: `.azz/tasks/*.md` (local
intent) and the remote. Two parts means every comparison is two-way, and a
two-way comparison cannot answer the question that matters.

The 2026-07-24 record rejected a local state cache on the grounds that
"AzDO item fetches are cheap enough to always go to the remote". That was
right about cost and wrong about correctness. This document proposes adding
the third part.

The idea, in the user's words: `.azz/cache/` is our knowledge of the remote,
`.azz/tasks/` is our working tree, and `fetch` updates the cache rather than
the working tree — exactly the distinction git draws between `git fetch` and
`git pull`.

---

## Problem 1 — drift is ambiguous

A file that differs from the remote has two possible causes, and today they
are indistinguishable:

- the user (or Claude) edited the file
- someone edited the work item on Azure DevOps

Both render as `[DRIFT]`. `fetch` has to guess which one it is to decide
whether refreshing the file is helpful or destructive.

The shipped workaround is `remote_changed_date` in the frontmatter: record
when the remote last changed, and treat "the remote's timestamp moved" as
"the remote is authoritative". It works for the common case and it is
honest about its failure — when *both* sides changed, `fetch` takes the
remote and the local edit is lost.

A merge base removes the guess. With a snapshot of what the remote looked
like at the last fetch, each side can be compared to the base independently:

| tasks vs cache | cache vs remote | Meaning | Action |
|---|---|---|---|
| same | same | in sync | nothing |
| same | differs | remote-only change | fast-forward the file |
| differs | same | local-only change | safe to push |
| differs | differs | both changed | conflict — stop |

This is the same table git uses, and it is exact rather than heuristic.

## Problem 2 — `status` costs one subprocess per file

`compute_changeset` calls `Engine.get_workitem` once per tracked file, and
each call spawns an `az` subprocess. Twenty files is twenty sequential
process launches.

This is about to get much worse. The backup workflow — fetch every work
item in the project, Closed ones included, as a personal archive — turns
`.azz/tasks/` into hundreds of files. `azz plan status` would become
unusable at exactly the moment the directory becomes interesting.

**A cache is not the cheapest fix for this.** `Engine.list_work_items`
already retrieves many items in a single WIQL query, so `compute_changeset`
could batch its lookups into one call and get the same speedup with none of
the design cost. That fix should happen regardless of what this document
decides.

What the cache adds beyond batching is that `status` needs **no network at
all**. It becomes pure local I/O: instant, safe to allow-list for Claude
with no rate-limit concern, and usable on a plane. That is a different
property from "fast", and it is the one that makes the TUI integration below
viable.

---

## Design

### Layout

```text
.azz/
  cache/
    7651.json      ← raw az response, keyed by work item id
    7695.json
  tasks/
    7651-langfuse-trace.md   ← working tree, human/agent owned
```

The cache is machine-owned. Nothing in it is meant to be edited by hand,
which is why it is keyed by id rather than by slug.

### Cache format: raw `az` JSON

Store the untouched JSON that `az boards work-item show` returned, and
rehydrate it with the existing `work_item_factory`.

The alternative — storing a rendered intent file, so cache and working tree
are the same format — is tempting because the comparison becomes a plain
text diff. It is rejected because it bakes the lossy HTML-to-Markdown
conversion into the merge base. Descriptions would round-trip twice and
phantom conflicts would appear. The raw response is the honest record of
what the remote actually said.

### Command semantics

| Command | Reads | Writes | Network |
|---|---|---|---|
| `azz plan fetch` | remote | cache | yes |
| `azz plan status` | cache + tasks | — | **no** |
| `azz plan pull` | cache + tasks | tasks | no (fetch first) |
| `azz plan push` | tasks | remote, then cache | yes |

`fetch` stops being a pull. That is the central behavioural change and the
one most likely to surprise: today `azz plan fetch` writes `.azz/tasks/`
directly, and after this it would not. Anyone relying on the current
behaviour wants `azz plan pull`.

`pull` fast-forwards every file whose local side is unchanged, and refuses
the ones where both sides moved, listing them. No automatic merge, no
three-way text merge of descriptions — a conflict is reported and the human
resolves it. That matches the original record's "shows the conflict and
stops".

### `remote_changed_date` goes away

It exists only because there was no merge base. Once the cache is
populated, the field is redundant and should be dropped from the
frontmatter — one less tool-managed key in a file meant to be human-readable.

Migration is trivial: the first `fetch` after upgrading populates the cache
for every tracked id, and the parser can ignore the stale key for a release.

---

## TUI integration

`azz interactive` shows remote items. With a cache it can also show each
item's relationship to the plan, in a leading glyph column:

```text
  ◆ 27/07  7441  44  Task  New   plan multi-prompt form-aware strategy
  ● 27/07  7412  44  Epic  New   Document Analysis Improvement Propositions
    27/07  7699  44  Task  New   [IR] Temporal/Modal Logic handling
```

| Glyph | Meaning |
|---|---|
| *(blank)* | remote only — not tracked in `.azz/tasks/` |
| `●` | tracked, in sync |
| `◆` | tracked, local changes not yet pushed |
| `▼` | tracked, remote moved since the last fetch |
| `✗` | tracked, both sides changed — conflict |

**On the performance concern.** This costs one directory scan of
`.azz/tasks/` and `.azz/cache/` at startup, then pure in-memory lookups by
id. No additional `az` calls, so the TUI does not get slower.

Worth noting honestly: the TUI already holds the remote items it just
listed, so the *blank vs tracked* and *in sync vs differs* distinctions are
computable today without any cache. It is the last two rows of that table —
telling `◆` apart from `▼` and `✗` — that need the merge base.

### Local-edit mode

The natural follow-on: a toggle in the TUI between editing the remote
directly (today's behaviour) and editing the plan. In plan mode, rename /
state-change / timebox actions write to `.azz/tasks/*.md` instead of calling
the engine, and the item picks up a `◆`. The user then reviews and runs
`azz plan push`.

This is the same safety argument as the `planning` permission profile,
applied to the human interface: make the reviewable path the easy path.

It should be a clearly indicated mode — a footer marker and a different
accent colour — because two modes with identical keybindings and different
targets is exactly how people destroy data by accident.

---

## Rejected alternatives

**Keep `remote_changed_date`, skip the cache.** It is genuinely cheaper and
covers the common case. Rejected because the failure mode is silent data
loss on the local side, and because it cannot make `status` offline. It was
always labelled a workaround.

**Cache the rendered intent file instead of raw JSON.** Rejected above:
double lossy conversion in the merge base.

**One combined cache file (`.azz/cache.json`).** Fewer inodes, one atomic
write. Rejected: every fetch rewrites the whole file, concurrent runs race
on it, and per-id files make partial fetches trivial. Revisit only if inode
count ever becomes a real complaint.

**Store the cache inside the `.md` files** (e.g. a second frontmatter block
holding the last-known remote state). Rejected: it doubles the size of
files a human is supposed to read, and it couples the merge base's lifetime
to the working tree's.

**Skip the cache and just batch the lookups.** This is the serious
alternative and it should be done anyway — it fixes Problem 2 at a fraction
of the cost. It does not fix Problem 1, does not make `status` offline, and
does not enable the last two TUI glyphs. Do both; batching first.

---

## Phasing

Each phase is shippable on its own and none of them strand the previous one.

1. **Batch the remote lookups in `compute_changeset`.** Independent of
   everything else here, immediate win, no new concepts. Do this first.
2. **Introduce `.azz/cache/`, populated by `fetch`, unused by anything.**
   Pure addition, no behaviour change. Lets the format settle before
   anything depends on it.
3. **Make `status` three-way and offline.** The payoff phase. Add
   `azz plan pull`; `fetch` stops writing the working tree.
4. **Drop `remote_changed_date`.**
5. **TUI glyph column.**
6. **TUI local-edit mode.**

Phases 1 and 2 are safe to do now. Phase 3 is the one that changes a
command's meaning and deserves its own review.

---

## Open questions

- Does `push` update the cache from the create/update response, or re-fetch
  the item afterwards? The response is cheaper; a re-fetch is accurate about
  server-side mutations such as the project-name prefix. The current
  `Applier` already re-fetches to record the timestamp, so re-fetching keeps
  the call count unchanged.
- Should `status` warn when the cache is old, the way `git status` says
  "your branch is behind"? Probably yes, with a "last fetched N hours ago"
  line — a silently stale cache is the main cost of separating fetch from
  pull.
- Should the cache be pruned when a file is deleted from `.azz/tasks/`?
  Leaning no: keeping it costs nothing and makes re-adding an item offline
  possible. But it does mean the cache grows without bound after a
  full-project backup fetch.
- What happens to a cached item that no longer exists on the remote? Today
  that surfaces as `[GONE]`. The cache should probably keep the last known
  copy rather than delete it — it may be the only remaining record.

---

## Verdict

Adopt the cache, but do the cheap fix first.

Batching the lookups in `compute_changeset` should land independently and
soon — it removes the immediate scaling problem that the backup workflow
creates. The cache is then justified on correctness rather than speed: it
provides the merge base that turns a guess into a decision, and it makes
`status` an offline operation.

Do not build phases 5 and 6 before phase 3 is in use for a while. The TUI
work is the visible, appealing part and the easiest to get wrong before the
underlying model has been lived with.

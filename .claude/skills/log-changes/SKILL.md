---
name: log-changes
description: "Add the minimal CHANGELOG.md entry for user-visible work and keep VERSION and pyproject.toml in sync. Owns the patch numbering."
disable-model-invocation: true
---

# Record changes in the CHANGELOG

Add an entry for work that is user-visible. Keep [CHANGELOG.md](../../../CHANGELOG.md)
readable at sight.

## Decide first: does this belong?

Only significant, user-visible changes. Skip internal refactors, test
changes, formatting, and scaffolding nothing consumes yet.

If in doubt, propose the line and ask rather than writing it.

## Steps

1. `just version` — VERSION, `pyproject.toml` and the latest CHANGELOG entry
   must already agree. If they do not, report it before touching anything.
2. `git log --oneline origin/main..HEAD` to see what is unreleased locally.
   Never bump more than one patch ahead of the remote head.
3. Choose the entry:
   - Extend the latest `- **vX.Y.Z**` bullet if this is the same concern.
   - Open a new patch bullet if it is a distinct concern:
     `- **v0.1.1**` under the existing `## v0.1` section. Never add a date:
     the changelog carries versions only.
   - **Never** open a new `## vX.Y` section — minor versions are the
     developer's call only.
4. Write the lines. One line per change, imperative, no marketing. Match the
   existing nesting.
5. If you opened a new patch bullet, update `VERSION` and the `version` field
   in `pyproject.toml` to match.
6. `just version` again to confirm all three agree.

## Style

Compare against what is already there — that is the target density.

- `azz plan prune` — delete the local files of Closed, in-sync items
- Never a paragraph. Never an explanation of why. The commit message holds
  the reasoning; the CHANGELOG holds the fact.

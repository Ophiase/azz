---
name: commit
description: "Commit the current uncommitted work in the repo's message style, after just checks passes. Never pushes, never rewrites history."
disable-model-invocation: true
allowed-tools: Bash(git status:*) Bash(git diff:*) Bash(git add:*) Bash(git commit:*) Bash(git log:*) Bash(just checks) Bash(just rumdl-fmt)
---

# Commit the current work

Only commit when this command is invoked. Never commit spontaneously.

## Steps

1. `git status` and `git diff` (plus `git diff --staged`) to see everything
   that changed. Read the actual diff — do not commit from memory.
2. `just checks` must pass. If it fails, fix it or stop and report; never
   commit over a failing check.
3. If any `.md` changed and `rumdl` complains, run `just rumdl-fmt`.
4. Decide whether this warrants a CHANGELOG entry — see `/log-changes`.
   Most internal refactors do not.
5. If not already on a topic branch, say so and ask before committing to
   `main`.
6. Stage deliberately. Never `git add -A` without checking what it picks up.
7. Commit with a message in the repo's style (below).
8. Report the resulting `git log -1 --stat`. Do not push.

## Message style

Match the existing history — it is informative, not terse.

- Subject: imperative mood, sentence case, no `feat:`/`fix:` prefix, no
  trailing period. `Add the backend protocol and the remote cache store`.
- Body: explain **why**, and what was rejected. Reference decision records by
  date when relevant. Wrap at 72 columns.
- English only.
- End with:

  ```text
  Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
  ```

## Never

- `--amend`, `rebase`, `reset --hard`, force-push, or any history rewrite.
- Pushing. That is the developer's call.
- Bundling unrelated concerns into one commit — propose splitting instead.

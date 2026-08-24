#!/usr/bin/env bash
# PostToolUse(Edit|Write): lint the markdown file that was just written.
# Exit 2 hands the rumdl report back to Claude so it fixes the file now
# instead of leaving the violation for `just checks`.
set -uo pipefail

payload=$(cat)
file=$(printf '%s' "$payload" | jq -r '.tool_input.file_path // empty')

[[ -z $file || $file != *.md ]] && exit 0
[[ -f $file ]] || exit 0
command -v rumdl >/dev/null 2>&1 || exit 0

# rumdl honours .rumdl.toml excludes when walking a directory, not when handed
# an explicit path — so repeat the ones that matter here.
case $file in
  */CHANGELOG.md | */LICENSE.md) exit 0 ;;
  */.azz/*) exit 0 ;;
esac

report=$(rumdl check "$file" 2>&1) && exit 0

printf 'rumdl reported markdown violations in %s:\n\n%s\n\n' "$file" "$report" >&2
printf 'Fix them now (`just rumdl-fmt` handles the formatting ones).\n' >&2
exit 2

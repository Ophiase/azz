#!/usr/bin/env bash
# Stop: lint the markdown this turn actually changed.
#
# The PostToolUse gate only sees Edit and Write. A file created through a Bash
# heredoc (`cat > file <<EOF`) never reaches it, so this catches what slipped
# past — including files nobody remembered to check.
#
# Loop guard: exit 2 makes Claude keep working, which fires this hook again.
# The report is hashed per session, so the same unfixed report never blocks
# twice in a row.
set -uo pipefail

payload=$(cat)
root=${CLAUDE_PROJECT_DIR:-$(pwd)}
command -v rumdl >/dev/null 2>&1 || exit 0
cd "$root" || exit 0

session=$(printf '%s' "$payload" | jq -r '.session_id // "unknown"')
state=".git/claude-stop-markdown-lint.${session}"

changed=$( { git diff --name-only HEAD -- '*.md'
             git ls-files --others --exclude-standard -- '*.md'; } 2>/dev/null \
           | sort -u \
           | grep -Ev '(^|/)(CHANGELOG|LICENSE)\.md$|(^|/)\.azz/' )

if [[ -z $changed ]]; then
  rm -f "$state"
  exit 0
fi

# shellcheck disable=SC2086
if report=$(rumdl check $changed 2>&1); then
  rm -f "$state"
  exit 0
fi

# Hash the findings only: rumdl's summary line carries an elapsed time that
# changes on every run and would defeat the guard.
hash=$(printf '%s\n' "$report" | grep -E '^[^ ]+:[0-9]+:[0-9]+:' | sha256sum | cut -d' ' -f1)
if [[ -f $state && $(cat "$state") == "$hash" ]]; then
  exit 0
fi
printf '%s' "$hash" > "$state"

printf 'Markdown you changed this turn does not pass rumdl:\n\n%s\n\n' "$report" >&2
printf 'Fix it before finishing (`just rumdl-fmt` handles the formatting ones).\n' >&2
exit 2

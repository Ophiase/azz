# Recipes meant for agent use. Documented in .claude/CLAUDE.md.
# `just *` is already allow-listed, so adding a recipe here needs no
# settings.json change.

# Markdown lint + lint + type-check, in one command with a real exit code.
[group("agent")]
@checks:
    rumdl check .
    uv run ruff check . --fix
    uv run ty check .

# VERSION, pyproject version and the latest CHANGELOG entry — these must agree.
[group("agent")]
@version:
    printf 'VERSION      '
    cat VERSION
    printf 'pyproject    '
    grep -m1 '^version' pyproject.toml
    printf 'changelog    '
    grep -m1 -- '- \*\*v' CHANGELOG.md

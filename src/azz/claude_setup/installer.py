from dataclasses import dataclass
from pathlib import Path
from typing import Final

from .docs_block import install_block, remove_block
from .git_ignore import (
    add_local_excludes,
    is_ignored,
    is_tracked,
    write_self_ignore,
)
from .profile import Profile
from .scope import InstallScope
from .settings_merge import install_settings

AGENTS_FILE_NAME: Final = "AGENTS.md"
CLAUDE_FILE_NAME: Final = "CLAUDE.md"


@dataclass(frozen=True, slots=True)
class InstallReport:
    profile: Profile
    scope: InstallScope
    skill_path: Path
    settings_path: Path
    agents_path: Path | None
    """Only written for a project install: AGENTS.md is a repository file and
    has no personal equivalent."""
    retired_claude_block: bool
    """An earlier azz version wrote its docs into CLAUDE.md. Re-installing
    removes that block so the content is not loaded twice."""
    self_ignore_path: Path | None = None
    """The `.gitignore` making the skill directory ignore itself."""
    excluded: tuple[str, ...] = ()
    """Patterns added to .git/info/exclude, for files in a directory azz does
    not own and that git does not already ignore."""
    already_tracked: tuple[str, ...] = ()
    """Paths git already tracks, which no ignore rule can hide."""


def install(
    profile: Profile,
    target: Path,
    scope: InstallScope = InstallScope.USER,
) -> InstallReport:
    skill_path = scope.skill_path(target)
    skill_path.parent.mkdir(parents=True, exist_ok=True)
    skill_path.write_text(profile.read_skill())

    settings_path = scope.settings_path(target)
    install_settings(settings_path, profile.read_permissions())

    agents_path = target / AGENTS_FILE_NAME
    if scope.shares_with_the_repository:
        install_block(agents_path, profile.read_agents_note())
    else:
        agents_path = None

    return InstallReport(
        profile=profile,
        scope=scope,
        skill_path=skill_path,
        settings_path=settings_path,
        agents_path=agents_path,
        retired_claude_block=remove_block(target / CLAUDE_FILE_NAME),
        self_ignore_path=_self_ignore(scope, skill_path),
        excluded=_exclude_settings(target, scope, settings_path),
        already_tracked=_already_tracked(target, scope, skill_path, settings_path),
    )


def _self_ignore(scope: InstallScope, skill_path: Path) -> Path | None:
    """azz owns the skill directory outright, so it can ignore itself."""
    if scope.shares_with_the_repository:
        return None
    return write_self_ignore(skill_path.parent)


def _exclude_settings(
    target: Path, scope: InstallScope, settings_path: Path
) -> tuple[str, ...]:
    """`settings.local.json` sits in `.claude/`, which belongs to the project,
    so it cannot be hidden by a directory-wide rule."""
    if scope.shares_with_the_repository or is_ignored(settings_path) is not False:
        return ()
    return add_local_excludes(target, (_pattern(target, settings_path),))


def _already_tracked(
    target: Path, scope: InstallScope, *paths: Path
) -> tuple[str, ...]:
    """Paths it is too late to hide: git ignores never apply to tracked files."""
    if scope.shares_with_the_repository:
        return ()
    return tuple(
        _pattern(target, path) for path in paths if is_tracked(target, path)
    )


def _pattern(target: Path, path: Path) -> str:
    return f"/{path.relative_to(target).as_posix()}"

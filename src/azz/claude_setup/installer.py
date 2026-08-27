from dataclasses import dataclass
from pathlib import Path
from typing import Final

from .docs_block import install_block, remove_block
from .git_ignore import add_local_excludes, is_tracked
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
    excluded: tuple[str, ...] = ()
    """Patterns added to .git/info/exclude by a personal install."""
    already_tracked: tuple[str, ...] = ()
    """Paths git already tracks, which no ignore rule can hide."""


def install(
    profile: Profile,
    target: Path,
    scope: InstallScope = InstallScope.PROJECT,
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

    personal = _keep_out_of_the_repository(target, scope, skill_path, settings_path)
    return InstallReport(
        profile=profile,
        scope=scope,
        skill_path=skill_path,
        settings_path=settings_path,
        agents_path=agents_path,
        retired_claude_block=remove_block(target / CLAUDE_FILE_NAME),
        excluded=personal[0],
        already_tracked=personal[1],
    )


def _keep_out_of_the_repository(
    target: Path, scope: InstallScope, *paths: Path
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Local git excludes for a personal install, and the paths too late to
    hide because git already tracks them."""
    if scope.shares_with_the_repository:
        return ((), ())
    patterns = tuple(f"/{path.relative_to(target).as_posix()}" for path in paths)
    tracked = tuple(
        pattern for pattern, path in zip(patterns, paths, strict=True)
        if is_tracked(target, path)
    )
    return add_local_excludes(target, patterns), tracked

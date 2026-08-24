from dataclasses import dataclass
from pathlib import Path
from typing import Final

from .docs_block import install_block, remove_block
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


def install(
    profile: Profile,
    target: Path,
    scope: InstallScope = InstallScope.PROJECT,
    home: Path | None = None,
) -> InstallReport:
    skill_path = scope.skill_path(target, home or Path.home())
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
    )

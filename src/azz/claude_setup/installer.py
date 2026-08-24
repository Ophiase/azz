from dataclasses import dataclass
from pathlib import Path
from typing import Final

from .docs_block import install_block, remove_block
from .profile import Profile
from .settings_merge import install_settings

SKILL_PATH_PARTS: Final = (".claude", "skills", "azz", "SKILL.md")
SETTINGS_PATH_PARTS: Final = (".claude", "settings.json")
AGENTS_FILE_NAME: Final = "AGENTS.md"
CLAUDE_FILE_NAME: Final = "CLAUDE.md"


@dataclass(frozen=True, slots=True)
class InstallReport:
    profile: Profile
    skill_path: Path
    agents_path: Path
    settings_path: Path
    retired_claude_block: bool
    """An earlier azz version wrote its docs into CLAUDE.md. Re-installing
    removes that block so the content is not loaded twice."""


def install(profile: Profile, target: Path) -> InstallReport:
    skill_path = target.joinpath(*SKILL_PATH_PARTS)
    skill_path.parent.mkdir(parents=True, exist_ok=True)
    skill_path.write_text(profile.read_skill())

    agents_path = target / AGENTS_FILE_NAME
    install_block(agents_path, profile.read_agents_note())

    settings_path = target.joinpath(*SETTINGS_PATH_PARTS)
    install_settings(settings_path, profile.read_permissions())

    return InstallReport(
        profile=profile,
        skill_path=skill_path,
        agents_path=agents_path,
        settings_path=settings_path,
        retired_claude_block=remove_block(target / CLAUDE_FILE_NAME),
    )

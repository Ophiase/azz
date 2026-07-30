from dataclasses import dataclass
from pathlib import Path

from .docs_block import install_docs
from .profile import Profile
from .settings_merge import install_settings

CLAUDE_MD_NAME = "CLAUDE.md"
SETTINGS_PATH_PARTS = (".claude", "settings.json")


@dataclass(frozen=True, slots=True)
class InstallReport:
    profile: Profile
    docs_path: Path
    settings_path: Path


def install(profile: Profile, target: Path) -> InstallReport:
    docs_path = target / CLAUDE_MD_NAME
    settings_path = target.joinpath(*SETTINGS_PATH_PARTS)
    install_docs(docs_path, profile.read_docs())
    install_settings(settings_path, profile.read_permissions())
    return InstallReport(profile, docs_path, settings_path)

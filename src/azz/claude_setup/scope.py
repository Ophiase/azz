from enum import StrEnum
from pathlib import Path
from typing import Final

SKILL_RELATIVE_PARTS: Final = (".claude", "skills", "azz", "SKILL.md")
PROJECT_SETTINGS_PARTS: Final = (".claude", "settings.json")
USER_SETTINGS_PARTS: Final = (".claude", "settings.local.json")


class InstallScope(StrEnum):
    PROJECT = "project"
    USER = "user"

    @property
    def summary(self) -> str:
        return SCOPE_SUMMARIES[self]

    @property
    def shares_with_the_repository(self) -> bool:
        return self is InstallScope.PROJECT

    def skill_path(self, target: Path, home: Path) -> Path:
        """Personal installs put the skill in the home directory, where it
        serves every project and never reaches a shared repository."""
        root = target if self.shares_with_the_repository else home
        return root.joinpath(*SKILL_RELATIVE_PARTS)

    def settings_path(self, target: Path) -> Path:
        parts = (
            PROJECT_SETTINGS_PARTS
            if self.shares_with_the_repository
            else USER_SETTINGS_PARTS
        )
        return target.joinpath(*parts)


SCOPE_SUMMARIES: Final = {
    InstallScope.PROJECT: (
        "Commit it: the skill, an AGENTS.md note and settings.json go into "
        "the repository, for everyone working on it."
    ),
    InstallScope.USER: (
        "Keep it to yourself: the skill goes to ~/.claude/skills and the "
        "permissions to settings.local.json. Nothing is added to the "
        "repository."
    ),
}

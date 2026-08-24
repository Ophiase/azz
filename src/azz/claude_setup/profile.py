import json
from collections.abc import Mapping, Sequence
from enum import StrEnum
from importlib.resources import files
from typing import Any, Final

PROFILES_DIRECTORY: Final = "profiles"
PERMISSION_KEYS: Final = ("allow", "deny")
COMMON_SKILL_BODY: Final = "skill-common.md"
AGENTS_NOTE: Final = "agents-note.md"


class Profile(StrEnum):
    PLANNING = "planning"
    STANDARD = "standard"

    @property
    def summary(self) -> str:
        return PROFILE_SUMMARIES[self]

    def read_skill(self) -> str:
        """The profile's own preamble followed by the shared workflow."""
        preamble = _read(f"skill-{self.value}.md").rstrip()
        return f"{preamble}\n\n{_read(COMMON_SKILL_BODY)}"

    def read_agents_note(self) -> str:
        return _read(AGENTS_NOTE)

    def read_permissions(self) -> Mapping[str, Sequence[str]]:
        document: dict[str, Any] = json.loads(_read(f"settings-{self.value}.json"))
        permissions = document.get("permissions", {})
        return {key: tuple(permissions.get(key, ())) for key in PERMISSION_KEYS}


PROFILE_SUMMARIES: Final = {
    Profile.PLANNING: (
        "Read the remote and author intent files. Every command that writes "
        "to Azure DevOps is denied — you run 'azz plan push' yourself."
    ),
    Profile.STANDARD: (
        "Everything in planning, plus the imperative write commands "
        "(create, state, close, attach, set_timebox), each behind a prompt."
    ),
}


def _read(file_name: str) -> str:
    resource = files(__package__).joinpath(PROFILES_DIRECTORY, file_name)
    return resource.read_text(encoding="utf-8")

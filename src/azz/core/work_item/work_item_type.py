from enum import StrEnum
from typing import Any, Final

DESCRIPTION_FIELD: Final = "System.Description"
REPRO_STEPS_FIELD: Final = "Microsoft.VSTS.TCM.ReproSteps"


class WorkItemType(StrEnum):
    TASK = "Task"
    USER_STORY = "User Story"
    BUG = "Bug"
    EPIC = "Epic"
    DEFAULT = "Default"
    ISSUE = "Issue"
    FEATURE = "Feature"

    @property
    def body_field(self) -> str:
        """The field a work item form shows as its body: a Bug's form hides
        the Description and shows Repro Steps instead."""
        return REPRO_STEPS_FIELD if self is WorkItemType.BUG else DESCRIPTION_FIELD

    @property
    def short_label(self) -> str:
        """At most four characters, for a narrow table column."""
        return SHORT_LABELS.get(self, self.value[:4])

    @classmethod
    def type_from_fields(cls, data: dict[str, Any]) -> WorkItemType:
        type_str = data.get("fields", {}).get("System.WorkItemType", "")
        return (
            WorkItemType(type_str)
            if type_str in WorkItemType.__members__.values()
            else WorkItemType.DEFAULT
        )

    @classmethod
    def from_user_input(cls, type_str: str) -> WorkItemType:
        """
        Convert user input to a WorkItemType.
        Accepts full names or first letters (case-insensitive).
        """
        if not type_str:
            return cls.DEFAULT

        type_str = type_str.strip().lower()
        match type_str[0]:
            case "t":
                return cls.TASK
            case "u":
                return cls.USER_STORY
            case "b":
                return cls.BUG
            case "e":
                return cls.EPIC
            case "i":
                return cls.ISSUE
            case "f":
                return cls.FEATURE
            case _:
                raise ValueError(f"Unknown work item type '{type_str}'")


SHORT_LABELS: Final = {
    WorkItemType.USER_STORY: "US",
    WorkItemType.FEATURE: "Feat",
    WorkItemType.ISSUE: "Iss",
    WorkItemType.DEFAULT: "—",
}

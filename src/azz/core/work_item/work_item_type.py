from enum import StrEnum
from typing import Any


class WorkItemType(StrEnum):
    TASK = "Task"
    USER_STORY = "User Story"
    BUG = "Bug"
    EPIC = "Epic"
    DEFAULT = "Default"
    ISSUE = "Issue"
    FEATURE = "Feature"

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

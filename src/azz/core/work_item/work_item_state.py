from enum import StrEnum
from typing import Final


class WorkItemState(StrEnum):
    ACTIVE = "Active"
    NEW = "New"
    DESIGN = "Design"
    RESOLVED = "Resolved"
    CLOSED = "Closed"
    UNKNOWN = "Unknown"

    @property
    def is_known(self) -> bool:
        return self != WorkItemState.UNKNOWN

    @classmethod
    def from_str(cls, state: str | None) -> WorkItemState:
        if state is None:
            return cls.UNKNOWN
        try:
            return cls(state)
        except ValueError:
            return cls.UNKNOWN

    @classmethod
    def from_user_input(cls, state: str) -> WorkItemState:
        """
        Convert user input to a WorkItemState.
        Accepts full names or first letters (case-insensitive).
        """
        if not state:
            return cls.UNKNOWN

        state = state.strip().lower()
        match state[0]:
            case "a":
                return cls.ACTIVE
            case "n":
                return cls.NEW
            case "d":
                return cls.DESIGN
            case "r":
                return cls.RESOLVED
            case "c":
                return cls.CLOSED
            case _:
                raise ValueError(f"Unknown state '{state}'")


STATE_COLORS: Final = {
    WorkItemState.ACTIVE.value: "green",
    WorkItemState.NEW.value: "yellow",
    WorkItemState.RESOLVED.value: "cyan",
    WorkItemState.CLOSED.value: "grey50",
}

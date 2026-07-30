from enum import StrEnum
from typing import Final


class ChangeType(StrEnum):
    CREATE = "create"
    UPDATE = "update"
    NOOP = "noop"
    GONE = "gone"

    @property
    def is_applicable(self) -> bool:
        return self in {ChangeType.CREATE, ChangeType.UPDATE}

    @property
    def label(self) -> str:
        return CHANGE_TYPE_LABELS[self]

    @property
    def style(self) -> str:
        return CHANGE_TYPE_COLORS[self]


CHANGE_TYPE_LABELS: Final = {
    ChangeType.CREATE: "NEW",
    ChangeType.UPDATE: "DRIFT",
    ChangeType.NOOP: "NOOP",
    ChangeType.GONE: "GONE",
}

CHANGE_TYPE_COLORS: Final = {
    ChangeType.CREATE: "green",
    ChangeType.UPDATE: "yellow",
    ChangeType.NOOP: "grey50",
    ChangeType.GONE: "red",
}

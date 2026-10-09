from enum import IntEnum
from typing import Any, Final

PRIORITY_FIELD: Final = "Microsoft.VSTS.Common.Priority"


class Priority(IntEnum):
    """Azure DevOps priority: 1 is the most urgent, 4 the least."""

    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4

    def shifted(self, step: int) -> Priority:
        """A negative step is more urgent; the ends of the scale hold."""
        return Priority(min(max(self + step, Priority.CRITICAL), Priority.LOW))

    @classmethod
    def of_fields(cls, fields: dict[str, Any]) -> Priority | None:
        try:
            return cls(fields.get(PRIORITY_FIELD))
        except ValueError:
            return None

    @classmethod
    def or_lowest(cls, priority: Priority | None) -> Priority:
        """An item without a priority ranks below every item with one."""
        return priority if priority is not None else cls.LOW

from enum import StrEnum

from azz.core.work_item.priority import Priority


class PriorityTint(StrEnum):
    """The `WorkItemTable` component class that tints a row by its priority."""

    CRITICAL = "work-table--critical"
    MINOR = "work-table--minor"

    @classmethod
    def of(cls, priority: Priority | None) -> PriorityTint | None:
        """Critical stands out, anything below High fades; the rest is plain."""
        if priority is Priority.CRITICAL:
            return cls.CRITICAL
        if priority is not None and priority > Priority.HIGH:
            return cls.MINOR
        return None

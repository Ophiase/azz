from enum import StrEnum
from typing import Final

from azz.core.work_item.priority import Priority
from azz.core.work_item.work_item import WorkItem
from azz.core.work_item.work_item_state import WorkItemState

_DONE_STATES: Final = frozenset({WorkItemState.RESOLVED, WorkItemState.CLOSED})


class RowTint(StrEnum):
    """The `WorkItemTable` component class that tints a row."""

    CRITICAL = "work-table--critical"
    MINOR = "work-table--minor"
    DONE = "work-table--done"

    @classmethod
    def of(cls, priority: Priority | None) -> RowTint | None:
        """Critical stands out, anything below High fades; the rest is plain."""
        if priority is Priority.CRITICAL:
            return cls.CRITICAL
        if priority is not None and priority > Priority.HIGH:
            return cls.MINOR
        return None

    @classmethod
    def of_item(cls, item: WorkItem) -> RowTint | None:
        """A done item fades out, whatever its priority."""
        if item.state in _DONE_STATES:
            return cls.DONE
        return cls.of(item.priority)

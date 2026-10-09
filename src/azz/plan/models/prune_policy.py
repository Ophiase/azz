from dataclasses import dataclass

from azz.core.iteration_path import IterationPath
from azz.core.work_item import WorkItem, WorkItemState
from azz.core.work_item.work_item import Username


@dataclass(frozen=True, slots=True)
class PrunePolicy:
    """Which in-sync items are no longer being worked on. Closed always is;
    each option set here widens the net."""

    current_timebox: IterationPath | None = None
    """Set: an item outside this timebox is no longer worked on."""
    owner: Username | None = None
    """Set: an item assigned to anyone else, or to nobody, is not mine."""

    def is_inactive(self, work_item: WorkItem) -> bool:
        return (
            work_item.state == WorkItemState.CLOSED
            or self._outside_timebox(work_item)
            or self._not_mine(work_item)
        )

    def _outside_timebox(self, work_item: WorkItem) -> bool:
        if self.current_timebox is None:
            return False
        iteration_path = work_item.iteration_path
        if iteration_path is None:
            return True
        return iteration_path.value != self.current_timebox.value

    def _not_mine(self, work_item: WorkItem) -> bool:
        return self.owner is not None and work_item.assigned_to != self.owner

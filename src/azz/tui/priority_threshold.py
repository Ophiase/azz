from dataclasses import dataclass

from azz.core.work_item.priority import Priority
from azz.core.work_item.work_item import WorkItem


@dataclass(frozen=True, slots=True)
class PriorityThreshold:
    """Show only the items at least as urgent as `ceiling`; none shows all."""

    ceiling: Priority | None = None

    def admits(self, item: WorkItem) -> bool:
        if self.ceiling is None:
            return True
        return item.priority is not None and item.priority <= self.ceiling

    @property
    def label(self) -> str:
        return "all" if self.ceiling is None else f"≤{int(self.ceiling)}"

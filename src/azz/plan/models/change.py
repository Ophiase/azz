from dataclasses import dataclass, field

from azz.core.work_item import WorkItem

from .change_type import ChangeType
from .field_diff import FieldDiff
from .local_item import LocalItem


@dataclass(frozen=True, slots=True)
class Change:
    local_item: LocalItem
    change_type: ChangeType
    field_diffs: tuple[FieldDiff, ...] = field(default=())
    remote_item: WorkItem | None = None
    remote_moved: bool = False
    """The remote changed after the timestamp recorded locally — someone
    else, or another tool, edited the item since the last fetch."""

    @property
    def changed_field_names(self) -> frozenset[str]:
        return frozenset(diff.field_name for diff in self.field_diffs)

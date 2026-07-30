from dataclasses import dataclass, field

from azz.core.work_item import WorkItem

from .field_diff import FieldDiff
from .local_item import LocalItem
from .sync_state import SyncState


@dataclass(frozen=True, slots=True)
class SyncEntry:
    """One intent file, placed against the cache."""

    local_item: LocalItem
    state: SyncState
    field_diffs: tuple[FieldDiff, ...] = field(default=())
    base_item: WorkItem | None = None
    fetched_item: WorkItem | None = None
    degraded: bool = False
    """A snapshot was missing, so the answer is the two-way one `azz plan
    status` gave before the cache existed."""

    @property
    def changed_field_names(self) -> frozenset[str]:
        return frozenset(diff.field_name for diff in self.field_diffs)

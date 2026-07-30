from dataclasses import dataclass, field

from azz.core.work_item import WorkItem

from .sync_entry import SyncEntry
from .sync_state import SyncState


@dataclass(frozen=True, slots=True)
class SyncReport:
    """Every intent file placed against the cache, plus what the cache holds
    that the working tree has never seen."""

    entries: tuple[SyncEntry, ...]
    incoming: tuple[WorkItem, ...] = field(default=())
    """Cached items with no intent file and no merge base — never pulled."""

    def of_state(self, state: SyncState) -> tuple[SyncEntry, ...]:
        return tuple(entry for entry in self.entries if entry.state is state)

    @property
    def conflicts(self) -> tuple[SyncEntry, ...]:
        return self.of_state(SyncState.CONFLICT)

    @property
    def degraded(self) -> tuple[SyncEntry, ...]:
        return tuple(entry for entry in self.entries if entry.degraded)

    @property
    def has_cache(self) -> bool:
        return bool(self.incoming) or any(
            entry.base_item is not None or entry.fetched_item is not None
            for entry in self.entries
        )

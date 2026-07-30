from collections.abc import Sequence
from pathlib import Path
from typing import Final

from azz.core.work_item import WorkItem

from .comparison import field_diffs
from .models import LocalItem, SyncEntry, SyncReport, SyncState
from .snapshot_diff import remote_advanced
from .snapshots import Snapshots

DECISION_TABLE: Final = {
    (False, False): SyncState.IN_SYNC,
    (False, True): SyncState.REMOTE_ONLY,
    (True, False): SyncState.LOCAL_ONLY,
    (True, True): SyncState.CONFLICT,
}
"""(tasks moved, remote moved) → meaning. The whole point of the merge base."""


class SyncInspector:
    """
    Places `.azz/tasks/` against `.azz/cache/` — offline, no engine, no `az`.

    A file is compared to the merge base and the merge base to the fetched
    snapshot, which separates "I edited this" from "someone else did". When a
    snapshot is missing the verdict falls back to the two-way one and is marked
    degraded, so upgrading mid-flight costs a notice rather than an error.
    """

    def __init__(self, plan_root: Path) -> None:
        self._snapshots = Snapshots.for_plan(plan_root)

    def inspect(self, local_items: Sequence[LocalItem]) -> SyncReport:
        entries = tuple(self._entry(local_item) for local_item in local_items)
        return SyncReport(entries, self._incoming(entries))

    def _entry(self, local_item: LocalItem) -> SyncEntry:
        item_id = local_item.item_id
        if item_id is None:
            return SyncEntry(local_item, SyncState.NEW)
        base = self._snapshots.base.read_item(item_id)
        fetched = self._snapshots.fetched.read_item(item_id)
        if base is not None and fetched is not None:
            return _three_way(local_item, base, fetched)
        if fetched is not None:
            return _two_way(local_item, fetched, is_base=False)
        if base is not None:
            return _two_way(local_item, base, is_base=True)
        return SyncEntry(local_item, SyncState.UNKNOWN, degraded=True)

    def _incoming(self, entries: Sequence[SyncEntry]) -> tuple[WorkItem, ...]:
        """Cached items the working tree never held. A file the user deleted
        keeps its merge base, so pruning is not undone by the next pull."""
        tracked = {entry.local_item.item_id for entry in entries}
        never_pulled = (
            self._snapshots.fetched.item_ids()
            - self._snapshots.base.item_ids()
            - tracked
        )
        items = (self._snapshots.fetched.read_item(one) for one in sorted(never_pulled))
        return tuple(item for item in items if item is not None)


def _three_way(
    local_item: LocalItem, base: WorkItem, fetched: WorkItem
) -> SyncEntry:
    diffs = field_diffs(local_item, base)
    state = DECISION_TABLE[bool(diffs), remote_advanced(base, fetched)]
    return SyncEntry(local_item, state, diffs, base, fetched)


def _two_way(local_item: LocalItem, known: WorkItem, is_base: bool) -> SyncEntry:
    """One snapshot only: we can see that the file differs, not which side
    moved — exactly what `status` reported before the cache existed."""
    diffs = field_diffs(local_item, known)
    state = SyncState.LOCAL_ONLY if diffs else SyncState.IN_SYNC
    return SyncEntry(
        local_item,
        state,
        diffs,
        base_item=known if is_base else None,
        fetched_item=None if is_base else known,
        degraded=True,
    )

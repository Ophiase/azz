from collections.abc import Sequence
from pathlib import Path
from typing import Final

from azz.core.timebox import Iteration
from azz.core.work_item import WorkItem

from .comparison import field_diffs
from .discovery import cache_directory, tasks_directory
from .fetch_clock import FetchClock
from .freshness import remote_is_ahead
from .models import FetchOutcome, FetchStatus, LocalItem
from .serializer import render_intent_file
from .slug import intent_file_name
from .snapshots import Snapshots

REMOTE_AHEAD_REASON: Final = "remote is ahead — local file replaced"
LOCAL_CHANGES_REASON: Final = "local changes — rerun with --force to overwrite"


class Fetcher:
    """
    Mirrors remote work items into `.azz/tasks/` and records them in the cache.

    Files are matched by `item_id`, not by filename, so a file keeps its name
    after the remote title changes. Every fetched item is written to the
    fetched snapshot; the merge base only advances for files the fetch actually
    brought level with the remote.
    """

    def __init__(self, plan_root: Path, local_items: Sequence[LocalItem]) -> None:
        self._directory = tasks_directory(plan_root)
        self._snapshots = Snapshots.for_plan(plan_root)
        self._clock = FetchClock(cache_directory(plan_root))
        self._by_item_id = {
            item.item_id: item for item in local_items if item.item_id is not None
        }

    def fetch(self, work_item: WorkItem, force: bool = False) -> FetchOutcome:
        outcome = self._mirror(work_item, force)
        self._record(work_item, outcome.status)
        return outcome

    def record_timeboxes(self, timeboxes: Sequence[Iteration]) -> None:
        self._snapshots.record_timeboxes(timeboxes)

    def record_fetch_time(self) -> None:
        self._clock.stamp()

    def _record(self, work_item: WorkItem, status: FetchStatus) -> None:
        if status is FetchStatus.SKIPPED:
            self._snapshots.record_fetched(work_item)
        else:
            self._snapshots.record_synced(work_item)

    def _mirror(self, work_item: WorkItem, force: bool) -> FetchOutcome:
        existing = self._by_item_id.get(work_item.id)
        if existing is None:
            path = self._directory / intent_file_name(work_item)
            return self._write(work_item, path, FetchStatus.CREATED)
        if force or not field_diffs(existing, work_item):
            return self._write(work_item, existing.path, FetchStatus.REFRESHED)
        if remote_is_ahead(existing, work_item):
            return self._write(
                work_item, existing.path, FetchStatus.REFRESHED, REMOTE_AHEAD_REASON
            )
        return FetchOutcome(
            work_item, existing.path, FetchStatus.SKIPPED, LOCAL_CHANGES_REASON
        )

    def _write(
        self,
        work_item: WorkItem,
        path: Path,
        status: FetchStatus,
        reason: str = "",
    ) -> FetchOutcome:
        self._directory.mkdir(parents=True, exist_ok=True)
        path.write_text(render_intent_file(work_item))
        return FetchOutcome(work_item, path, status, reason)

from collections.abc import Sequence
from pathlib import Path
from typing import Final

from azz.core.work_item import WorkItem

from .comparison import field_diffs
from .discovery import tasks_directory
from .freshness import remote_is_ahead
from .models import FetchOutcome, FetchStatus, LocalItem
from .serializer import render_intent_file
from .slug import intent_file_name

REMOTE_AHEAD_REASON: Final = "remote is ahead — local file replaced"
LOCAL_CHANGES_REASON: Final = "local changes — rerun with --force to overwrite"


class Fetcher:
    """
    Mirrors remote work items into `.azz/tasks/`.

    Files are matched by `item_id`, not by filename, so a file keeps its name
    after the remote title changes.
    """

    def __init__(self, plan_root: Path, local_items: Sequence[LocalItem]) -> None:
        self._directory = tasks_directory(plan_root)
        self._by_item_id = {
            item.item_id: item for item in local_items if item.item_id is not None
        }

    def fetch(self, work_item: WorkItem, force: bool = False) -> FetchOutcome:
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

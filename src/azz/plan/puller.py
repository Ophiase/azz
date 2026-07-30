from pathlib import Path
from typing import Final

from azz.core.work_item import WorkItem

from .discovery import tasks_directory
from .models import LocalItem, PullOutcome, PullStatus, SyncEntry, SyncReport, SyncState
from .serializer import render_intent_file
from .slug import intent_file_name
from .snapshots import Snapshots

CONFLICT_REASON: Final = "both sides changed — resolve by hand, or --force"
NO_BASE_REASON: Final = "no merge base — --force takes the remote"
NOT_CACHED_REASON: Final = "not in the cache — run azz plan fetch"
FORCED_REASON: Final = "local changes overwritten"
BASE_ADOPTED_REASON: Final = "merge base recorded"


class Puller:
    """
    Writes `.azz/cache/` into `.azz/tasks/` — a fast-forward, never a merge.

    A file whose local side is untouched is replaced by the fetched state and
    its merge base advances with it. A file where both sides moved is refused
    and listed: there is no automatic text merge, the human resolves it.
    """

    def __init__(self, plan_root: Path) -> None:
        self._directory = tasks_directory(plan_root)
        self._snapshots = Snapshots.for_plan(plan_root)

    def pull(self, report: SyncReport, force: bool = False) -> tuple[PullOutcome, ...]:
        created = tuple(self._create(work_item) for work_item in report.incoming)
        visited = tuple(self._visit(entry, force) for entry in report.entries)
        return created + visited

    def _visit(self, entry: SyncEntry, force: bool) -> PullOutcome:
        match entry.state:
            case SyncState.REMOTE_ONLY:
                return self._fast_forward(entry)
            case SyncState.CONFLICT:
                return self._resolve(entry, force)
            case SyncState.LOCAL_ONLY if entry.degraded:
                return self._resolve(entry, force, NO_BASE_REASON)
            case SyncState.IN_SYNC if entry.degraded:
                return self._adopt(entry)
            case SyncState.UNKNOWN:
                return _outcome(entry, PullStatus.SKIPPED, NOT_CACHED_REASON)
            case _:
                return _outcome(entry, PullStatus.UP_TO_DATE)

    def _fast_forward(self, entry: SyncEntry, reason: str = "") -> PullOutcome:
        fetched = entry.fetched_item
        if fetched is None:
            return _outcome(entry, PullStatus.SKIPPED, NOT_CACHED_REASON)
        self._write(entry.local_item.path, fetched)
        return _outcome(entry, PullStatus.FAST_FORWARDED, reason)

    def _resolve(
        self, entry: SyncEntry, force: bool, refusal: str = CONFLICT_REASON
    ) -> PullOutcome:
        if not force:
            status = (
                PullStatus.REFUSED
                if entry.state is SyncState.CONFLICT
                else PullStatus.SKIPPED
            )
            return _outcome(entry, status, refusal)
        return self._fast_forward(entry, FORCED_REASON)

    def _adopt(self, entry: SyncEntry) -> PullOutcome:
        """The file already matches the fetched state — record the merge base
        so the next comparison is a real three-way one."""
        fetched = entry.fetched_item
        if fetched is None:
            return _outcome(entry, PullStatus.UP_TO_DATE)
        self._snapshots.record_base(fetched)
        return _outcome(entry, PullStatus.UP_TO_DATE, BASE_ADOPTED_REASON)

    def _create(self, work_item: WorkItem) -> PullOutcome:
        path = self._directory / intent_file_name(work_item)
        self._write(path, work_item)
        return PullOutcome(path, work_item.id, PullStatus.CREATED)

    def _write(self, path: Path, work_item: WorkItem) -> None:
        self._directory.mkdir(parents=True, exist_ok=True)
        path.write_text(render_intent_file(work_item))
        self._snapshots.record_base(work_item)


def _outcome(entry: SyncEntry, status: PullStatus, reason: str = "") -> PullOutcome:
    local_item: LocalItem = entry.local_item
    return PullOutcome(local_item.path, local_item.item_id, status, reason)

from collections.abc import Sequence
from pathlib import Path

from azz.core.timebox import Iteration
from azz.core.work_item import WorkItem

from .discovery import cache_directory
from .fetch_clock import FetchClock
from .models import FetchOutcome, FetchStatus
from .snapshot_diff import remote_advanced
from .snapshots import Snapshots


class Fetcher:
    """
    Records what the remote said into `.azz/cache/`.

    It never touches `.azz/tasks/` — `azz plan pull` does that, the way
    `git fetch` leaves the working tree to `git merge`. Keeping the two apart
    is what gives every later comparison a merge base instead of a guess.
    """

    def __init__(self, plan_root: Path) -> None:
        self._snapshots = Snapshots.for_plan(plan_root)
        self._clock = FetchClock(cache_directory(plan_root))

    def fetch(self, work_item: WorkItem) -> FetchOutcome:
        previous = self._snapshots.fetched.read_item(work_item.id)
        self._snapshots.record_fetched(work_item)
        return FetchOutcome(work_item, _status(previous, work_item))

    def record_timeboxes(self, timeboxes: Sequence[Iteration]) -> None:
        self._snapshots.record_timeboxes(timeboxes)

    def record_fetch_time(self) -> None:
        self._clock.stamp()


def _status(previous: WorkItem | None, fetched: WorkItem) -> FetchStatus:
    if previous is None:
        return FetchStatus.CREATED
    if remote_advanced(previous, fetched):
        return FetchStatus.REFRESHED
    return FetchStatus.UNCHANGED

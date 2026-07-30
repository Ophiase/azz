from dataclasses import dataclass

from azz.core.work_item import WorkItem

from .fetch_status import FetchStatus


@dataclass(frozen=True, slots=True)
class FetchOutcome:
    """One work item as the cache recorded it. There is no path: a fetch writes
    the cache, not the working tree."""

    work_item: WorkItem
    status: FetchStatus
    reason: str = ""

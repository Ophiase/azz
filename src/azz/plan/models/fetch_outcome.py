from dataclasses import dataclass
from pathlib import Path

from azz.core.work_item import WorkItem

from .fetch_status import FetchStatus


@dataclass(frozen=True, slots=True)
class FetchOutcome:
    work_item: WorkItem
    path: Path
    status: FetchStatus
    reason: str = ""

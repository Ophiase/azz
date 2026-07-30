from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Self

from azz.cache import CacheStore, ItemPayload
from azz.core.timebox import Iteration
from azz.core.work_item import WorkItem

from .discovery import cache_directory, fetched_cache_directory


@dataclass(frozen=True, slots=True)
class Snapshots:
    """
    `.azz/cache/` as two generations of our knowledge of the remote.

    `base` is the state each intent file was last synced from — the merge base.
    `fetched` is the newest state the remote reported. Comparing a file to
    `base` says whether the human moved it; comparing `base` to `fetched` says
    whether the remote moved. Two comparisons, no guessing.
    """

    base: CacheStore
    fetched: CacheStore

    @classmethod
    def for_plan(cls, plan_root: Path) -> Self:
        return cls(
            base=CacheStore(cache_directory(plan_root)),
            fetched=CacheStore(fetched_cache_directory(plan_root)),
        )

    def record_fetched(self, work_item: WorkItem) -> None:
        self.fetched.write_item(ItemPayload.from_work_item(work_item))

    def record_base(self, work_item: WorkItem) -> None:
        self.base.write_item(ItemPayload.from_work_item(work_item))

    def record_synced(self, work_item: WorkItem) -> None:
        """Both generations at once — the working tree now agrees with this."""
        self.record_fetched(work_item)
        self.record_base(work_item)

    def record_timeboxes(self, timeboxes: Sequence[Iteration]) -> None:
        """Timeboxes have no working-tree counterpart, so one copy is enough."""
        self.base.write_timeboxes(
            tuple(_timebox_fields(timebox) for timebox in timeboxes)
        )


def _timebox_fields(timebox: Iteration) -> dict[str, Any]:
    """The shape `Iteration.from_fields` reads back."""
    return {
        "id": timebox.id,
        "name": timebox.name,
        "path": timebox.path.value,
        "attributes": {
            "startDate": _timestamp(timebox.start_date),
            "finishDate": _timestamp(timebox.finish_date),
        },
    }


def _timestamp(moment: datetime | None) -> str | None:
    return moment.isoformat() if moment is not None else None

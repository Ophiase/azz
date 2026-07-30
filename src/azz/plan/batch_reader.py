from collections.abc import Sequence
from typing import Protocol, runtime_checkable

from azz.core.work_item import WorkItem


@runtime_checkable
class BatchWorkItemReader(Protocol):
    """
    A data source that can resolve many work item ids in one round trip.

    Kept separate from `WorkItemBackend` and checked at runtime so a backend
    without the capability still works — it just costs one call per id.
    """

    def get_work_items_by_id(
        self, work_item_ids: Sequence[int]
    ) -> tuple[WorkItem, ...]: ...

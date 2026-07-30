from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Self

from azz.core.work_item.work_item import WorkItem
from azz.plan.discovery import find_plan_root
from azz.plan.tracking import TrackingStatus, tracking_statuses


@dataclass(frozen=True, slots=True)
class PlanState:
    """
    How the local plan in `.azz/tasks` relates to the work items on screen.

    Built once per item-list refresh, never per row: `load` costs one directory
    scan plus one small cache read per tracked item. Any failure degrades to an
    empty mapping, so a broken `.azz` shows a blank gutter instead of taking
    the table down.
    """

    statuses: Mapping[int, TrackingStatus] = field(default_factory=dict)

    @classmethod
    def load(cls, remote_items: Sequence[WorkItem]) -> Self:
        try:
            return cls(tracking_statuses(find_plan_root(), remote_items))
        except Exception:
            return cls()

    @property
    def tracked_count(self) -> int:
        return len(self.statuses)

    def status(self, work_item_id: int) -> TrackingStatus:
        return self.statuses.get(work_item_id, TrackingStatus.UNTRACKED)

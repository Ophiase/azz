from typing import Protocol

from azz.core.timebox import Iteration
from azz.core.work_item import WorkItem, WorkItemState
from azz.core.work_item.work_item_type import WorkItemType


class WorkItemBackend(Protocol):
    """
    Everything the CLI, the TUI and the plan engine need from a data source.

    `Engine` (Azure DevOps via `az`) satisfies this structurally. So does a
    backend reading and writing a local cache, which is what makes offline and
    demo modes possible without any caller knowing the difference.

    The 2026-07-24 plan-engine record deferred this protocol until a second
    backend actually existed. It now does.
    """

    def list_work_items(
        self,
        assigned_to: str = "@me",
        states: frozenset[WorkItemState] | None = None,
        show_others: bool = False,
        project_filter: bool = True,
        current_timebox_only: bool = False,
    ) -> tuple[WorkItem, ...]: ...

    def get_workitem(self, work_item_id: int) -> WorkItem: ...

    def update_workitem(self, work_item: WorkItem) -> None: ...

    def update_work_item_state(
        self, work_item_id: int, new_state: WorkItemState
    ) -> None: ...

    def update_work_item_title(self, work_item_id: int, new_title: str) -> None: ...

    def create_work_item_helper(
        self,
        name: str,
        description: str | None = None,
        project: str | None = None,
        item_type: WorkItemType = WorkItemType.TASK,
    ) -> WorkItem: ...

    def delete_workitem_helper(self, work_item_id: int) -> None: ...

    def link_parent(self, child_id: int, parent_id: int) -> None: ...

    def list_timeboxes(self, project: str | None = None) -> tuple[Iteration, ...]: ...

    def get_current_timebox(self, project: str | None = None) -> Iteration: ...

    def set_timebox(self, task_id: int, timebox: Iteration) -> None: ...

    def edit_work_item(self, work_item_id: int, edit_title: bool) -> WorkItem: ...

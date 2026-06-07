from copy import replace
from logging import getLogger

from azz.core.iteration_path import IterationPath
from azz.core.timebox import Iteration
from azz.core.wiql import build_wiql_query
from azz.core.work_item.work_item import work_item_factory
from azz.core.work_item.work_item_filter import IterationPathFilter
from azz.core.work_item.work_item_type import WorkItemType

from .editor import edit_work_item_in_editor
from .engine_config import EngineConfig
from .runner import run_az_command_sync, run_az_void_sync
from .work_item import ProjectNameFilter, WorkItem, WorkItemFilter, WorkItemState

logger = getLogger(__name__)


class Engine:
    def __init__(self, config: EngineConfig):
        self.config = config

    def _fetch_tasks_from_project(
        self,
        project: str,
        assigned_to: str | None = None,
        states: frozenset[WorkItemState] | None = None,
    ) -> tuple[WorkItem, ...]:
        if states is None:
            states = frozenset({WorkItemState.ACTIVE, WorkItemState.NEW})
        wiql = build_wiql_query(assigned_to, states)

        result = run_az_command_sync(
            "boards",
            "query",
            f"--project={project}",
            f"--wiql={wiql}",
            "-o",
            "json",
        )

        if not isinstance(result, list):
            raise RuntimeError(f"Unexpected result format from az command: {result}")

        return tuple(work_item_factory(item) for item in result)

    def list_work_items(
        self,
        assigned_to: str = "@me",
        states: frozenset[WorkItemState] | None = None,
        show_others: bool = False,
        project_filter: bool = True,
        current_timebox_only: bool = False,
    ) -> tuple[WorkItem, ...]:
        def project_tasks(project: str) -> tuple[WorkItem, ...]:
            query_assigned_to = None if show_others else assigned_to
            return self._fetch_tasks_from_project(project, query_assigned_to, states)

        tasks = project_tasks(self.config.management_project)
        filters = []
        if project_filter and self.config.prepend_project_name:
            filters.append(ProjectNameFilter(self.config.projects))
        if current_timebox_only:
            current_timebox = self.get_current_timebox()
            filters.append(IterationPathFilter(current_timebox.path))
        return WorkItemFilter.apply_filters(tasks, *filters)

    def get_workitem(self, work_item_id: int) -> WorkItem:
        result = run_az_command_sync(
            "boards", "work-item", "show", f"--id={work_item_id}", "-o", "json"
        )
        if not isinstance(result, dict):
            raise RuntimeError(f"Unexpected result format from az command: {result}")

        return work_item_factory(result)

    def update_workitem(self, work_item: WorkItem) -> None:
        run_az_command_sync(
            "boards",
            "work-item",
            "update",
            f"--id={work_item.id}",
            "--fields",
            f"System.Title={work_item.name}",
            f"System.Description={work_item.description or ''}",
        )

    def update_work_item_state(
        self, work_item_id: int, new_state: WorkItemState
    ) -> None:
        run_az_command_sync(
            "boards",
            "work-item",
            "update",
            f"--id={work_item_id}",
            "--fields",
            f"System.State={new_state.value}",
        )

    def list_timeboxes(self, project: str | None = None) -> tuple[Iteration, ...]:
        if project is None:
            project = self.config.management_project

        result = run_az_command_sync(
            "boards",
            "iteration",
            "project",
            "list",
            f"--project={project}",
            "-o",
            "json",
        )

        if not isinstance(result, dict):
            raise RuntimeError(f"Unexpected result format from az command: {result}")
        result: list = result.get("children", [])

        return tuple(Iteration.from_fields(item) for item in result)

    def get_current_timebox(self, project: str | None = None) -> Iteration:
        timeboxes = self.list_timeboxes(project)
        for timebox in timeboxes:
            if timebox.is_current:
                return timebox
        raise RuntimeError("Current timebox not found")

    def set_timebox(self, task_id: int, timebox: Iteration) -> None:
        return self.set_timebox_from_path(task_id, timebox.path)

    def set_timebox_from_path(self, task_id: int, timebox_path: IterationPath) -> None:
        if not timebox_path.normalized:
            raise ValueError("Invalid timebox path")
        run_az_command_sync(
            "boards",
            "work-item",
            "update",
            f"--id={task_id}",
            "--fields",
            f"System.IterationPath={timebox_path.value}",
        )

    def link_parent(
        self,
        child_id: int,
        parent_id: int,
    ) -> None:
        run_az_void_sync(
            "boards",
            "work-item",
            "relation",
            "add",
            "--id",
            str(child_id),
            "--relation-type",
            "parent",
            "--target-id",
            str(parent_id),
        )

    def create_work_item_helper(
        self,
        name: str,
        description: str | None = None,
        project: str | None = None,
        item_type: WorkItemType = WorkItemType.TASK,
    ) -> WorkItem:
        if project is None:
            project = self.config.default_project
        management_project = self.config.management_project

        timebox = self.get_current_timebox(management_project)
        if self.config.prepend_project_name:
            task_name = f"[{project}] - {name}"
        else:
            task_name = name

        cmd = [
            "boards",
            "work-item",
            "create",
            "--type",
            item_type.value,
            "--title",
            task_name,
            "--assigned-to",
            "me",
            "--project",
            management_project,
        ]

        if description:
            cmd.extend([
                "--description",
                description,
            ])

        result = run_az_command_sync(*cmd)

        if not isinstance(result, dict):
            raise RuntimeError(f"Unexpected result format from az command: {result}")

        item = WorkItem.from_fields(result)
        if timebox.path:
            self.set_timebox(item.id, timebox)
        item = replace(item, item_type=item_type, iteration_path=timebox.path)
        return item

    def delete_workitem_helper(self, work_item_id: int) -> None:
        cmd = [
            "boards",
            "work-item",
            "delete",
            "--id",
            str(work_item_id),
            "--yes",
        ]

        run_az_void_sync(*cmd)

    def edit_work_item(self, work_item_id: int, edit_title: bool) -> WorkItem:
        item = self.get_workitem(work_item_id)
        result = edit_work_item_in_editor(item, edit_title)
        self.update_workitem(result)
        return result

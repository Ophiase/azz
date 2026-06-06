from collections.abc import Sequence
from typing import Protocol, Self

from azz.core.iteration_path import IterationPath

from .work_item import WorkItem


class WorkItemFilter(Protocol):
    def __call__(self, task: WorkItem) -> bool: ...

    @classmethod
    def apply_filters(
        cls, tasks: Sequence[WorkItem], *filters: Self
    ) -> tuple[WorkItem, ...]:
        return tuple(
            task for task in tasks if all(task_filter(task) for task_filter in filters)
        )


class ProjectNameFilter(WorkItemFilter):
    def __init__(self, projects: str | tuple[str, ...]):
        if isinstance(projects, str):
            projects = (projects,)
        self.projects = projects

    def __call__(self, task: WorkItem) -> bool:
        def valid(project: str) -> bool:
            return task.name_project == project

        return any(valid(project) for project in self.projects)


class StateFilter(WorkItemFilter):
    def __init__(self, states: WorkItem | tuple[WorkItem, ...]):
        if isinstance(states, WorkItem):
            states = (states,)
        self.states = states

    def __call__(self, task: WorkItem) -> bool:
        return any(task.state == state for state in self.states)


class IterationPathFilter(WorkItemFilter):
    def __init__(self, iteration_path: IterationPath):
        self.iteration_path = iteration_path

    def __call__(self, task: WorkItem) -> bool:
        return task.iteration_path == self.iteration_path
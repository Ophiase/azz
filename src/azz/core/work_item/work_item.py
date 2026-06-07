from typing import Any, Self, override

from pydantic.dataclasses import dataclass

from azz.core.timebox import IterationPath

from .helper import Markdown, html_to_markdown
from .work_item_state import STATE_COLORS, WorkItemState
from .work_item_type import WorkItemType

type Username = str


@dataclass(frozen=True, slots=True)
class WorkItem:
    id: int
    name: str
    state: WorkItemState
    project: str
    description: Markdown | None = None
    assigned_to: Username | None = None
    iteration_path: IterationPath | None = None
    parent_id: int | None = None

    @property
    def name_project(self) -> str | None:
        """
        When the name is like:
        "[Project] Task Name"
        extract the project name "Project"
        """
        if self.name.startswith("[") and "]" in self.name:
            return self.name.split("]")[0][1:]

    @property
    def item_type(self) -> WorkItemType:
        return WorkItemType.DEFAULT

    def state_style(self) -> str:
        return STATE_COLORS.get(self.state, "white")

    def render_list(self) -> str:
        style = self.state_style()
        iteration_path_number = (
            self.iteration_path.optional_number if self.iteration_path else None
        )
        return (
            f"[{style}]{self.id} {iteration_path_number!s:<4} "
            f"{self.item_type:<10} {self.state:<10} "
            f"{self.name}[/{style}]"
        )

    def render_details(self) -> str:
        assigned = self.assigned_to or "unassigned"
        description = (
            html_to_markdown(self.description) if self.description else "No description"
        )

        state_color = self.state_style()

        iteration_path_str = (
            f"[green]Iteration[/green]: {self.iteration_path.optional_number} | "
            if self.iteration_path and self.iteration_path.optional_number is not None
            else ""
        )
        return (
            f"[bold]Task {self.id}: {self.name}[/bold]\n\n"
            f"[green]State[/green]: [{state_color}]{self.state}[/{state_color}] | "
            f"[green]Type[/green]: {self.item_type} | "
            f"[green]Assigned[/green]: {assigned}\n"
            f"[green]Name Project[/green]: {self.name_project} | "
            + iteration_path_str
            + f"[green]Parent[/green]: {self.parent_id} "
            "\n\n"
            f"[bold]Description[/bold]\n{description}"
        )

    @staticmethod
    def _common_fields(data: dict[str, Any]) -> dict[str, Any]:
        fields = data.get("fields", {})

        assigned = fields.get("System.AssignedTo")
        assigned_name = (
            assigned.get("displayName") if isinstance(assigned, dict) else None
        )

        return {
            "id": data.get("id", ""),
            "name": fields.get("System.Title", ""),
            "state": WorkItemState.from_str(fields.get("System.State", "Unknown")),
            "project": fields.get("System.TeamProject", ""),
            "description": fields.get("System.Description"),
            "assigned_to": assigned_name,
            "iteration_path": IterationPath(
                fields.get("System.IterationPath"), normalized=True
            ),
            "parent_id": fields.get("System.Parent"),
        }

    @classmethod
    def from_fields(cls, data: dict[str, Any]) -> Self:
        return cls(**cls._common_fields(data))


@dataclass(frozen=True, slots=True)
class Task(WorkItem):
    @override
    @property
    def item_type(self) -> WorkItemType:
        return WorkItemType.TASK

    pass


@dataclass(frozen=True, slots=True)
class UserStory(WorkItem):
    points: int | None = None
    acceptance_criteria: str | None = None

    @override
    @property
    def item_type(self) -> WorkItemType:
        return WorkItemType.USER_STORY

    @override
    @classmethod
    def from_fields(cls, data: dict[str, Any]) -> Self:
        base = super()._common_fields(data)
        fields = data.get("fields", {})
        return cls(
            **base,
            points=fields.get("Microsoft.VSTS.Scheduling.StoryPoints"),
            acceptance_criteria=fields.get("Custom.AcceptanceCriteria"),
        )


@dataclass(frozen=True, slots=True)
class Bug(WorkItem):
    severity: str | None = None

    @override
    @property
    def item_type(self) -> WorkItemType:
        return WorkItemType.BUG

    @override
    @classmethod
    def from_fields(cls, data: dict[str, Any]) -> Self:
        base = super()._common_fields(data)
        fields = data.get("fields", {})
        return cls(
            **base,
            severity=fields.get("Microsoft.VSTS.Common.Severity"),
        )


class Epic(WorkItem):
    @override
    @property
    def item_type(self) -> WorkItemType:
        return WorkItemType.EPIC

    @override
    @classmethod
    def from_fields(cls, data: dict[str, Any]) -> Self:
        base = super()._common_fields(data)
        return cls(**base)


class Issue(WorkItem):
    @override
    @property
    def item_type(self) -> WorkItemType:
        return WorkItemType.ISSUE

    @override
    @classmethod
    def from_fields(cls, data: dict[str, Any]) -> Self:
        base = super()._common_fields(data)
        return cls(**base)


class Feature(WorkItem):
    @override
    @property
    def item_type(self) -> WorkItemType:
        return WorkItemType.FEATURE

    @override
    @classmethod
    def from_fields(cls, data: dict[str, Any]) -> Self:
        base = super()._common_fields(data)
        return cls(**base)


def work_item_factory(data: dict[str, Any]) -> WorkItem:
    item_type = WorkItemType.type_from_fields(data)
    if item_type == WorkItemType.TASK:
        return Task.from_fields(data)
    elif item_type == WorkItemType.USER_STORY:
        return UserStory.from_fields(data)
    elif item_type == WorkItemType.BUG:
        return Bug.from_fields(data)
    elif item_type == WorkItemType.EPIC:
        return Epic.from_fields(data)
    elif item_type == WorkItemType.ISSUE:
        return Issue.from_fields(data)
    elif item_type == WorkItemType.FEATURE:
        return Feature.from_fields(data)
    else:
        return WorkItem.from_fields(data)

from __future__ import annotations

from dataclasses import replace
from typing import Annotated

import typer
from rich import print

from azz.core.editor import edit_in_editor
from azz.core.engine import Engine
from azz.core.work_item import WorkItemState
from azz.core.work_item.work_item_type import WorkItemType


def register(app: typer.Typer, engine: Engine) -> None:
    def list_work_items(
        include_closed: bool = typer.Option(False, "--all", "-a"),
        show_others: bool = typer.Option(False, "--others", "-A"),
        resolved_only: bool = typer.Option(False, "--resolved", "-r"),
        current_timebox_only: bool = typer.Option(
            False, "--current-timebox", "-c"
        ),
        sorted_by_update: bool = typer.Option(
            False, "--sorted-by-update", "-s"
        ),
        limit: int | None = typer.Option(None, "--limit", "-l"),
        show_date: bool = typer.Option(False, "--date", "-d"),
        show_project: bool = typer.Option(False, "--show-project", "-p"),
    ) -> None:
        states: frozenset[WorkItemState] | None = None
        if include_closed:
            states = frozenset({
                WorkItemState.ACTIVE,
                WorkItemState.NEW,
                WorkItemState.RESOLVED,
                WorkItemState.CLOSED,
            })
        if resolved_only:
            states = frozenset({WorkItemState.RESOLVED})

        tasks = engine.list_work_items(
            states=states,
            show_others=show_others,
            current_timebox_only=current_timebox_only,
        )

        if not tasks:
            print("[yellow]No tasks found[/yellow]")
            return

        if sorted_by_update:
            tasks = tuple(sorted(
                tasks,
                key=lambda task: (
                    task.changed_date.timestamp()
                    if task.changed_date
                    else 0.0
                ),
            ))

        if limit is not None:
            tasks = tasks[-limit:]

        for task in tasks:
            print(task.render_list(show_date=show_date, show_project=show_project))

    def show_work_item(work_item_id: int) -> None:
        work_item = engine.get_workitem(work_item_id)
        print(work_item.render_details())

    def create_work_item(
        name: str,
        state: str | None = typer.Option(None, "--state", "-s"),
        parent: int | None = typer.Option(None, "--parent", "-p"),
        item_type: str | None = typer.Option(
            None, "--type", "-t", help="Work item type (default: Task)"
        ),
        project: str | None = typer.Option(
            None, "--project", "-P", help="Project to create the work item in"
        ),
        description: str | None = typer.Option(None, "--description", "-d"),
        editor: bool = typer.Option(False, "--editor", "-e"),
    ) -> None:
        if editor:
            description = edit_in_editor(description or "")
        item_type_parsed = (
            WorkItemType.from_user_input(item_type)
            if item_type
            else WorkItemType.TASK
        )
        item = engine.create_work_item_helper(
            name,
            description=description,
            project=project,
            item_type=item_type_parsed,
        )
        if state:
            task_state = WorkItemState.from_user_input(state)
            engine.update_work_item_state(item.id, task_state)
            item = replace(item, state=task_state)
        if parent:
            engine.link_parent(item.id, parent)
            item = replace(item, parent_id=parent)
        print(item.render_list())

    def edit_work_item(
        work_item_id: int,
        edit_title: bool = typer.Option(False, "--title", "-t"),
    ) -> None:
        engine.edit_work_item(work_item_id, edit_title=edit_title)

    def delete_work_item(
        work_item_ids: Annotated[list[int], typer.Argument()],
    ) -> None:
        for work_item_id in work_item_ids:
            engine.delete_workitem_helper(work_item_id)

    def attach(
        parent_id: int,
        children_ids: Annotated[list[int], typer.Argument()],
    ) -> None:
        for child_id in children_ids:
            engine.link_parent(child_id, parent_id)

    for name in ["list", "l"]:
        app.command(name)(list_work_items)
    app.command("show")(show_work_item)
    for name in ["create", "c"]:
        app.command(name)(create_work_item)
    app.command("edit")(edit_work_item)
    app.command("delete")(delete_work_item)
    app.command("attach")(attach)

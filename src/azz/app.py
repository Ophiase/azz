from dataclasses import replace
from functools import partial
from typing import Annotated

import typer
from rich import print

from azz.core.editor import edit_in_editor
from azz.core.engine import Engine
from azz.core.engine_config import EngineConfig
from azz.core.work_item import WorkItemState
from azz.core.work_item.work_item_type import WorkItemType
from azz.logging import configure_logging


class AzzApp:
    _app: typer.Typer
    _engine: Engine

    def __init__(self):
        config = EngineConfig.from_env()
        self._engine = Engine(config)
        self._initialize_app()

    def _initialize_app(self):
        self._app = typer.Typer(invoke_without_command=True)

        @self._app.callback()
        def callback(
            verbose: bool = typer.Option(
                False, "--verbose", "-v", help="Enable verbose logging"
            ),
        ):
            configure_logging(verbose)

        self._initialize_commands()

    def _initialize_commands(self):
        command = self._app.command
        # stateless
        for n in ["list", "l"]:
            command(n)(self.list_work_items)
        command("show")(self.show_work_item)
        command("timebox")(self.show_timebox)
        command("set_timebox")(self.set_timebox)
        # stateful
        for n in ["create", "c"]:
            command(n)(self.create_work_item)
        command("edit")(self.edit_work_item)
        command("delete")(self.delete_work_item)
        command("attach")(self.attach)
        # work item state update
        command("state")(self.state)
        command("close")(partial(self.state, state="Closed"))
        command("resolve")(partial(self.state, state="Resolved"))
        # interactive
        command("interactive")(self.interactive)

    def list_work_items(
        self,
        include_closed: bool = typer.Option(False, "--all", "-a"),
        show_others: bool = typer.Option(False, "--others", "-A"),
        resolved_only: bool = typer.Option(False, "--resolved", "-r"),
        current_timebox_only: bool = typer.Option(False, "--current-timebox", "-c"),
    ):
        states = None
        if include_closed:
            states = frozenset({
                WorkItemState.ACTIVE,
                WorkItemState.NEW,
                WorkItemState.RESOLVED,
                WorkItemState.CLOSED,
            })
        if resolved_only:
            states = frozenset({WorkItemState.RESOLVED})

        tasks = self._engine.list_work_items(
            states=states,
            show_others=show_others,
            current_timebox_only=current_timebox_only,
        )

        if not tasks:
            print("[yellow]No tasks found[/yellow]")
            return

        for task in tasks:
            print(task.render_list())

    def show_work_item(self, work_item_id: int):
        work_item = self._engine.get_workitem(work_item_id)
        print(work_item.render_details())

    def attach(
        self, parent_id: int, children_ids: Annotated[list[int], typer.Argument()]
    ):
        for child_id in children_ids:
            self._engine.link_parent(child_id, parent_id)

    def edit_work_item(
        self, work_item_id: int, edit_title: bool = typer.Option(False, "--title", "-t")
    ):
        self._engine.edit_work_item(work_item_id, edit_title=edit_title)

    def create_work_item(
        self,
        name: str,
        state: str | None = typer.Option(None, "--state", "-s"),
        parent: int | None = typer.Option(None, "--parent", "-p"),
        *,
        item_type: str | None = typer.Option(
            None,
            "--type",
            "-t",
            help="The type of the work item (e.g., default: Task)",
        ),
        project: str | None = typer.Option(
            None, "--project", "-P", help="The project to create the work item in"
        ),
        description: str | None = typer.Option(None, "--description", "-d"),
        editor: bool = typer.Option(False, "--editor", "-e"),
    ):
        """
        Remark: the name of the work item will be:
        "[<project>] <name>"
        """

        if editor:
            description = edit_in_editor(description or "")
        item_type_parsed = WorkItemType.TASK
        if item_type:
            item_type_parsed = WorkItemType.from_user_input(item_type)

        item = self._engine.create_work_item_helper(
            name,
            description=description,
            project=project,
            item_type=item_type_parsed,
        )
        if state:
            task_state = WorkItemState.from_user_input(state)
            self._engine.update_work_item_state(item.id, task_state)
            item = replace(item, state=task_state)
        if parent:
            self._engine.link_parent(item.id, parent)
            item = replace(item, parent_id=parent)

        if item:
            print(item.render_list())
        else:
            print("[red]Failed to create work item[/red]")

    def state(
        self,
        state: str,
        task_ids: Annotated[list[int], typer.Argument()],
    ):
        """
        Update the state of a work item (New, Active, Closed, Resolved)
        """

        task_state = WorkItemState.from_user_input(state)
        for task_id in task_ids:
            self._engine.update_work_item_state(task_id, task_state)

    def delete_work_item(
        self,
        work_item_ids: Annotated[list[int], typer.Argument()],
    ):
        for work_item_id in work_item_ids:
            self._engine.delete_workitem_helper(work_item_id)

    def show_timebox(self):
        timebox = self._engine.get_current_timebox()
        print(timebox.render_all())

    def set_timebox(
        self,
        work_item_ids: Annotated[list[int], typer.Argument()],
        timebox: int | None = typer.Option(None, "--timebox", "-t"),
    ):
        if timebox is not None:
            print("timebox parameter is currently ignored.")
        timebox_engine = self._engine.get_current_timebox()

        for work_item_id in work_item_ids:
            self._engine.set_timebox(work_item_id, timebox_engine)
    
    def create_pull_request(
        self,
        source_branch: str,
        target_branch: str,
        title: str | None = typer.Option(None, "--title", "-t"),
        description: str | None = typer.Option(None, "--description", "-d"),
        no_confirm: bool = typer.Option(False, "--no-confirm", "-n"),
    ):
        raise NotImplementedError("Pull request creation is not implemented yet")

    def list_pull_requests(self):
        raise NotImplementedError("Pull request listing is not implemented yet")
    
    def show_pull_request(self, pr_id: int):
        raise NotImplementedError("Pull request details are not implemented yet")

    def interactive(self):
        raise NotImplementedError("Interactive mode is not implemented yet")

    def run(self):
        self._app()


def main():
    AzzApp().run()

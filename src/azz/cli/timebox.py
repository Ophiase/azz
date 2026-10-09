from __future__ import annotations

from typing import Annotated

import typer
from rich import print

from azz.backend import WorkItemBackend


def register(app: typer.Typer, engine: WorkItemBackend) -> None:
    def show_timebox() -> None:
        """Show the current timebox."""
        timebox = engine.get_current_timebox()
        print(timebox.render_all())

    def list_timeboxes() -> None:
        """List every timebox, past and future."""
        for timebox in engine.list_timeboxes():
            print(timebox.render_all())

    def set_timebox(
        work_item_ids: Annotated[list[int], typer.Argument()],
        timebox: int | None = typer.Option(None, "--timebox", "-t"),
    ) -> None:
        """Move work items into the current timebox."""
        if timebox is not None:
            print("timebox parameter is currently ignored.")
        current_timebox = engine.get_current_timebox()
        for work_item_id in work_item_ids:
            engine.set_timebox(work_item_id, current_timebox)

    app.command("timebox")(show_timebox)
    app.command("list_timebox")(list_timeboxes)
    app.command("set_timebox")(set_timebox)

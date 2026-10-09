from __future__ import annotations

import typer
from rich import print

from azz.backend import WorkItemBackend
from azz.core.branch import branch_name
from azz.core.clipboard import copy_to_clipboard


def register(app: typer.Typer, engine: WorkItemBackend) -> None:
    def branch(work_item_id: int) -> None:
        """Print a git branch name for a work item, and copy it."""
        work_item = engine.get_workitem(work_item_id)
        name = branch_name(work_item)
        print(name)
        if copy_to_clipboard(name):
            print("[dim]Copied to clipboard[/dim]")

    app.command("branch")(branch)

from __future__ import annotations

from typing import Annotated

import typer

from azz.backend import WorkItemBackend
from azz.core.work_item import WorkItemState


def register(app: typer.Typer, engine: WorkItemBackend) -> None:
    def update_state(
        state: str,
        task_ids: Annotated[list[int], typer.Argument()],
    ) -> None:
        """Set the state of one or more work items."""
        task_state = WorkItemState.from_user_input(state)
        for task_id in task_ids:
            engine.update_work_item_state(task_id, task_state)

    def close(task_ids: Annotated[list[int], typer.Argument()]) -> None:
        """Set work items to Closed."""
        update_state("Closed", task_ids)

    def resolve(task_ids: Annotated[list[int], typer.Argument()]) -> None:
        """Set work items to Resolved."""
        update_state("Resolved", task_ids)

    app.command("state")(update_state)
    app.command("close")(close)
    app.command("resolve")(resolve)

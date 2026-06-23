from __future__ import annotations

from typing import Annotated

import typer

from azz.core.engine import Engine
from azz.core.work_item import WorkItemState


def register(app: typer.Typer, engine: Engine) -> None:
    def update_state(
        state: str,
        task_ids: Annotated[list[int], typer.Argument()],
    ) -> None:
        task_state = WorkItemState.from_user_input(state)
        for task_id in task_ids:
            engine.update_work_item_state(task_id, task_state)

    def close(task_ids: Annotated[list[int], typer.Argument()]) -> None:
        update_state("Closed", task_ids)

    def resolve(task_ids: Annotated[list[int], typer.Argument()]) -> None:
        update_state("Resolved", task_ids)

    app.command("state")(update_state)
    app.command("close")(close)
    app.command("resolve")(resolve)

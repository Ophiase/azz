from __future__ import annotations

from typing import TYPE_CHECKING

import typer

if TYPE_CHECKING:
    from azz.backend import WorkItemBackend


def register(
    app: typer.Typer,
    backend: WorkItemBackend,
    notice: str | None = None,
) -> None:
    def interactive() -> None:
        from azz.tui.app import AzzTUI

        tui = AzzTUI(backend)
        if notice:
            tui.sub_title = notice
        tui.run()

    for name in ["interactive", "i"]:
        app.command(name)(interactive)

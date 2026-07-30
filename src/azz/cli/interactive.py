from __future__ import annotations

from typing import TYPE_CHECKING, cast

import typer

if TYPE_CHECKING:
    from azz.backend import WorkItemBackend
    from azz.core.engine import Engine


def register(
    app: typer.Typer,
    backend: WorkItemBackend,
    notice: str | None = None,
) -> None:
    def interactive() -> None:
        from azz.tui.app import AzzTUI

        # AzzTUI still annotates `Engine`; it only calls the backend protocol.
        tui = AzzTUI(cast("Engine", backend))
        if notice:
            tui.sub_title = notice
        tui.run()

    for name in ["interactive", "i"]:
        app.command(name)(interactive)

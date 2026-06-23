from __future__ import annotations

import typer

from azz.core.engine import Engine


def register(app: typer.Typer, engine: Engine) -> None:
    def interactive() -> None:
        from azz.tui.app import AzzTUI

        AzzTUI(engine).run()

    for name in ["interactive", "i"]:
        app.command(name)(interactive)

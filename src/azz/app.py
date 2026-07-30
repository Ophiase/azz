from __future__ import annotations

import typer

from azz.core.engine import Engine
from azz.core.engine_config import EngineConfig
from azz.logging import configure_logging


class AzzApp:
    def __init__(self) -> None:
        config = EngineConfig.from_env()
        self._engine = Engine(config)
        self._app = typer.Typer(invoke_without_command=True)
        self._register_callback()
        self._register_commands()

    def _register_callback(self) -> None:
        @self._app.callback()
        def callback(
            verbose: bool = typer.Option(
                False, "--verbose", "-v", help="Enable verbose logging"
            ),
        ) -> None:
            configure_logging(verbose)

    def _register_commands(self) -> None:
        from azz.cli import branch, interactive, plan, state, timebox, work_items

        for module in [work_items, timebox, state, branch, interactive, plan]:
            module.register(self._app, self._engine)

    def run(self) -> None:
        self._app()


def main() -> None:
    AzzApp().run()

from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING, cast

import typer

from azz.backend import WorkItemBackend
from azz.core.engine import Engine
from azz.core.engine_config import EngineConfig
from azz.demo import DEMO_FLAG, DemoSession, demo_requested
from azz.logging import configure_logging

if TYPE_CHECKING:
    from collections.abc import Sequence

logger = getLogger(__name__)


class AzzApp:
    """
    Wires one backend into every command.

    Demo mode is decided here, once, before the commands are registered:
    `EngineConfig.from_env()` must not run when `--demo` or `AZZ_DEMO` is set,
    so that someone without an Azure DevOps account at all can still record
    the TUI.
    """

    def __init__(self, argv: Sequence[str] | None = None) -> None:
        self._demo = DemoSession.start() if demo_requested(argv) else None
        self._backend: WorkItemBackend = (
            self._demo.backend if self._demo else Engine(EngineConfig.from_env())
        )
        self._app = typer.Typer(invoke_without_command=True)
        self._register_callback()
        self._register_commands()

    def _register_callback(self) -> None:
        @self._app.callback()
        def callback(
            verbose: bool = typer.Option(
                False, "--verbose", "-v", help="Enable verbose logging"
            ),
            demo: bool = typer.Option(
                False,
                DEMO_FLAG,
                help="Work on a bundled fictional board instead of Azure DevOps",
            ),
        ) -> None:
            configure_logging(verbose)
            logger.debug("demo mode: %s", demo)

    def _register_commands(self) -> None:
        from azz.cli import (
            branch,
            claude,
            interactive,
            plan,
            state,
            timebox,
            work_items,
        )

        # Those modules still annotate `Engine`, yet each one only ever calls
        # the `WorkItemBackend` surface, so a cache-backed run is safe.
        engine = cast(Engine, self._backend)
        for module in [
            work_items,
            timebox,
            state,
            branch,
            plan,
            claude,
        ]:
            module.register(self._app, engine)
        interactive.register(self._app, self._backend, notice=self._notice)

    @property
    def _notice(self) -> str | None:
        return self._demo.notice if self._demo else None

    def run(self) -> None:
        self._app()


def main() -> None:
    AzzApp().run()

import os
import sys
from collections.abc import Sequence
from itertools import takewhile
from typing import Final

DEMO_VARIABLE: Final = "AZZ_DEMO"
DEMO_FLAG: Final = "--demo"
TRUTHY: Final = frozenset({"1", "true", "yes", "on"})


def demo_requested(argv: Sequence[str] | None = None) -> bool:
    """
    Whether this process should run against the bundled fictional board.

    Read straight from `argv` (`sys.argv` convention: program name first)
    rather than from the parsed Typer callback, because the backend has to
    exist before any command is registered, which happens long before Typer
    parses anything.
    """
    arguments = sys.argv if argv is None else argv
    return _variable_enabled() or DEMO_FLAG in _global_options(arguments[1:])


def _global_options(arguments: Sequence[str]) -> tuple[str, ...]:
    """
    The options Typer parses before the subcommand name.

    Stopping at the subcommand keeps `azz create "support --demo"` from
    quietly switching a real board for the fake one.
    """
    return tuple(takewhile(lambda argument: argument.startswith("-"), arguments))


def _variable_enabled() -> bool:
    return os.getenv(DEMO_VARIABLE, "").strip().lower() in TRUTHY

from __future__ import annotations

from typing import ClassVar

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Label, Static

from azz.plan.tracking import TrackingStatus

_GLYPH_WIDTH = 3
_NAME_WIDTH = 14


class PlanLegendScreen(ModalScreen[None]):
    """
    What the leading plan gutter means.

    The wording is read from `TrackingStatus.description` so the legend can
    never drift from the statuses the plan engine actually reports.
    """

    CSS = """
    PlanLegendScreen { align: center middle; }
    #dialog {
        width: 56;
        height: auto;
        border: solid $primary;
        background: $surface;
        padding: 1 2;
    }
    """

    BINDINGS: ClassVar = [
        Binding("escape", "dismiss", "Close"),
        Binding("q", "dismiss", "Close"),
        Binding("enter", "dismiss", "Close"),
    ]

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label("[bold]Plan state[/bold]")
            yield Static(_legend_text(), id="legend")
            yield Label("[dim]P: refresh plan state · Esc: close[/dim]")


def _legend_text() -> Text:
    text = Text()
    for status in TrackingStatus:
        text.append(status.glyph.center(_GLYPH_WIDTH), style=f"bold {status.style}")
        text.append(status.value.ljust(_NAME_WIDTH), style="bold")
        text.append(status.description, style="dim")
        text.append("\n")
    return text

from __future__ import annotations

from typing import ClassVar

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Label


class RenameScreen(ModalScreen[str | None]):
    CSS = """
    RenameScreen { align: center middle; }
    #dialog {
        width: 70;
        height: auto;
        border: solid $primary;
        background: $surface;
        padding: 1 2;
    }
    """

    BINDINGS: ClassVar = [Binding("escape", "dismiss_none", "Cancel")]

    def __init__(self, current_name: str) -> None:
        super().__init__()
        self._current_name = current_name

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label("[bold]Rename[/bold]")
            yield Input(value=self._current_name, id="rename-input")

    def on_mount(self) -> None:
        self.query_one(Input).focus()

    @on(Input.Submitted)
    def on_submitted(self, event: Input.Submitted) -> None:
        stripped = event.value.strip()
        self.dismiss(stripped if stripped else None)

    def action_dismiss_none(self) -> None:
        self.dismiss(None)

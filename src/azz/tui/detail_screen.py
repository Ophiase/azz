from __future__ import annotations

from typing import ClassVar

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer
from textual.screen import ModalScreen
from textual.widgets import Static

from azz.core.work_item.work_item import WorkItem


class DetailScreen(ModalScreen[None]):
    CSS = """
    DetailScreen { align: center middle; }
    #dialog {
        width: 90;
        height: auto;
        max-height: 80%;
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

    def __init__(self, work_item: WorkItem) -> None:
        super().__init__()
        self._work_item = work_item

    def compose(self) -> ComposeResult:
        with ScrollableContainer(id="dialog"):
            yield Static(self._work_item.render_details())

from typing import ClassVar, Final

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.events import Key
from textual.screen import ModalScreen
from textual.widgets import Label, ListItem, ListView

from azz.core.work_item import WorkItemState

_SHORTCUT: Final[dict[str, WorkItemState]] = {
    "n": WorkItemState.NEW,
    "a": WorkItemState.ACTIVE,
    "d": WorkItemState.DESIGN,
    "r": WorkItemState.RESOLVED,
    "c": WorkItemState.CLOSED,
}

_DISPLAY: Final[tuple[tuple[str, WorkItemState], ...]] = (
    ("n", WorkItemState.NEW),
    ("a", WorkItemState.ACTIVE),
    ("d", WorkItemState.DESIGN),
    ("r", WorkItemState.RESOLVED),
    ("c", WorkItemState.CLOSED),
)


class StatePickerScreen(ModalScreen[WorkItemState | None]):
    CSS = """
    StatePickerScreen { align: center middle; }
    #dialog {
        width: 30;
        height: auto;
        border: solid $primary;
        background: $surface;
        padding: 1;
    }
    """

    BINDINGS: ClassVar = [
        Binding("escape", "dismiss_none", "Cancel"),
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
    ]

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label("[bold]Select State[/bold]")
            yield ListView(
                *[
                    ListItem(
                        Label(f"[dim]{key}[/dim]  {state.value}"),
                        id=f"s-{state.value}",
                    )
                    for key, state in _DISPLAY
                ]
            )

    def action_cursor_down(self) -> None:
        self.query_one(ListView).action_cursor_down()

    def action_cursor_up(self) -> None:
        self.query_one(ListView).action_cursor_up()

    def on_key(self, event: Key) -> None:
        state = _SHORTCUT.get(event.key)
        if state is not None:
            event.prevent_default()
            self.dismiss(state)

    @on(ListView.Selected)
    def on_selected(self, event: ListView.Selected) -> None:
        raw_id = event.item.id or ""
        self.dismiss(WorkItemState.from_str(raw_id.removeprefix("s-")))

    def action_dismiss_none(self) -> None:
        self.dismiss(None)

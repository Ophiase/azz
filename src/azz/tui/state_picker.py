from typing import ClassVar, Final

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Label, ListItem, ListView

from azz.core.work_item import WorkItemState

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

    # Declare all letter shortcuts as BINDINGS so they shadow the app's bindings
    # while this modal is active — on_key would still bubble to the app.
    BINDINGS: ClassVar = [
        Binding("escape", "dismiss_none", "Cancel"),
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("n", "pick_new", "", show=False),
        Binding("a", "pick_active", "", show=False),
        Binding("d", "pick_design", "", show=False),
        Binding("r", "pick_resolved", "", show=False),
        Binding("c", "pick_closed", "", show=False),
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

    def action_pick_new(self) -> None:
        self.dismiss(WorkItemState.NEW)

    def action_pick_active(self) -> None:
        self.dismiss(WorkItemState.ACTIVE)

    def action_pick_design(self) -> None:
        self.dismiss(WorkItemState.DESIGN)

    def action_pick_resolved(self) -> None:
        self.dismiss(WorkItemState.RESOLVED)

    def action_pick_closed(self) -> None:
        self.dismiss(WorkItemState.CLOSED)

    @on(ListView.Selected)
    def on_selected(self, event: ListView.Selected) -> None:
        raw_id = event.item.id or ""
        self.dismiss(WorkItemState.from_str(raw_id.removeprefix("s-")))

    def action_dismiss_none(self) -> None:
        self.dismiss(None)
